"""HTTP wrapper exposing the deterministic layers as agent tools, plus upload.

Endpoints
---------
POST /packages              multipart upload of one contract package -> package_id
GET  /packages              list packages currently available
POST /project-metadata      exact metadata booleans (drives applicability)
POST /search-package        clauses addressing a requirement, base docs AND addenda
POST /governing-document    precedence.resolve(), the one clause to judge
POST /verify-evidence       is this span verbatim in the cited document

The upload endpoint is what lets an end user drop a folder into your UI. The
files are parsed once, on arrival, into the same Clause objects the offline
pipeline uses, and held under a generated package_id. Every tool call the agent
makes carries that package_id, so a session can only ever see its own package.

Layers 3 and 4 are deliberately NOT exposed. Deciding whether a clause
materially deviates is the one genuinely semantic judgement; that is the
agent's job. Everything here is a stated rule executed in code.

Run locally:
    pip install fastapi uvicorn python-multipart
    python3 deploy/tool_server.py            # http://localhost:8080/docs

Deploy:
    gcloud run deploy deldot-review-tools --source . --region us-central1
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from crf import precedence
from crf.extract import discover_packages, load_package
from crf.models import Clause, Package
from crf.reference import ReferenceChecklist

# --------------------------------------------------------------------------- #
# Checklist and package registry
# --------------------------------------------------------------------------- #

DATA_ROOT = Path(
    os.environ.get("CRF_DATA_ROOT", "Contract_Clause_Risk_Flagging")
).resolve()
CHECKLIST_PATH = DATA_ROOT / "References" / "Reference_Checklist.csv"
BUNDLED_SPLITS = ("Development", "Validation")
UPLOAD_ROOT = Path(os.environ.get("CRF_UPLOAD_ROOT", tempfile.gettempdir())) / "crf-uploads"

_checklist: ReferenceChecklist | None = None
_packages: dict[str, Package] = {}
_bundled_loaded = False


def checklist() -> ReferenceChecklist:
    global _checklist
    if _checklist is None:
        _checklist = ReferenceChecklist.load(CHECKLIST_PATH)
    return _checklist


def _load_bundled() -> None:
    """Parse the packages shipped with the repo once, on first request."""
    global _bundled_loaded
    if _bundled_loaded:
        return
    _bundled_loaded = True
    for split in BUNDLED_SPLITS:
        split_root = DATA_ROOT / split
        if not split_root.exists():
            continue
        for pkg_root in discover_packages(split_root):
            try:
                pkg = load_package(pkg_root, checklist())
                _packages[pkg.package_id.upper()] = pkg
            except Exception as exc:  # a bad bundled package must not kill startup
                print(f"[startup] skipped {pkg_root}: {exc}")


def get_package(package_id: str) -> Package:
    _load_bundled()
    pkg = _packages.get((package_id or "").strip().upper())
    if pkg is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown package_id {package_id!r}. "
            f"Known: {', '.join(sorted(_packages)) or '(none)'}",
        )
    return pkg


def _norm(text: str) -> str:
    """Whitespace and case normalisation only - never alters wording."""
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


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


app = FastAPI(
    title="DelDOT Contract Review - deterministic tools",
    version="2.0.0",
    description="Package upload, applicability inputs, clause retrieval, "
    "precedence resolution, evidence verification.",
)


# --------------------------------------------------------------------------- #
# 0. Upload - a user drops a folder, we parse it and hand back a package_id
# --------------------------------------------------------------------------- #

# Files the browser will send that we must never write to disk.
_JUNK = {".ds_store", "thumbs.db", "desktop.ini"}


def _safe_relative(raw: str, fallback: str) -> Optional[Path]:
    """Reject absolute paths, traversal, and junk. Return a clean relative path."""
    candidate = (raw or fallback or "").strip().replace("\\", "/")
    if not candidate:
        return None
    parts = [p for p in candidate.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        return None
    if not parts or parts[-1].lower() in _JUNK or parts[-1].startswith("."):
        return None
    return Path(*parts)


@app.post("/packages", operation_id="upload_contract_package")
async def upload_contract_package(
    files: list[UploadFile] = File(...),
    paths: list[str] = Form(default=[]),
    package_id: str = Form(default=""),
) -> dict:
    """Accept one contract package as uploaded files and return its package_id.

    Send each file with its folder-relative path (the browser's
    webkitRelativePath) in the parallel `paths` field, so Docs/ and the
    top-level Project_Metadata.json land in the right places.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files received.")

    upload_id = (package_id or f"UPLOAD-{uuid.uuid4().hex[:8]}").strip().upper()
    root = UPLOAD_ROOT / upload_id
    if root.exists():
        shutil.rmtree(root)
    (root / "Docs").mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    skipped: list[str] = []

    for i, upload in enumerate(files):
        raw = paths[i] if i < len(paths) else (upload.filename or "")
        rel = _safe_relative(raw, upload.filename or "")
        if rel is None:
            skipped.append(raw or upload.filename or "<unnamed>")
            continue

        # Drop the user's own top folder name so the layout is predictable, then
        # route PDFs into Docs/ and the two control files to the package root.
        tail = rel.name
        if tail.lower().endswith(".pdf"):
            dest = root / "Docs" / tail
        elif tail in ("Project_Metadata.json", "Document_Index.csv"):
            dest = root / tail
        else:
            skipped.append(str(rel))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fh:
            shutil.copyfileobj(upload.file, fh)
        written.append(str(dest.relative_to(root)))

    if not (root / "Project_Metadata.json").exists():
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail="Project_Metadata.json is missing. Applicability cannot be "
            "decided without it, and a review that guesses applicability is "
            "worse than no review. Upload the whole package folder.",
        )
    if not any((root / "Docs").glob("*.pdf")):
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(status_code=400, detail="No PDF documents found in the upload.")

    try:
        pkg = load_package(root, checklist())
    except Exception as exc:
        shutil.rmtree(root, ignore_errors=True)
        raise HTTPException(status_code=422, detail=f"Could not parse package: {exc}")

    # The metadata's own package_id wins if it has one, so DEV-HARBOR-CROSSING
    # stays DEV-HARBOR-CROSSING rather than becoming UPLOAD-1a2b3c4d.
    resolved_id = (pkg.package_id or upload_id).strip().upper()
    pkg.package_id = resolved_id
    for c in pkg.clauses:
        c.package_id = resolved_id
    _packages[resolved_id] = pkg

    addenda = sorted({c.file_name for c in pkg.clauses if precedence.is_addendum(c)})
    resolvable = sorted({
        req.requirement_id
        for req in checklist()
        if precedence.candidates(pkg, req.requirement_id, checklist())
    })

    return {
        "package_id": resolved_id,
        "project_title": pkg.project_title,
        "documents": pkg.doc_files,
        "addenda": addenda,
        "clauses_parsed": len(pkg.clauses),
        "requirements_with_clauses": resolvable,
        "requirements_without_clauses": [
            r for r in checklist().ids() if r not in resolvable
        ],
        "files_written": written,
        "files_skipped": skipped,
        "next": f"Start a session keyed on {resolved_id} and review all 18 requirements.",
    }


