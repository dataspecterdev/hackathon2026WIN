"""DORA chat service: serves the review-assistant web page and answers chat
turns about DelDOT contract packages.

Three interchangeable backends, selected by DORA_BACKEND (default "rules"):

  DORA_BACKEND=rules (default)
    No LLM, no network call, no credential at all. Extracts a package_id and
    optional CC-NN requirement id(s) from the user's message with a regex,
    then runs the same deterministic pipeline the rest of this repo scores
    against — crf.pipeline.analyse_package(): applicability gate ->
    precedence resolution -> invariant detector -> emit, with no LLM
    adjudicator (see README.md's "why not RAG" argument for why a rule
    that's already stated in the checklist should never be re-derived
    probabilistically). Every row's `rule_id`/`decided_by` goes into the
    trace the UI already renders as an audit trail. This is the same code
    path `run.py` and `deploy/handler.py` (the Lambda /analyze route) use.

  DORA_BACKEND=ces
    Proxies to a hosted Gemini Enterprise (CES) deployment where DORA's
    persona and its six tools are configured on Google's side. This process
    only forwards user text to `sessions:runSession` and returns the agent's
    text — no tool loop runs locally. Auth is an OAuth access token minted
    from Application Default Credentials (equivalent to
    `gcloud auth print-access-token`, but usable from a server process).
    Configure via CES_PROJECT / CES_LOCATION / CES_APP / CES_DEPLOYMENT /
    CES_APP_VERSION / CES_API_VERSION (defaults match the deployment this was
    built against).

  DORA_BACKEND=gemini
    Runs a tool-use loop locally against the raw Gemini API, re-deriving the
    checklist rules through the model rather than the compiled detectors in
    crf/. Six tools, matching the {@TOOL: ...} references in the prompt:

        lookup_reference_requirement   Tier 1 - checklist row (Challenge_Reference_Rule)
        get_project_metadata           Applicability gate - Project_Metadata.json booleans
        search_contract_package        Clause retrieval - base + addendum clauses for a heading
        resolve_governing_document     Precedence - the one clause that governs
        verify_evidence_verbatim       Evidence check - is this span really in that document
        specifications                 Tier 3 - best-effort live fetch of the external authority text

    The first five are deterministic lookups over the local challenge dataset
    (same data tool_server.py wraps). `specifications` is the one tool that
    reaches the open internet; it degrades to "nothing found" rather than
    fabricating text. Auth is a Gemini API key from GOOGLE_API_KEY.

No credential is ever sent to, or embedded in, the browser, on any backend.

Run locally (rules backend, no setup needed):
    pip install -r deploy/requirements-dora-chat.txt
    python3 deploy/dora_chat.py                  # http://localhost:8081

Run locally (CES backend):
    export DORA_BACKEND=ces
    gcloud auth application-default login     # once, interactively
    python3 deploy/dora_chat.py

Run locally (Gemini fallback):
    export DORA_BACKEND=gemini
    export GOOGLE_API_KEY=AQ...                # from Google AI Studio / Cloud Console
    python3 deploy/dora_chat.py

Deploy (Cloud Run):
    gcloud run deploy dora-chat --source . \
        --region us-central1 \
        --set-env-vars DORA_BACKEND=rules \
        --allow-unauthenticated
"""

from __future__ import annotations

import csv
import html
import io
import json
import logging
import os
import re
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import requests
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    # Lets this module run as `python3 deploy/dora_chat.py` from any cwd,
    # not just when the repo root happens to already be on sys.path.
    sys.path.insert(0, str(_REPO_ROOT))

from crf import precedence
from crf.evaluate import evaluate as evaluate_against_labels
from crf.evaluate import load_labels
from crf.extract import discover_packages, load_package
from crf.models import Clause, Finding, Package
from crf.pipeline import analyse_package
from crf.reference import ReferenceChecklist

LOG = logging.getLogger("dora_chat")
logging.basicConfig(level=logging.INFO)

ROOT = _REPO_ROOT
DATA_ROOT = Path(os.environ.get("CRF_DATA_ROOT", ROOT / "Contract_Clause_Risk_Flagging")).resolve()
CHECKLIST_PATH = DATA_ROOT / "References" / "Reference_Checklist.csv"
SYSTEM_PROMPT_PATH = Path(
    os.environ.get("DORA_SYSTEM_PROMPT", ROOT / "prompts" / "dora_agent_prompt_v2.xml")
)
# Which frontend to serve. Lets two instances run side by side with different
# branding (e.g. website/ for the rules backend, website-gemini/ for CES).
STATIC_DIR = Path(os.environ.get("DORA_STATIC_DIR", "website"))
if not STATIC_DIR.is_absolute():
    STATIC_DIR = ROOT / STATIC_DIR
SPLITS = ("Development", "Validation")
MODEL_ID = os.environ.get("DORA_MODEL_ID", "gemini-3.7-flash")
# The Gemini free tier caps requests per model per day. When the active model
# returns 429 RESOURCE_EXHAUSTED, the chat loop falls through this chain — each
# model has its own daily quota bucket, so switching buys a fresh allowance.
MODEL_FALLBACKS = [
    m.strip()
    for m in os.environ.get(
        "DORA_MODEL_FALLBACKS", "gemini-3.5-flash,gemini-3.1-flash-lite,gemini-3.5-flash-lite"
    ).split(",")
    if m.strip()
]
MAX_TOOL_ITERATIONS = 12
MAX_SESSIONS = 200  # simple bound so an in-memory demo server can't grow unbounded

# DORA_BACKEND selects who answers a chat turn:
#   "rules"  (default) - crf.pipeline.analyse_package(), the deterministic
#            detector pipeline the rest of this repo is scored against. No
#            LLM, no network call, no credential.
#   "ces"    - proxy to a hosted Gemini Enterprise (CES) deployment, where the
#            DORA persona and the six tools are configured on Google's side.
#            This process just forwards text and returns text.
#   "gemini" - run the tool-use loop locally against the raw Gemini API, using
#            the TOOLS/_TOOL_IMPL defined above. Kept as a fallback in case
#            the hosted deployment is unreachable or misconfigured.
DORA_BACKEND = os.environ.get("DORA_BACKEND", "rules").strip().lower()

