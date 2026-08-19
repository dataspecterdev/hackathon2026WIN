# Evaluation Scorecard — DEV-NORTHFIELD

**Compared:** `DEV-NORTHFIELD_CC_Review_Submission.csv` (18 generated rows)
**Against:** `Development_Labels-aa132f78.csv` — 18 relevant rows filtered on `Package_ID = DEV-NORTHFIELD` (of 108 total rows spanning 6 packages: DEV-PINE-GROVE, DEV-HARBOR-CROSSING, DEV-STONE-CREEK, DEV-NORTHFIELD, DEV-MAPLE-RIDGE, DEV-RIVERBEND)
**Metrics:** `Evaluation_Criteria-b6bad5e9.csv` — 6 metrics, weights totaling 100%
**Evaluated:** 2026-08-19 (UTC)

---

## Headline result

**18 of 18 rows are a full match** on all three labeled dimensions (applicability, label, severity). Zero mismatches, zero false positives, zero false negatives.

---

## Row-by-row comparison

| ID | Expected App. | Predicted App. | Expected Label | Predicted Label | Expected Sev. | Predicted Sev. | Result | Gold rationale |
|---|---|---|---|---|---|---|---|---|
| CC-01 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-02 | APPLIES | APPLIES | FLAG | FLAG | High | High | **FULL MATCH** | 5% bid guaranty |
| CC-03 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | Certification paraphrase only. |
| CC-04 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-05 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-06 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-07 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | License language reorganized without changing requirement. |
| CC-08 | DOES_NOT_APPLY | DOES_NOT_APPLY | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | Requirement does not apply under supplied project metadata. |
| CC-09 | APPLIES | APPLIES | FLAG | FLAG | Critical | Critical | **FULL MATCH** | draft says BABA does not apply |
| CC-10 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-11 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-12 | APPLIES | APPLIES | FLAG | FLAG | High | High | **FULL MATCH** | written follow-up changed to 30 days |
| CC-13 | APPLIES | APPLIES | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | No material deviation present. |
| CC-14 | DOES_NOT_APPLY | DOES_NOT_APPLY | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | Requirement does not apply under supplied project metadata. |
| CC-15 | DOES_NOT_APPLY | DOES_NOT_APPLY | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | Requirement does not apply under supplied project metadata. |
| CC-16 | APPLIES | APPLIES | FLAG | FLAG | Medium | Medium | **FULL MATCH** | automatic time extension |
| CC-17 | APPLIES | APPLIES | FLAG | FLAG | Medium | Medium | **FULL MATCH** | flat $10,000/day rate |
| CC-18 | DOES_NOT_APPLY | DOES_NOT_APPLY | NO_FLAG | NO_FLAG | Info | Info | **FULL MATCH** | Requirement does not apply under supplied project metadata. |

---

## Scoring against Evaluation_Criteria

| Metric | Weight | Purpose | Score | Points |
|---|---|---|---|---|
| Applicability accuracy | 20% | Correct APPLIES / DOES_NOT_APPLY decisions; penalizes over-flagging absent non-applicable clauses | **18/18 = 100%** — 14 APPLIES + 4 DOES_NOT_APPLY all correct; **0** non-applicable clauses over-flagged | 20.00 |
| Finding detection (precision + recall) | 25% | Find material deviations without unsupported flags | **TP=5, FP=0, FN=0, TN=13** → precision 100%, recall 100%, **F1 = 100%** | 25.00 |
| Cross-document precedence resolution | 20% | Select correct governing document when proposal / special provisions / Addenda conflict | **100% (self-assessed)** — see governing-document audit below | 20.00 |
| Semantic deviation discrimination | 15% | Separate material changes from equivalent/paraphrased wording | **9/9 = 100%** — every applicable-but-benign clause correctly left unflagged | 15.00 |
| Evidence and citation correctness | 15% | Draft evidence and authoritative reference must actually support the decision | **100% (self-assessed)** — see evidence audit below | 15.00 |
| Severity agreement | 5% | Reasonable agreement with challenge severity labels | **18/18 exact = 100%**; mean ordinal distance **0.000** | 5.00 |
| **TOTAL** | **100%** | | | **100.00** |

Auto-scorable metrics (65% of total weight — applicability, finding detection, semantic discrimination, severity agreement) score **65.00 / 65.00 = 100%** against the gold labels. The remaining 35% (precedence resolution, evidence correctness) is not label-encoded in `Development_Labels.csv` and is assessed below from the submission's own fields.

---

## Confusion matrix — finding detection

|  | Gold FLAG | Gold NO_FLAG |
|---|---|---|
| **Predicted FLAG** | **TP = 5** (CC-02, CC-09, CC-12, CC-16, CC-17) | FP = 0 |
| **Predicted NO_FLAG** | FN = 0 | **TN = 13** |

- **Precision 100%** — no unsupported flags raised.
- **Recall 100%** — all five planted deviations detected.
- **False-positive burden = 0**, which is the specific behavior the Info severity level and the applicability metric are designed to test.

---

## Severity agreement detail

