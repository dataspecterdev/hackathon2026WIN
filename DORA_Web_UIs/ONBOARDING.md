# Onboarding — how this codebase is put together

Three docs, three jobs:

| Doc | Answers |
|---|---|
| [`README.md`](./README.md) | What this is and how to run it |
| [`SOLUTION.md`](./SOLUTION.md) | *Why* it's built this way — the argument, the results, the limitations |
| **This file** | *Where* things live and what to edit when you want to change a behaviour |

Read this if you're about to touch the code.

---

## 1. Fifteen-minute orientation

```bash
pip install -r requirements.txt
brew install poppler                  # pdftotext; or: pip install pypdf

python3 run.py dev                    # should print 100.00 / 108 rows exact
python3 run.py inspect Harbor_Crossing # the single most useful command in the repo
python3 run.py robustness             # should print 46/46
```

`inspect` prints, for one package: the project metadata, every clause found per
requirement, which one **governs** and which are **superseded** (and why), the
applicability decision for all 18 requirements, and any heading that failed to
resolve. If you're ever confused about why a row came out the way it did, start here.

---

## 2. The one mental model

Every output row is one **(package × requirement)** pair, decided by four layers
that run in a **fixed order**:

```
ingest → applicability gate → precedence resolution → invariant detector → (LLM only if uncertain) → emit
```

The order is load-bearing, not stylistic:

- **Applicability before retrieval** — an out-of-scope requirement never reads a
  clause, so it structurally cannot produce a false flag.
- **Precedence before detection** — the detector only ever sees the *one* clause
  that actually governs, so superseded base text can't cause a false positive.
- **LLM last** — by the time the model is asked anything, the question has been
  narrowed to "is this one clause materially deviant, yes or no?"