CES_API_VERSION = os.environ.get("CES_API_VERSION", "v1beta")
CES_PROJECT = os.environ.get("CES_PROJECT", "hackathon-2026-transport-2")
CES_LOCATION = os.environ.get("CES_LOCATION", "us")
CES_APP = os.environ.get("CES_APP", "a9c38b91-99b9-429d-a249-0154dba7969a")
CES_DEPLOYMENT = os.environ.get("CES_DEPLOYMENT", "04efd120-46bb-401f-a9d9-5842a211e4e4")
# Optional: the console's "test this deployment" snippet includes a pinned app
# version. Leave unset to let the deployment resolve its own current version.
CES_APP_VERSION = os.environ.get("CES_APP_VERSION", "4c6b5387-fae7-42ec-a17c-2da3dcd88d8f")

# User-uploaded packages: never mixed into the sample dataset directory, and
# excluded from git (see .gitignore) since they may be private documents.
UPLOAD_ROOT = Path(os.environ.get("DORA_UPLOAD_ROOT", ROOT / "uploads")).resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
_PACKAGE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
ALLOWED_UPLOAD_NAMES = {"Project_Metadata.json", "Document_Index.csv"}
MAX_UPLOAD_FILES = 40
MAX_UPLOAD_FILE_BYTES = 25 * 1024 * 1024  # 25 MB/file — generous for a contract PDF

SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Dataset cache (same shape as deploy/tool_server.py, kept independent so the
# two tool servers can be deployed separately)
# --------------------------------------------------------------------------- #

_checklist: Optional[ReferenceChecklist] = None
_packages: dict[str, Package] = {}
_loaded_roots: set[str] = set()


def checklist() -> ReferenceChecklist:
    global _checklist
    if _checklist is None:
        _checklist = ReferenceChecklist.load(CHECKLIST_PATH)
    return _checklist


def _load_all() -> None:
    if not _packages:
        for split_root in [DATA_ROOT / split for split in SPLITS] + [UPLOAD_ROOT]:
            if not split_root.exists():
                continue
            for pkg_root in discover_packages(split_root):
                pkg = load_package(pkg_root, checklist())
                _packages[pkg.package_id.upper()] = pkg
                _loaded_roots.add(str(pkg_root.resolve()))
    # uploads/ is shared on disk between instances (8081 rules, 8082 gemini),
    # so pick up any package another instance uploaded since we started.
    for pkg_root in discover_packages(UPLOAD_ROOT):
        key = str(pkg_root.resolve())
        if key in _loaded_roots:
            continue
        try:
            pkg = load_package(pkg_root, checklist())
        except Exception:
            LOG.warning("skipping unparseable uploaded package at %s", pkg_root)
            continue
        _packages[pkg.package_id.upper()] = pkg
        _loaded_roots.add(key)


def get_package(package_id: str) -> Package:
    _load_all()
    pkg = _packages.get(package_id.strip().upper())
    if pkg is None:
        raise KeyError(
            f"Unknown package_id {package_id!r}. Known: {', '.join(sorted(_packages))}"
        )
    return pkg


def clause_payload(c: Clause) -> dict:
    return {
        "file_name": c.file_name,
        "doc_type": c.doc_type,
        "heading": c.heading,
        "page": c.page,
        "location": c.location,
        "text": c.text,
        "is_replacement": c.is_replacement,
    }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #

def tool_lookup_reference_requirement(requirement_id: str) -> dict:
    req_id = (requirement_id or "").strip().upper()
    try:
        r = checklist().get(req_id)
    except KeyError:
        return {"error": f"Unknown requirement_id {requirement_id!r}. Known: {', '.join(checklist().ids)}"}
    return {
        "requirement_id": r.requirement_id,
        "tier": r.tier,
        "requirement_name": r.requirement_name,
        "reference_source": r.reference_source,
        "section": r.section,
        "applicability_rule": r.applicability_rule,
        "review_expectation": r.review_expectation,
        "severity_guidance": r.severity_guidance,
        "evidence_required": r.evidence_required,
        "challenge_reference_rule": r.challenge_reference_rule,
        "reference_location": r.reference_location,
    }


def tool_get_project_metadata(package_id: str) -> dict:
    try:
        pkg = get_package(package_id)
    except KeyError as exc:
        return {"error": str(exc)}
    return {
        "package_id": pkg.package_id,
        "project_title": pkg.project_title,
        "federal_aid": pkg.federal_aid,
        "buy_america_baba_applicable": pkg.baba_applicable,
        "subcontracting_planned": pkg.subcontracting_planned,
        "claim_event": pkg.claim_event,
        "delay_event": pkg.delay_event,
        "changed_work_event": pkg.changed_work_event,
        "issued_addenda": pkg.issued_addenda,
        "assumed_contract_value": pkg.contract_value,
        "document_files": pkg.doc_files,
    }


def tool_search_contract_package(package_id: str, requirement_name: str) -> dict:
    try:
        pkg = get_package(package_id)
    except KeyError as exc:
        return {"error": str(exc)}

    req_id = checklist().resolve_heading(requirement_name)
    if req_id is None:
        return {
            "package_id": pkg.package_id,
            "requirement_name": requirement_name,
            "resolved_requirement_id": None,
            "clause_count": 0,
            "clauses": [],
            "message": (
                "No requirement matched this heading. Use the exact Requirement_Name "
                "string from lookup_reference_requirement, not a paraphrase."
            ),
        }

    clauses = precedence.candidates(pkg, req_id, checklist())
    return {
        "package_id": pkg.package_id,
        "requirement_name": requirement_name,
        "resolved_requirement_id": req_id,
        "clause_count": len(clauses),
        "clauses": [clause_payload(c) for c in clauses],
        "message": (
            "Includes base documents and any Addenda ('Revision to <name>'). "
            "Resolve precedence with resolve_governing_document before judging any one clause."
        ),
    }


def _precedence_basis(governing: Optional[Clause], superseded: list[Clause]) -> str:
    if governing is None:
        return "not_located"
    if precedence.is_addendum(governing) and governing.is_replacement:
        return "addendum_replacement"
    return "deldot_105_6" if superseded else "single_occurrence"


def tool_resolve_governing_document(package_id: str, requirement_id: str) -> dict:
    try:
        pkg = get_package(package_id)
    except KeyError as exc:
        return {"error": str(exc)}

    req_id = (requirement_id or "").strip().upper()
    if req_id not in set(checklist().ids):
        return {"error": f"Unknown requirement_id {requirement_id!r}"}

    governing, superseded, note = precedence.resolve(pkg, req_id, checklist())
    return {
        "package_id": pkg.package_id,
        "requirement_id": req_id,
        "found": governing is not None,
        "governing": clause_payload(governing) if governing else None,
        "governing_document": (
            f"{governing.doc_type} ({governing.file_name})" if governing else "Not located in package"
        ),
        "superseded": [clause_payload(c) for c in superseded],
        "resolution_basis": _precedence_basis(governing, superseded),
        "resolution_note": note,
    }


def tool_verify_evidence_verbatim(package_id: str, file_name: str, span: str) -> dict:
    try:
        pkg = get_package(package_id)
    except KeyError as exc:
        return {"error": str(exc)}

    wanted_file = (file_name or "").strip().lower()
    in_file = [c for c in pkg.clauses if c.file_name.lower() == wanted_file]
    if not in_file:
        return {"error": f"{file_name!r} is not a document of {pkg.package_id}. Documents: {', '.join(pkg.doc_files)}"}

    needle = _norm(span)
    if not needle:
        return {
            "verbatim": False,
            "package_id": pkg.package_id,
            "file_name": file_name,
            "matched_heading": None,
            "matched_page": None,
            "message": "Empty span. An empty draft_evidence is only correct for a DOES_NOT_APPLY row.",
        }

    for c in in_file:
        if needle in _norm(c.text):
            return {
                "verbatim": True,
                "package_id": pkg.package_id,
                "file_name": c.file_name,
                "matched_heading": c.heading,
                "matched_page": c.page,
                "message": f"Verbatim span of {c.location}.",
            }

    return {
        "verbatim": False,
        "package_id": pkg.package_id,
        "file_name": file_name,
        "matched_heading": None,
        "matched_page": None,
        "message": (
            "This span does not occur in the cited document. It is not evidence. "
            "Retrieve the governing clause again and quote text that exists, or lower "
            "confidence and escalate the row for human review."
        ),
    }


# Reference_Source keyword -> external authority page, per the knowledge_source_rules
# in the DORA prompt. Best-effort: these are large government pages, so the fetch is
# whole-page text, not a section-precise API. Section-precision is left to Tier 1.
_SPEC_SOURCES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"fhwa-?\s*1273|federal-aid", re.I), "https://www.fhwa.dot.gov/construction/cqit/form1273.cfm"),
    (re.compile(r"contractor registration", re.I), "https://delcode.delaware.gov/title19/c036/index.html"),
    (re.compile(r"public works licens|business.*licens|subcontractor.*licens", re.I), "https://delcode.delaware.gov/title29/c069/index.html"),
    (re.compile(r"deldot", re.I), "https://engineeringsupport.deldot.gov/index.php/Standard_Specifications"),
]
_HTML_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
_HTML_TAG = re.compile(r"<[^>]+>")