@app.get("/packages", operation_id="list_packages")
def list_packages() -> dict:
    _load_bundled()
    return {
        "packages": [
            {
                "package_id": pid,
                "project_title": p.project_title,
                "documents": p.doc_files,
            }
            for pid, p in sorted(_packages.items())
        ]
    }


# --------------------------------------------------------------------------- #
# 1. Project metadata - drives the applicability gate
# --------------------------------------------------------------------------- #

class MetadataRequest(BaseModel):
    package_id: str = Field(..., examples=["DEV-HARBOR-CROSSING"])


@app.post("/project-metadata", operation_id="get_project_metadata")
def get_project_metadata(req: MetadataRequest) -> dict:
    """Exact metadata booleans. Read before any contract text."""
    pkg = get_package(req.package_id)
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


# --------------------------------------------------------------------------- #
# 2. Clause retrieval - every clause addressing a requirement, addenda included
# --------------------------------------------------------------------------- #

class SearchRequest(BaseModel):
    package_id: str = Field(..., examples=["DEV-HARBOR-CROSSING"])
    requirement_id: str = Field(..., examples=["CC-04"])


@app.post("/search-package", operation_id="search_contract_package")
def search_contract_package(req: SearchRequest) -> dict:
    """Every clause addressing this requirement, base documents AND addenda.

    Heading-anchored, not similarity-ranked: the package uses the checklist
    Requirement_Name verbatim as a section heading and addenda use
    "Revision to <Requirement_Name>", so this is exact, complete, and has no
    top-k cutoff that could silently drop the addendum that supersedes the base.
    """
    pkg = get_package(req.package_id)
    req_id = req.requirement_id.strip().upper()
    if req_id not in set(checklist().ids()):
        raise HTTPException(
            status_code=404, detail=f"Unknown requirement_id {req.requirement_id!r}"
        )

    found = precedence.candidates(pkg, req_id, checklist())
    return {
        "package_id": pkg.package_id,
        "requirement_id": req_id,
        "requirement_name": checklist().get(req_id).requirement_name,
        "clause_count": len(found),
        "clauses": [clause_payload(c) for c in found],
        "note": "All matches are returned, addenda included. Do not judge any of "
        "these until resolve_governing_document has selected which one governs.",
    }


