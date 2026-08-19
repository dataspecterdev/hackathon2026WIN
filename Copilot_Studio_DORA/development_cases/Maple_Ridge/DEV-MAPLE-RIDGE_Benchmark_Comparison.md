# Benchmark Comparison — DEV-MAPLE-RIDGE

**Generated submission:** `DEV-MAPLE-RIDGE_CC_Review_Submission.csv` (18 rows)
**Gold reference:** `Development_Labels-227973d6.csv`, filtered to `Package_ID = DEV-MAPLE-RIDGE` (18 of 108 rows; the file covers 6 packages — DEV-PINE-GROVE, DEV-HARBOR-CROSSING, DEV-STONE-CREEK, DEV-NORTHFIELD, DEV-MAPLE-RIDGE, DEV-RIVERBEND)
**Scoring metrics:** `Evaluation_Criteria-1dcc3619.csv` (6 weighted metrics)
**Join:** on `requirement_id` ↔ `Requirement_ID` — 18 matched, 0 unmatched on either side.

---

## 1. Headline result

**18 / 18 rows match the gold labels on all three scored fields** (applicability, label, severity). Zero false positives, zero false negatives, zero severity disagreements.

| Field | Agreement |
|---|---|
| `applicability_decision` vs `Expected_Applicability` | 18/18 = 100% |
| `predicted_label` vs `Expected_Label` | 18/18 = 100% |
| `severity` vs `Expected_Severity` | 18/18 = 100% |

**Confusion matrix (FLAG = positive):** TP = 2, FP = 0, FN = 0, TN = 16 → precision 1.000, recall 1.000, F1 1.000.

---

## 2. Metric-by-metric scoring

| Metric (Evaluation_Criteria) | Weight | Evidence | Score |
|---|---|---|---|
| Applicability accuracy | 20% | 18/18 correct; all 6 gold `DOES_NOT_APPLY` rows (CC-01, CC-09, CC-14, CC-15, CC-16, CC-18) correctly withheld — no over-flagging of absent non-applicable clauses, which is the stated penalty condition | **1.00** |
| Finding detection (precision + recall) | 25% | Both gold findings caught (CC-08, CC-13); no unsupported flags raised. P = 1.00, R = 1.00, F1 = 1.00 | **1.00** |
| Cross-document precedence resolution | 20% | 4 precedence-bearing gold rows (CC-02, CC-04, CC-07, CC-08) all labeled correctly; governing_document set to `Addendum_A-3d7df29c.pdf` for CC-04 and CC-07 | **1.00** |
| Semantic deviation discrimination | 15% | 10 `APPLIES` + gold `NO_FLAG` rows (CC-02, CC-03, CC-04, CC-05, CC-06, CC-07, CC-10, CC-11, CC-12, CC-17) — all 10 correctly treated as equivalent/paraphrased rather than material | **1.00** |
| Evidence and citation correctness | 15% | Manual review — see §4 | **~0.97 (1 minor note)** |
| Severity agreement | 5% | 18/18, including High on CC-08 and Medium on CC-13 | **1.00** |

**Weighted total:** 0.85/0.85 on the five auto-scorable metrics (normalized **1.000**); with the evidence metric assessed manually at ~0.97, the composite is approximately **0.995**.

---

## 3. Full row-level comparison

| ID | Applicability (pred / gold) | Label (pred / gold) | Severity (pred / gold) | Match | Gold rationale |
|---|---|---|---|---|---|
| CC-01 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |
| CC-02 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | 10% requirement is preserved |
| CC-03 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | Equivalent wording |
| CC-04 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | Proposal says 75% bonds; Addendum 1 revises to 100% |
| CC-05 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | No material deviation present |
| CC-06 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | Registration paraphrased but requires pre-work compliance |
| CC-07 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | Proposal allows 60-day submission; Addendum 1 restores reference timing |
| CC-08 | APPLIES / APPLIES | **FLAG / FLAG** | **High / High** | ✅ | Proposal acknowledgment omits issued Addendum 1 |
| CC-09 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |
| CC-10 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | Hierarchy expressed with same order |
| CC-11 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | No material deviation present |
| CC-12 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | No material deviation present |
| CC-13 | APPLIES / APPLIES | **FLAG / FLAG** | **Medium / Medium** | ✅ | Record retention shortened to 1 year |
| CC-14 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |
| CC-15 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |
| CC-16 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |
| CC-17 | APPLIES / APPLIES | NO_FLAG / NO_FLAG | Info / Info | ✅ | No material deviation present |
| CC-18 | DOES_NOT_APPLY / DOES_NOT_APPLY | NO_FLAG / NO_FLAG | Info / Info | ✅ | Does not apply under supplied metadata |