def _pick_spec_url(reference_source: str, section: str) -> Optional[str]:
    haystack = f"{reference_source} {section}"
    for pattern, url in _SPEC_SOURCES:
        if pattern.search(haystack):
            return url
    return None


def tool_specifications(reference_source: str, section: str) -> dict:
    url = _pick_spec_url(reference_source, section)
    if url is None:
        return {
            "section": section,
            "reference_source": reference_source,
            "url": None,
            "found": False,
            "excerpt": "",
            "message": "No mapped external source for this Reference_Source. Tier 3 is silent; rely on Tier 1.",
        }
    try:
        resp = requests.get(url, timeout=6, headers={"User-Agent": "DORA-contract-reviewer/1.0"})
        resp.raise_for_status()
    except Exception as exc:  # network unavailable, blocked, 4xx/5xx, timeout, ...
        return {
            "section": section,
            "reference_source": reference_source,
            "url": url,
            "found": False,
            "excerpt": "",
            "message": f"Live fetch failed ({exc.__class__.__name__}). Tier 3 returned nothing from this server; rely on Tier 1.",
        }

    stripped = _HTML_SCRIPT_STYLE.sub(" ", resp.text)
    text = re.sub(r"\s+", " ", html.unescape(_HTML_TAG.sub(" ", stripped))).strip()
    needle = re.sub(r"[^0-9A-Za-z.§ ]", "", section).strip()
    idx = text.find(needle) if needle else -1
    if idx >= 0:
        excerpt = text[max(0, idx - 300): idx + 1200]
    else:
        excerpt = text[:1500]

    return {
        "section": section,
        "reference_source": reference_source,
        "url": url,
        "found": True,
        "excerpt": excerpt,
        "message": (
            "Live page fetched. Whole-page text, not guaranteed section-precise. "
            "Interpretive support only — never a source for a number, deadline, or rate that Tier 1 already states."
        ),
    }