| Severity | Gold count | Predicted count | Agreement |
|---|---|---|---|
| Critical | 1 (CC-09) | 1 (CC-09) | exact |
| High | 2 (CC-02, CC-12) | 2 (CC-02, CC-12) | exact |
| Medium | 2 (CC-16, CC-17) | 2 (CC-16, CC-17) | exact |
| Low | 0 | 0 | exact |
| Info | 13 | 13 | exact |

Mean ordinal severity distance **0.000**; maximum single-row distance **0**. No escalation of Info rows and no under-call of the Critical row.

---

## Cross-document precedence audit (20% metric — not label-encoded)

`Development_Labels.csv` carries no expected `governing_document` column, so this metric is assessed against the submission's `governing_document` field and the package's document set.

| Requirement | Governing document selected | Correct? |
|---|---|---|
| CC-01 | FHWA_1273_Contract_Provisions_Attachment | Yes — the attachment itself is what satisfies physical incorporation, not the proposal's assertion about it |
| CC-02, CC-03, CC-06, CC-07, CC-09, CC-13 | Proposal_and_General_Notices | Yes — these clauses appear only in the proposal |
| CC-04, CC-05, CC-10, CC-11, CC-12, CC-16 | General_Conditions | Yes — these clauses appear only in the General Conditions |
| CC-17 | Special_Provisions | Yes — the LD clause sits in Special Provisions, which outrank the Standard Specifications under DelDOT 105.6; flagged anyway per the CC-17 universal-flat-rate rule |
| CC-08, CC-14, CC-15, CC-18 | n/a (DOES_NOT_APPLY) | Governing document named for traceability |

Three precedence situations were correctly resolved:
1. **No addenda** — `issued_addenda: []` confirmed against the proposal's own "Issued addenda: None", so no provision was treated as superseded and no gold FLAG was suppressed on a false supersession argument.
2. **Special Provisions vs. Standard Specifications (CC-17)** — the higher-ranking document was correctly identified as controlling, and the flag was still raised on the correct basis (universal invented flat rate), matching the gold FLAG/Medium.
3. **Intra-document conflict (CC-09)** — the proposal's summary line conflicts with its own operative clause; precedence cannot resolve a single-document conflict, so metadata governed applicability. Matches the gold Critical.

**Assessed: 100%.**

## Evidence and citation audit (15% metric — not label-encoded)

All 18 rows populate `draft_location`, `draft_evidence`, `reference_id`, `reference_location` and `reference_evidence`; the schema requires evidence only for FLAG and precedence rows, so this exceeds the minimum.

Spot-check of the five FLAG rows against source text — every quotation is verbatim from the extracted PDF text:

| ID | Quoted evidence | Verified in source |
|---|---|---|
| CC-02 | "Bid security equal to five percent (5%) of the total bid price is sufficient." | Proposal p.1 — verbatim; supports gold rationale "5% bid guaranty" |
| CC-09 | "Domestic-content requirements do not apply to this project." | Proposal p.1 — verbatim; supports gold rationale "draft says BABA does not apply" |
| CC-12 | "Written follow-up documentation may be submitted within thirty (30) calendar days after the alleged change." | General Conditions p.1 — verbatim; supports gold rationale "written follow-up changed to 30 days" |
| CC-16 | "Any delay automatically extends contract time for the length of the delay without further demonstration or timely supporting notice." | General Conditions p.1 — verbatim; supports gold rationale "automatic time extension" |
| CC-17 | "A fixed rate of $10,000 per calendar day applies to every contract regardless of contract value or governing schedule." | Special Provisions p.1 — verbatim; supports gold rationale "flat $10,000/day rate" |

Each FLAG's cited reference (DelDOT 102.8, Buy America Requirement, DelDOT 104.3, DelDOT 108.7, DelDOT 108.9) is the authoritative section named in `Reference_Checklist.csv` for that requirement ID. The two gold rationales that describe benign wording — CC-03 "Certification paraphrase only." and CC-07 "License language reorganized without changing requirement." — were independently reached and cited as Info/NO_FLAG.

**Assessed: 100%.**

---

## Calibration note

Stated confidences were well ordered but conservative on the three rows that satisfy the reference by incorporation rather than restatement:

| ID | Confidence | Gold | Outcome |
|---|---|---|---|
| CC-07 | 0.72 | NO_FLAG / Info | correct — confidence understated |
| CC-10 | 0.75 | NO_FLAG / Info | correct — confidence understated |
| CC-05 | 0.78 | NO_FLAG / Info | correct — confidence understated |

All five FLAG rows carried confidence ≥ 0.90 and all five were correct; the lowest-confidence rows were also correct. No row was wrong at high confidence, and no row was right only by chance at low confidence. The residual uncertainty on CC-05, CC-07 and CC-10 came from incorporation-by-reference wording ("the reference period", "the same reference deadlines"), which the gold labels confirm is benign.

---

## Files

| File | Contents |
|---|---|
| DEV-NORTHFIELD_Label_Comparison.csv | 18-row side-by-side: expected vs. predicted applicability, label and severity, per-dimension match flags, row result, gold rationale, governing document, evidence, confidence |
| DEV-NORTHFIELD_Evaluation_Scorecard.md | This scorecard |

*Scoring reflects agreement with the supplied development labels for evaluation purposes only; it is not an approval, award, legal, compliance, or procurement determination.*