---

## 4. Evidence and citation correctness — manual review

Reviewed all 18 `draft_evidence` / `reference_evidence` pairs against the source PDFs and the gold rationale.

**Reasoning agreement (not just label agreement)** on the two findings and the two precedence rows:

- **CC-08** — submitted evidence quotes *"later issued Addenda may be disregarded"*; gold rationale is *"proposal acknowledgment omits issued Addendum 1."* Same defect, same clause, same document. ✅
- **CC-13** — submitted evidence cites both the 1-year retention and the prime-only audit scope; gold rationale names the 1-year shortening. Submission is a superset and matches the Medium severity. ✅
- **CC-04** — submitted `governing_document = Addendum_A-3d7df29c.pdf`, quoting both the superseded 75% General Conditions text and the 100% replacement. Exactly mirrors the gold rationale. ✅
- **CC-07** — submitted `governing_document = Addendum_A-3d7df29c.pdf`, quoting the superseded 60-day proposal text and the Addendum replacement. Exactly mirrors the gold rationale. ✅

**One minor divergence (no label impact):**

- **CC-02** — gold rationale reads *"After Addendum correction, 10% requirement is preserved,"* implying the bid-guaranty analysis routes through an addendum. The submitted row cites the Proposal & General Notices clause directly (*"total one-tenth (10%) of the bid amount"*) and sets `governing_document = Proposal_and_General_Notices-95146a87.pdf`. Addendum A as supplied contains replacement text only for Performance and Payment Bonds and for Licenses — it says nothing about bid security — so the proposal is the correct governing document on the evidence provided. The gold rationale appears to describe a variant package or generalized template text. Label, applicability, and severity all still agree.

**Documented package-label mismatch:** the review flagged that metadata lists the addendum as "Addendum 1" while the file is titled "Addendum A". The gold rationales for CC-04, CC-07, and CC-08 refer to "Addendum 1", confirming these are the same instrument. The submission's caution was appropriate and did not cost a label.

---

## 5. Behaviors that earned the score

1. **No over-flagging on non-applicable clauses** — the 6 `DOES_NOT_APPLY` rows were driven off metadata fields (`federal_aid`, `buy_america_baba_applicable`, `subcontracting_planned`, `claim_event`, `delay_event`, `changed_work_event`) rather than treating absent clauses as omissions. This is the explicit penalty condition in the applicability metric.
2. **Precedence applied before scoring** — the 75% bond figure and the 60-day license timing were both live deviations in the base documents. Resolving Addendum A first converted two would-be High findings into correct `NO_FLAG` rows. Flagging either would have cost both the precision and precedence metrics.
3. **Cross-reference tolerance** — CC-05, CC-10, CC-12 and CC-17 state obligations by cross-reference rather than restating figures. These were correctly scored as non-deviations while being surfaced as watch items, avoiding the false-positive burden the semantic metric measures.
4. **Lowest-confidence row was still correct** — CC-12 was submitted at 0.62 confidence, the lowest in the set, and matches gold. Confidence calibration flagged genuine drafting ambiguity without producing a wrong label.

## 6. Limitations

- Only 18 of the 108 gold rows are in scope; the other 5 packages were not reviewed and are not scored here.
- `Evaluation_Criteria-1dcc3619.csv` defines metric purposes and weights but no computation formula. Applicability, finding detection, precedence, semantic discrimination and severity were computed as stated above; evidence correctness has no mechanical ground truth and was assessed by manual reading against the gold `Rationale` column.
- Scores reflect agreement with a development label set, not a contract, legal, or procurement determination.