TOOLS: list[dict] = [
    {
        "name": "lookup_reference_requirement",
        "description": (
            "Tier 1. Return the full Reference_Checklist.csv row for one requirement ID: "
            "Requirement_Name, Reference_Source, Section, Applicability_Rule, Review_Expectation, "
            "Severity_Guidance, Evidence_Required, and the authoritative Challenge_Reference_Rule "
            "text. Call this first, before anything else, for every requirement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"requirement_id": {"type": "string", "description": "e.g. CC-04"}},
            "required": ["requirement_id"],
        },
    },
    {
        "name": "get_project_metadata",
        "description": (
            "Return the exact Project_Metadata.json booleans for a package (federal_aid, "
            "buy_america_baba_applicable, subcontracting_planned, claim_event, delay_event, "
            "changed_work_event, issued_addenda, assumed_contract_value, document_files). "
            "Call before deciding applicability; never infer these from clause text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"package_id": {"type": "string", "description": "e.g. DEV-HARBOR-CROSSING"}},
            "required": ["package_id"],
        },
    },
    {
        "name": "search_contract_package",
        "description": (
            "Retrieve every clause in the package (base documents AND addenda) whose heading "
            "resolves to the given Requirement_Name, or to 'Revision to <Requirement_Name>'. "
            "Must be called before resolve_governing_document — a retrieval that skips addenda "
            "produces a confidently wrong precedence decision."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_id": {"type": "string"},
                "requirement_name": {
                    "type": "string",
                    "description": "The exact Requirement_Name from the checklist row, e.g. 'Performance and payment bonds'.",
                },
            },
            "required": ["package_id", "requirement_name"],
        },
    },
    {
        "name": "resolve_governing_document",
        "description": (
            "Resolve which single clause governs a requirement in a package: Addendum "
            "supersession first (latest ordinal wins), else the DelDOT 105.6 precedence ladder. "
            "Returns the governing clause and everything it supersedes. Test only the governing clause."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_id": {"type": "string"},
                "requirement_id": {"type": "string"},
            },
            "required": ["package_id", "requirement_id"],
        },
    },
    {
        "name": "verify_evidence_verbatim",
        "description": (
            "Check whether a candidate draft_evidence span appears verbatim (whitespace/case "
            "normalised only) in the named document. Call on every non-empty draft_evidence "
            "before emitting a row. If verbatim is false, the quote is not evidence — retrieve "
            "the clause again and quote text that exists, or lower confidence and escalate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "package_id": {"type": "string"},
                "file_name": {"type": "string", "description": "e.g. Addendum_B.pdf"},
                "span": {"type": "string", "description": "The exact text proposed as draft_evidence."},
            },
            "required": ["package_id", "file_name", "span"],
        },
    },
    {
        "name": "specifications",
        "description": (
            "Tier 3. Best-effort live fetch of the external authoritative source page for a "
            "Section citation (DelDOT engineeringsupport.deldot.gov, fhwa.dot.gov FHWA-1273, or "
            "delcode.delaware.gov). Interpretive support only — it may clarify a Tier 1 term but "
            "never supplies or overrides a number, deadline, threshold, or rate that Tier 1 states. "
            "May report that no network-reachable text was found; that is a valid, expected result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reference_source": {"type": "string", "description": "The checklist Reference_Source column value."},
                "section": {"type": "string", "description": "The exact Section citation, e.g. 'DelDOT 103.5' or '19 Del. C. § 3604'."},
            },
            "required": ["reference_source", "section"],
        },
    },
]

_TOOL_IMPL = {
    "lookup_reference_requirement": lambda i: tool_lookup_reference_requirement(**i),
    "get_project_metadata": lambda i: tool_get_project_metadata(**i),
    "search_contract_package": lambda i: tool_search_contract_package(**i),
    "resolve_governing_document": lambda i: tool_resolve_governing_document(**i),
    "verify_evidence_verbatim": lambda i: tool_verify_evidence_verbatim(**i),
    "specifications": lambda i: tool_specifications(**i),
}


# --------------------------------------------------------------------------- #
# Deterministic rule-match backend: crf.pipeline.analyse_package(), no LLM.
#
# A chat message isn't structured input, so this parses out the two things
# the pipeline needs — which package, which requirement(s) — with a regex
# rather than an LLM, then runs the same deterministic detectors the rest of
# the repo is scored against. Every row carries a rule_id/decided_by, which
# becomes the "audit trail" trace entries the UI already knows how to render.
# --------------------------------------------------------------------------- #

_REQUIREMENT_ID_RE = re.compile(r"\bCC-?\s*(\d{1,2})\b", re.IGNORECASE)
_SCORE_INTENT_RE = re.compile(r"\bscore|\bevaluat|\bgrade|\baccuracy|\blabel", re.IGNORECASE)

# Expected labels ship only with the Development split; VAL-* and uploaded
# packages have no ground truth to score against.
LABELS_PATH = DATA_ROOT / "Development" / "Development_Labels.csv"
_labels: Optional[dict] = None


def dev_labels() -> dict:
    global _labels
    if _labels is None:
        _labels = load_labels(LABELS_PATH) if LABELS_PATH.exists() else {}
    return _labels


def _evaluation_markdown(package: Package, findings: list[Finding]) -> Optional[str]:
    """Score the shown rows against Development_Labels.csv, when labels exist."""
    lbls = dev_labels()
    if not any((f.document_id, f.requirement_id) in lbls for f in findings):
        return None
    report = evaluate_against_labels(findings, lbls, [package], checklist())

    table = ["| Metric | Score | Weight | Contribution |", "|---|---|---|---|"]
    for m in report.metrics:
        table.append(
            f"| {m.name} | {m.score * 100:.1f}% | {m.weight * 100:.0f}% | {m.contribution * 100:.2f} |"
        )

    sections = [
        "### Label evaluation — Development split",
        (
            f"Weighted score: **{report.weighted_score * 100:.2f} / 100** across "
            f"{report.row_count} labelled row(s), {len(report.errors)} mismatch(es). "
            "Metrics and weights follow Evaluation_Criteria.csv."
        ),
        "\n".join(table),
    ]
    if report.errors:
        bullets = [
            (
                f"- **{e['requirement_id']}**: expected {e['expected_applicability']}/"
                f"{e['expected_label']}/{e['expected_severity']}, got "
                f"{e['predicted_applicability']}/{e['predicted_label']}/"
                f"{e['predicted_severity']} — {e['rationale']}"
            )
            for e in report.errors
        ]
        sections.append("Mismatches:\n" + "\n".join(bullets))
    return "\n\n".join(sections)