If you find yourself wanting to move work between layers, re-read
[SOLUTION.md § Why the layer order is the design](./SOLUTION.md#why-the-layer-order-is-the-design)
first. Most "improvements" that reorder these reintroduce a bug the order was
built to prevent.

---

## 3. File map

### The pipeline (`crf/`)

| File | Owns | You'd edit it when… |
|---|---|---|
| `models.py` | The 5 dataclasses everything passes around | You're adding a field to the output |
| `reference.py` | Loads the checklist; maps a document heading → requirement ID | A heading isn't being recognised |
| `extract.py` | PDF → heading-anchored `Clause` records | Extraction is mangling text or missing sections |
| `applicability.py` | `APPLIES` / `DOES_NOT_APPLY` from project metadata | A requirement is in/out of scope wrongly |
| `precedence.py` | Which clause governs (addendum supersession, then DelDOT 105.6) | The wrong document is cited as governing |
| `detectors.py` | One invariant test per requirement (18 of them) | **A FLAG / NO_FLAG verdict is wrong** ← most edits land here |
| `llm.py` | The narrow adjudicator + provider plumbing | You're changing the escalation prompt or adding a provider |
| `pipeline.py` | Runs the four layers, writes the CSVs | You're changing orchestration or output shape |

### The checks (these read the output, they never feed back into decisions)

| File | Checks |
|---|---|
| `evaluate.py` | Scores against `Development_Labels.csv` using the official weights |
| `perturb.py` | Builds mutated `Package` objects whose right answer is known by construction |
| `robustness.py` | Runs 46 perturbation cases and reports `TARGET` / `DRIFT` / `GOVERN` / `DEGRADE` |
| `conformance.py` | 11 machine checks on the submission CSVs — deliberately has **zero** internal imports so it can't be fooled by a shared bug |

### Everything else

```
run.py                          CLI: dev / val / all / inspect / robustness / schema
Contract_Clause_Risk_Flagging/  the challenge dataset (packages, checklist, schema, labels)
out/                            generated submission + audit CSVs
deploy/                         AWS CDK stack (API Gateway + Lambda)
instruction/                    hackathon participant guide
```

---

## 4. The five data shapes

They flow strictly left to right; nothing flows back.

```
Requirement   one checklist row — the scoring authority        (reference.py)
   │
Clause        heading + text + file + page, lifted from a PDF  (extract.py)
   │
Package       metadata + doc index + all its clauses           (extract.py)
   │
Verdict       label + explanation + confidence + rule_id       (detectors.py / llm.py)
   │          `uncertain=True` is the *only* escalation signal
Finding       one submission row, 15 fields + 2 audit fields   (pipeline.py)
```

`Verdict.uncertain` is worth internalising: it's how a detector says *"I don't
know"* instead of guessing. That flag, and nothing else, is what invokes the LLM.

---

## 5. "I want to change X" → edit Y

| Goal | Where | Note |
|---|---|---|
| Fix a wrong FLAG/NO_FLAG | `detectors.py`, function `ccNN_*` | Find it via the `rule_id` in the audit CSV |
| A heading isn't recognised | `reference.py` → `HEADING_ALIASES` | Add `"normalised heading": "CC-NN"` |
| A heading is being treated as a clause but shouldn't be | `reference.py` → `IGNORED_HEADINGS` | |
| A requirement should/shouldn't be in scope | `applicability.py` → `_RULES` | Predicate + both reason strings; reasons must cite the actual metadata field |
| Wrong governing document | `precedence.py` → `_DOC_TYPE_RANK` or `addendum_ordinal` | |
| Add/rename an output column | `models.py` → `SUBMISSION_FIELDS`, then `conformance.py` | Both, or `run.py schema` fails |
| Add a regression test | `robustness.py` → `build_cases()`, helpers in `perturb.py` | |
| Change what the LLM is asked | `llm.py` → `SYSTEM_PROMPT` / `USER_TEMPLATE` | Keep it to the one bounded question |

---

## 6. Anatomy of a detector

All 18 look like this. `cc02_bid_guaranty` is the clearest example:

```python
def cc02_bid_guaranty(clause: Clause | None, pkg: Package) -> Verdict:
    """Proposal guaranty must equal 10% of total bid price."""
    text = clause.text if clause else ""
    pcts = percents(text)                      # 1. extract the invariant

    if 10 in pcts or has(text, r"one-tenth"):  # 2. satisfied → NO_FLAG
        return ok(..., "CC02.ten_percent", evidence=find_sentence(text, r"10\s*%|one-tenth"))

    if pcts:                                   # 3. present but wrong → FLAG
        bad = [p for p in pcts if p != 10]
        return flag(..., "CC02.wrong_percent", find_sentence(text, rf"{bad[0]}\s*%"))

    if defers(text):                           # 4. defers to the reference → NO_FLAG
        return ok(..., "CC02.defers", 0.85, ...)

    return unsure("No proposal guaranty percentage located.", "CC02.no_value", text)
```

Four helpers build the `Verdict`: **`ok()`** (NO_FLAG), **`flag()`** (FLAG),
**`unsure()`** (NO_FLAG with `uncertain=True`, escalates to the LLM), and the
shared extractors `percents()`, `days()`, `retention_years()`, `has()`,
`defers()`, `find_sentence()`.

`rule_id` convention is `CCNN.what_fired`. It lands in the audit CSV, so any row
can be traced back to the exact branch that produced it. Give new branches a
distinct id — that's what makes `DEGRADE` detection work.

---

## 7. Rules of the road

Five invariants. Breaking any of them will show up as a robustness failure, but
it's cheaper to just not break them:

1. **Flag on a violated invariant, never on textual difference.** `ten percent
   (10%)` and `one-tenth (10%)` are the same requirement. Compare the *number*,
   not the string.
2. **Evidence must be a verbatim span of the governing clause.** Every detector
   returns the sentence it actually fired on. Don't paraphrase into
   `draft_evidence`.
3. **Return `unsure()` rather than guessing.** A wrong confident answer is worse
   than an escalation.
4. **Clauses that defer to the reference are compliant.** "within the reference
   period" preserves the requirement — it is not a missing deadline.
5. **Severity is looked up, not decided.** It comes from the checklist's
   `Severity_Guidance`, and is `Info` on every non-FLAG row.

---

## 8. Before you push

```bash
python3 run.py all         # 100.00 / 108 rows exact on dev; 36 rows on val
python3 run.py schema      # 11/11 conformance checks
python3 run.py robustness  # 46/46
```

All three should be green. `robustness` is the one that catches subtle damage:
a `DRIFT` failure means your detector started reading text that belongs to a
different requirement, which the dev score alone will not reveal.

Runs are deterministic — two consecutive `run.py all` invocations produce
byte-identical CSVs. If they don't, something is wrong.

---

## 9. Debugging tips

- **`run.py inspect <package>`** first, always. Substring match, case-insensitive.
- **`out/audit_*.csv`** adds `decided_by` (`applicability` / `rule` / `llm`) and
  `rule_id` to every row — this is how you find the code path without a debugger.
- **`CRF_PDF_BACKEND=pypdf`** forces the pure-Python extraction path (the one
  Lambda uses, since there's no poppler binary there). Worth running before any
  deploy to confirm the two backends agree.
- **`run.py robustness <filter>`** narrows the suite by case kind or name.
- The LLM path is **off by default** (`--llm null`). Nothing hits the network
  unless you pass `--llm bedrock` or `--llm anthropic`.

---

## 10. Known rough edges

- `cmd_split` in `run.py` ends with `return 0 if not report.errors else 0` — both
  branches return 0, so a failing dev evaluation still exits successfully. Should
  be `else 1`.
- Addendum ordering comes from the filename letter (`Addendum_A` → 1). Real
  addenda are dated, and dates should drive it. Fine for this dataset, wrong for
  production.
- `General Conditions` has no exact slot in the DelDOT 105.6 ladder; it's mapped
  to the `Standard Specifications` rank. Untested by this data — see
  [SOLUTION.md § Limitations](./SOLUTION.md#limitations).