# --------------------------------------------------------------------------- #
# 3. Precedence - which single clause governs
# --------------------------------------------------------------------------- #

class PrecedenceRequest(BaseModel):
    package_id: str = Field(..., examples=["DEV-HARBOR-CROSSING"])
    requirement_id: str = Field(..., examples=["CC-04"])


def _basis(governing: Optional[Clause], superseded: list[Clause]) -> str:
    if governing is None:
        return "not_located"
    if precedence.is_addendum(governing) and governing.is_replacement:
        return "addendum_replacement"
    return "deldot_105_6" if superseded else "single_occurrence"


@app.post("/governing-document", operation_id="resolve_governing_document")
def resolve_governing_document(req: PrecedenceRequest) -> dict:
    """Addendum supersession first, then the DelDOT 105.6 ladder."""
    pkg = get_package(req.package_id)
    req_id = req.requirement_id.strip().upper()
    if req_id not in set(checklist().ids()):
        raise HTTPException(
            status_code=404, detail=f"Unknown requirement_id {req.requirement_id!r}"
        )

    governing, superseded, note = precedence.resolve(pkg, req_id, checklist())

    return {
        "package_id": pkg.package_id,
        "requirement_id": req_id,
        "found": governing is not None,
        "governing": clause_payload(governing) if governing else None,
        "governing_document": (
            f"{governing.doc_type} ({governing.file_name})"
            if governing
            else "Not located in package"
        ),
        "superseded": [clause_payload(c) for c in superseded],
        "resolution_basis": _basis(governing, superseded),
        "resolution_note": note,
    }


# --------------------------------------------------------------------------- #
# 4. Evidence verification - is this span really in that document
# --------------------------------------------------------------------------- #

class EvidenceRequest(BaseModel):
    package_id: str = Field(..., examples=["DEV-HARBOR-CROSSING"])
    file_name: str = Field(..., examples=["Addendum_B.pdf"])
    span: str = Field(..., examples=["Required bond coverage shall equal one hundred percent (100%)"])


@app.post("/verify-evidence", operation_id="verify_evidence_verbatim")
def verify_evidence_verbatim(req: EvidenceRequest) -> dict:
    """True only if the span occurs in that document after whitespace/case normalisation."""
    pkg = get_package(req.package_id)
    wanted_file = req.file_name.strip().lower()

    in_file = [c for c in pkg.clauses if c.file_name.lower() == wanted_file]
    if not in_file:
        raise HTTPException(
            status_code=404,
            detail=f"{req.file_name!r} is not a document of {pkg.package_id}. "
            f"Documents: {', '.join(pkg.doc_files)}",
        )

    needle = _norm(req.span)
    if not needle:
        return {
            "verbatim": False,
            "package_id": pkg.package_id,
            "file_name": req.file_name,
            "matched_heading": None,
            "matched_page": None,
            "message": "Empty span. An empty draft_evidence is only correct for a "
            "DOES_NOT_APPLY row, where no clause was read.",
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
        "file_name": req.file_name,
        "matched_heading": None,
        "matched_page": None,
        "message": "This span does not occur in the cited document. It is not "
        "evidence. Retrieve the governing clause again and quote text that "
        "exists, or lower confidence and escalate the row for human review. "
        "Do not paraphrase this span into place.",
    }


@app.get("/healthz")
def healthz() -> dict:
    _load_bundled()
    return {"ok": True, "packages": sorted(_packages)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