def _find_package_id_in_text(text: str) -> Optional[str]:
    _load_all()
    upper = text.upper()
    # Longest id first so one package's id can't shadow-match inside another's.
    for pid in sorted(_packages, key=len, reverse=True):
        if pid in upper:
            return pid
    return None


def _find_requirement_ids_in_text(text: str) -> list[str]:
    ids = {f"CC-{int(m):02d}" for m in _REQUIREMENT_ID_RE.findall(text)}
    known = set(checklist().ids)
    return sorted(i for i in ids if i in known)


def _finding_row_markdown(f: Finding) -> str:
    return (
        f"**{f.requirement_id}** — {f.predicted_label} ({f.severity}, "
        f"confidence {f.confidence:.2f})\n"
        f"- Applicability: {f.applicability_decision} — {f.applicability_reason}\n"
        f"- Governing document: {f.governing_document}\n"
        + (f"- Draft location: {f.draft_location}\n" if f.draft_location else "")
        + (f"- Draft evidence: \"{f.draft_evidence}\"\n" if f.draft_evidence else "")
        + f"- Reference: {f.reference_location}\n"
        f"- Explanation: {f.explanation}\n"
        f"- Recommended action: {f.recommended_human_action}"
    )


def _findings_table_markdown(findings: list[Finding]) -> str:
    header = "| Req | Label | Severity | Governing document | Confidence | Action |"
    sep = "|---|---|---|---|---|---|"
    rows = [header, sep]
    for f in findings:
        rows.append(
            f"| {f.requirement_id} | {f.predicted_label} | {f.severity} | "
            f"{f.governing_document} | {f.confidence:.2f} | {f.recommended_human_action} |"
        )
    return "\n".join(rows)


_SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}


def _summary_markdown(package_id: str, findings: list[Finding]) -> str:
    """A short natural-language read of the findings, built from the rows themselves."""
    applicable = [f for f in findings if f.applicability_decision == "APPLIES"]
    out_of_scope = len(findings) - len(applicable)
    flags = sorted(
        (f for f in findings if f.predicted_label == "FLAG"),
        key=lambda f: _SEVERITY_ORDER.get(f.severity, 9),
    )
    scope_note = (
        f", with {out_of_scope} requirement(s) out of scope under project metadata"
        if out_of_scope
        else ""
    )

    if not flags:
        return (
            f"**Summary.** No deviations were found in {package_id}: "
            f"{len(applicable)} applicable requirement(s) reviewed{scope_note}. "
            "Every row is decision support for a human reviewer, not a verdict."
        )

    lines = [
        f"**Summary.** {len(flags)} of {len(applicable)} applicable requirement(s) in "
        f"{package_id} deviate from the reference checklist{scope_note}:"
    ]
    for f in flags:
        name = checklist().get(f.requirement_id).requirement_name
        first_sentence = f.explanation.split(". ")[0].rstrip(".") + "."
        lines.append(f"- **{f.severity} — {f.requirement_id} ({name})**: {first_sentence}")
    lines.append(
        "\nThese findings are decision support for human review before award — "
        "not approval, compliance, or legal determinations."
    )
    return "\n".join(lines)


def _csv_url(package_id: str, requirement_ids: list[str]) -> str:
    url = f"/api/review/{package_id}/csv"
    if requirement_ids:
        url += "?ids=" + ",".join(requirement_ids)
    return url


def _rules_chat(req: ChatRequest) -> ChatResponse:
    package_id = _find_package_id_in_text(req.message)
    if package_id is None:
        _load_all()
        known = ", ".join(sorted(_packages)) or "none loaded yet"
        return ChatResponse(
            reply=(
                "I couldn't find a package id in that message. Upload a package or name "
                f"one already loaded exactly as shown in the picker. Known packages: {known}."
            ),
            trace=[],
        )

    try:
        package = get_package(package_id)
    except KeyError as exc:
        return ChatResponse(reply=str(exc), trace=[])

    requirement_ids = _find_requirement_ids_in_text(req.message)
    findings = analyse_package(package, checklist(), adjudicator=None)
    if requirement_ids:
        findings = [f for f in findings if f.requirement_id in requirement_ids]

    trace = [{"tool": f"{f.requirement_id} ({f.decided_by}:{f.rule_id})", "input": None, "output": f.to_audit_row()} for f in findings]

    if not findings:
        return ChatResponse(
            reply=f"No matching requirement rows for {package_id} with the ids you gave.",
            trace=trace,
        )

    summary = _summary_markdown(package.package_id, findings)
    if len(findings) == 1:
        body = _finding_row_markdown(findings[0])
    else:
        body = _findings_table_markdown(findings)

    sections = [f"### {package.package_id}", summary, body]
    evaluation = _evaluation_markdown(package, findings)
    if evaluation:
        sections.append(evaluation)
    elif _SCORE_INTENT_RE.search(req.message):
        sections.append(
            "Label evaluation is only available for Development packages (DEV-*) — "
            "they ship with expected labels in Development_Labels.csv. Validation and "
            "uploaded packages have no ground truth to score against."
        )
    return ChatResponse(
        reply="\n\n".join(sections),
        trace=trace,
        csv_url=_csv_url(package.package_id, requirement_ids),
    )


# --------------------------------------------------------------------------- #
# CES (hosted Gemini Enterprise deployment) client
#
# DORA's persona and tools are configured on Google's side for this
# deployment, so this process is a thin proxy: forward the user's text,
# return the agent's text. No local tool loop runs on this path.
# --------------------------------------------------------------------------- #

_ces_credentials = None
_ces_auth_attempted = False
_ces_auth_error: Optional[str] = None


def _ces_access_token() -> str:
    """Mint/refresh an OAuth access token via Application Default Credentials.

    Equivalent to `gcloud auth print-access-token`, but usable from a server
    process without shelling out to the CLI. Needs either
    `gcloud auth application-default login` run once in this environment, or
    a service account attached (e.g. Cloud Run's runtime service account).

    A missing-ADC lookup itself is slow (google-auth probes the GCE/Cloud Run
    metadata server, which can take several seconds to time out on a machine
    that isn't GCP). That failure is cached after the first attempt so a
    misconfigured server fails every subsequent call fast instead of re-paying
    that probe on every request; restart the process after fixing credentials.
    """
    global _ces_credentials, _ces_auth_attempted, _ces_auth_error
    if not _ces_auth_attempted:
        _ces_auth_attempted = True
        import google.auth
        import google.auth.exceptions

        try:
            _ces_credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        except google.auth.exceptions.DefaultCredentialsError as exc:
            _ces_auth_error = str(exc)

    if _ces_credentials is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "No Google Cloud Application Default Credentials found on this server. "
                "Run `gcloud auth application-default login` in the environment running "
                "dora_chat.py (or attach a service account in production), then restart "
                f"the service. Underlying error: {_ces_auth_error}"
            ),
        )

    if not _ces_credentials.valid:
        import google.auth.transport.requests

        _ces_credentials.refresh(google.auth.transport.requests.Request())
    return _ces_credentials.token


def _ces_session_resource(session_id: str) -> str:
    return f"projects/{CES_PROJECT}/locations/{CES_LOCATION}/apps/{CES_APP}/sessions/{session_id}"


def _ces_run_session(session_id: str, message: str) -> tuple[str, list[dict]]:
    token = _ces_access_token()
    session_resource = _ces_session_resource(session_id)

    config: dict[str, Any] = {
        "session": session_resource,
        "deployment": f"projects/{CES_PROJECT}/locations/{CES_LOCATION}/apps/{CES_APP}/deployments/{CES_DEPLOYMENT}",
    }
    if CES_APP_VERSION:
        config["app_version"] = (
            f"projects/{CES_PROJECT}/locations/{CES_LOCATION}/apps/{CES_APP}/versions/{CES_APP_VERSION}"
        )

    url = f"https://ces.googleapis.com/{CES_API_VERSION}/{session_resource}:runSession"
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"config": config, "inputs": [{"text": message}]},
            timeout=90,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"CES request failed: {exc}") from exc

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"CES returned {resp.status_code}: {resp.text[:2000]}")

    data = resp.json()
    texts: list[str] = []
    trace: list[dict] = []
    for out in data.get("outputs", []):
        if "text" in out:
            texts.append(out["text"])
        elif "toolCalls" in out:
            # Tool execution is configured to happen on Google's side for this
            # deployment; surfaced here only as an audit-trail entry, not
            # something this process needs to act on.
            trace.append({"tool": "ces:toolCalls", "input": None, "output": out["toolCalls"]})
        elif "citations" in out:
            trace.append({"tool": "ces:citations", "input": None, "output": out["citations"]})
        elif "endSession" in out:
            trace.append({"tool": "ces:endSession", "input": None, "output": out["endSession"]})

    if not texts:
        LOG.warning("CES runSession returned no text output: %s", json.dumps(data)[:2000])
        return (
            "DORA's hosted agent responded without a text output. This can happen if the "
            "deployment expects streaming (streamRunSession, not implemented here) or the turn "
            "didn't complete. Check the server logs for the raw response.",
            trace,
        )
    return "".join(texts), trace


# --------------------------------------------------------------------------- #
# Gemini client + tool declarations + chat loop (local fallback; see
# DORA_BACKEND above)
# --------------------------------------------------------------------------- #

_genai_client = None
_genai_tool = None  # built lazily too, since it needs the `types` module


def _client():
    global _genai_client
    if _genai_client is None:
        if not os.environ.get("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail="GOOGLE_API_KEY is not set on the server. Export it in the server "
                "environment (never in the browser) and restart the service.",
            )
        from google import genai  # lazy import: app can boot with no key configured

        _genai_client = genai.Client()
    return _genai_client


def _tool() -> Any:
    """The single genai.types.Tool wrapping all six DORA tool declarations."""
    global _genai_tool
    if _genai_tool is None:
        from google.genai import types

        _genai_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t["input_schema"],
                )
                for t in TOOLS
            ]
        )
    return _genai_tool


# session_id -> genai.types.Content list. In-memory only: a demo-scale
# convenience, not a durable store. Restarting the server clears all sessions.
_sessions: dict[str, list[Any]] = {}


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    reply: str
    trace: list[dict]
    # Set by the rules backend: relative URL where the same review can be
    # downloaded as a 15-field submission-schema CSV.
    csv_url: Optional[str] = None


app = FastAPI(title="DORA chat", version="1.0.0")


@app.get("/api/packages")
def list_packages() -> dict:
    _load_all()
    return {"packages": sorted(_packages)}


@app.get("/api/packages/{package_id}/briefing")
def package_briefing(package_id: str, download: bool = False) -> Response:
    """The full parsed package as plain text, for pasting into a hosted agent.

    Hosted agents (Copilot Studio, Gemini Enterprise) run on their vendor's
    side and cannot reach this server, so a locally-uploaded package is
    invisible to them. Their chat input, however, accepts text — and a parsed
    package is only a few thousand words. This renders metadata plus every
    clause verbatim so the user can hand the whole package to the agent in
    one paste.
    """
    try:
        pkg = get_package(package_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    lines = [
        f"CONTRACT PACKAGE CONTENT: {pkg.package_id} ({pkg.project_title})",
        "These are the package documents for review, extracted clause-by-clause "
        "from the package PDFs. Treat them as the authoritative package text; "
        f"use \"{pkg.package_id}\" as the document_id on every output row.",
        "Formatting note: reply in plain text — do not use bold or other "
        "markdown emphasis in your responses.",
        "",
        "PROJECT METADATA (authoritative for applicability decisions):",
    ]
    for key, value in pkg.metadata.items():
        lines.append(f"  {key}: {value}")
    lines += ["", f"DOCUMENTS: {', '.join(pkg.doc_files)}"]
    for clause in pkg.clauses:
        marker = "  [ADDENDUM REPLACEMENT TEXT]" if clause.is_replacement else ""
        lines += ["", f"--- {clause.location}{marker} ---", clause.text]

    headers = {}
    if download:
        # Chat attachment pickers take single files, not folders — this hands
        # the whole package over as one attachable .txt.
        headers["Content-Disposition"] = f'attachment; filename="{pkg.package_id}_package.txt"'
    return Response(
        content="\n".join(lines),
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )


@app.get("/api/review/{package_id}/csv")
def review_csv(package_id: str, ids: str = "") -> Response:
    """The current review as a submission-schema CSV (all 15 fields).

    Deterministic re-run of the same pipeline the chat answer came from, so the
    file always matches what the user was just shown. `ids` optionally narrows
    to a comma-separated list of CC-NN requirement ids.
    """
    try:
        package = get_package(package_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    findings = analyse_package(package, checklist(), adjudicator=None)
    wanted = _find_requirement_ids_in_text(ids)
    if wanted:
        findings = [f for f in findings if f.requirement_id in wanted]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(Finding.SUBMISSION_FIELDS))
    writer.writeheader()
    for finding in findings:
        writer.writerow(finding.to_submission_row())

    suffix = "_" + "_".join(wanted) if wanted else ""
    file_name = f"{package.package_id}{suffix}_review.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


def _safe_upload_package_id(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        value = f"UPLOAD-{uuid.uuid4().hex[:8].upper()}"
    if not _PACKAGE_ID_RE.match(value):
        raise HTTPException(
            status_code=400,
            detail="package_id may contain only letters, digits, '-' and '_' (max 64 characters).",
        )
    return value


@app.post("/api/packages/upload")
async def upload_package(
    package_id: str = Form(""),
    files: list[UploadFile] = File(...),
) -> dict:
    """Accept a user-supplied contract package and make it reviewable immediately.

    Expects, in any order, as one multipart upload: a file literally named
    Project_Metadata.json (required), an optional Document_Index.csv, and one or
    more *.pdf documents. Anything else is ignored. Classification is by exact
    filename / extension, not by any folder structure the browser may have sent,
    so a flat multi-file picker works with no client-side directory handling.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")
    if len(files) > MAX_UPLOAD_FILES:
        raise HTTPException(status_code=400, detail=f"Too many files (max {MAX_UPLOAD_FILES}).")

    _load_all()  # ensure the sample dataset is loaded before we add to _packages

    pkg_id = _safe_upload_package_id(package_id)
    pkg_root = (UPLOAD_ROOT / pkg_id).resolve()
    if UPLOAD_ROOT not in pkg_root.parents:
        raise HTTPException(status_code=400, detail="Invalid package_id.")

    # A re-upload under the same id replaces the prior contents outright, so
    # stale documents from an earlier attempt can never linger and get judged.
    if pkg_root.exists():
        shutil.rmtree(pkg_root)
    docs_dir = pkg_root / "Docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    has_metadata = False
    saved_pdfs: list[str] = []
    try:
        for f in files:
            name = Path(f.filename or "").name  # drop any path component the browser sent
            ext = Path(name).suffix.lower()
            if name not in ALLOWED_UPLOAD_NAMES and ext != ".pdf":
                continue  # ignore .DS_Store and anything else unrecognised

            data = await f.read()
            if len(data) > MAX_UPLOAD_FILE_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"{name} exceeds the {MAX_UPLOAD_FILE_BYTES // (1024 * 1024)} MB per-file limit.",
                )

            if name == "Project_Metadata.json":
                (pkg_root / name).write_bytes(data)
                has_metadata = True
            elif name == "Document_Index.csv":
                (pkg_root / name).write_bytes(data)
            elif ext == ".pdf":
                (docs_dir / name).write_bytes(data)
                saved_pdfs.append(name)

        if not has_metadata:
            raise HTTPException(
                status_code=400,
                detail="Project_Metadata.json is required (exact file name) so applicability can be checked.",
            )
        if not saved_pdfs:
            raise HTTPException(status_code=400, detail="At least one PDF document is required.")

        try:
            pkg = load_package(pkg_root, checklist())
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse the package: {exc}") from exc

    except HTTPException:
        shutil.rmtree(pkg_root, ignore_errors=True)
        raise

    _packages[pkg.package_id.upper()] = pkg
    _loaded_roots.add(str(pkg_root))
    LOG.info("uploaded package %s: %d PDF(s), %d clause(s)", pkg.package_id, len(pkg.doc_files), len(pkg.clauses))
    return {
        "package_id": pkg.package_id,
        "project_title": pkg.project_title,
        "documents": pkg.doc_files,
        "clauses_extracted": len(pkg.clauses),
    }


@app.get("/api/health")
def health() -> dict:
    base = {"ok": True, "backend": DORA_BACKEND, "system_prompt_chars": len(SYSTEM_PROMPT)}
    if DORA_BACKEND == "rules":
        _load_all()
        base.update(
            {
                "model": "deterministic-rule-pipeline (crf.pipeline.analyse_package)",
                "model_key_configured": True,  # no credential needed on this path
                "packages_loaded": len(_packages),
            }
        )
    elif DORA_BACKEND == "ces":
        adc_found = True
        try:
            _ces_access_token()
        except HTTPException:
            adc_found = False
        base.update(
            {
                "model": "ces:" + CES_DEPLOYMENT,
                "model_key_configured": adc_found,
                "ces_session_resource_prefix": f"projects/{CES_PROJECT}/locations/{CES_LOCATION}/apps/{CES_APP}",
            }
        )
    else:
        base.update({"model": active_model(), "model_key_configured": bool(os.environ.get("GOOGLE_API_KEY"))})
    return base


@app.post("/api/session/reset")
def reset_session(payload: dict) -> dict:
    session_id = str(payload.get("session_id", "")).strip()
    _sessions.pop(session_id, None)
    return {"ok": True}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if DORA_BACKEND == "rules":
        return _rules_chat(req)
    if DORA_BACKEND == "ces":
        reply, trace = _ces_run_session(req.session_id, req.message)
        return ChatResponse(reply=reply, trace=trace)
    return _gemini_chat(req)


def _runtime_system_prompt() -> str:
    """DORA's prompt plus what is actually loaded right now.

    Regenerated per request so packages uploaded mid-session (visible to the
    tools through the shared uploads/ rescan) are also visible to the model —
    otherwise it asks the user to 'provide the contract package' it already has.
    """
    _load_all()
    upload_prefix = str(UPLOAD_ROOT)
    uploaded = sorted(p for p, pkg in _packages.items() if pkg.root.startswith(upload_prefix))
    builtin = sorted(p for p in _packages if p not in set(uploaded))
    return (
        SYSTEM_PROMPT
        + "\n\n<runtime_context>Packages loaded in the review server and queryable "
        f"through your tools right now — challenge packages: {', '.join(builtin) or 'none'}; "
        f"user-uploaded packages: {', '.join(uploaded) or 'none'}. Review uploaded "
        "packages exactly like challenge packages. If the user asks what packages are "
        "available or what they uploaded, answer from these lists instead of asking "
        "them to provide documents.</runtime_context>"
    )


# Index into [MODEL_ID] + MODEL_FALLBACKS of the model currently in use.
# Advances when a model's daily free-tier quota is exhausted; process-wide so
# one 429 doesn't get re-hit by every subsequent request.
_active_model_idx = 0


def _generate_with_fallback(client, history, cfg):
    """generate_content with two failure policies:

    - 429 RESOURCE_EXHAUSTED (daily quota spent): advance the chain
      permanently — the bucket stays empty until the daily reset.
    - 503 UNAVAILABLE (temporary capacity spike on Google's side): retry the
      same model with a short backoff, then hop to the next model for this
      request only — the preferred model usually recovers within minutes.
    """
    global _active_model_idx
    candidates = [MODEL_ID] + MODEL_FALLBACKS
    idx = _active_model_idx
    last_exc: Optional[Exception] = None

    while idx < len(candidates):
        model = candidates[idx]
        for attempt in range(3):
            try:
                return client.models.generate_content(model=model, contents=history, config=cfg)
            except Exception as exc:
                last_exc = exc
                msg = str(exc)
                if "RESOURCE_EXHAUSTED" in msg or "'code': 429" in msg:
                    LOG.warning("model %s daily quota exhausted; falling back permanently", model)
                    if idx + 1 < len(candidates):
                        _active_model_idx = idx + 1
                    break  # next candidate
                if "UNAVAILABLE" in msg or "'code': 503" in msg:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue  # transient — retry the same model
                    LOG.warning("model %s still unavailable after retries; hopping for this request", model)
                    break  # next candidate, without moving the global index
                raise
        idx += 1

    raise last_exc if last_exc else RuntimeError("no model candidates configured")


def active_model() -> str:
    return ([MODEL_ID] + MODEL_FALLBACKS)[_active_model_idx]


def _gemini_chat(req: ChatRequest) -> ChatResponse:
    from google.genai import types

    client = _client()
    cfg = types.GenerateContentConfig(
        system_instruction=_runtime_system_prompt(),
        tools=[_tool()],
        max_output_tokens=8192,
    )

    if req.session_id not in _sessions and len(_sessions) >= MAX_SESSIONS:
        # Evict an arbitrary session rather than growing without bound.
        _sessions.pop(next(iter(_sessions)), None)
    history = _sessions.setdefault(req.session_id, [])
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=req.message)]))

    trace: list[dict[str, Any]] = []
    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            resp = _generate_with_fallback(client, history, cfg)
        except Exception as exc:
            LOG.exception("Gemini API call failed")
            raise HTTPException(status_code=502, detail=f"Model call failed: {exc}") from exc

        if not resp.candidates or resp.candidates[0].content is None:
            reason = resp.candidates[0].finish_reason if resp.candidates else "no candidates"
            return ChatResponse(
                reply=f"DORA got no usable response from the model (finish_reason={reason}). Please retry.",
                trace=trace,
            )

        turn = resp.candidates[0].content
        history.append(turn)

        function_calls = [p.function_call for p in turn.parts if p.function_call]
        if not function_calls:
            final_text = "".join(p.text for p in turn.parts if p.text)
            return ChatResponse(reply=final_text, trace=trace)

        response_parts = []
        for call in function_calls:
            impl = _TOOL_IMPL.get(call.name)
            if impl is None:
                result: dict = {"error": f"Unknown tool {call.name!r}"}
            else:
                try:
                    result = impl(dict(call.args or {}))
                except Exception as exc:
                    result = {"error": f"{exc.__class__.__name__}: {exc}"}
            trace.append({"tool": call.name, "input": call.args, "output": result})
            response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        id=call.id,
                        name=call.name,
                        response=json.loads(json.dumps(result, default=str)),
                    )
                )
            )
        history.append(types.Content(role="user", parts=response_parts))

    return ChatResponse(
        reply=(
            "DORA stopped after too many tool calls without a final answer. "
            "Please retry, or narrow the request to one document/requirement pair."
        ),
        trace=trace,
    )


# --------------------------------------------------------------------------- #
# Static frontend
# --------------------------------------------------------------------------- #

@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
