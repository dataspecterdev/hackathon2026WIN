# Contract Clause Review Report — DEV-MAPLE-RIDGE

**Project:** Maple Ridge Maintenance Services
**Package ID / document_id:** DEV-MAPLE-RIDGE
**Review date:** 2026-08-19 (UTC)
**Criteria library:** Reference_Checklist.csv — 18 requirements (CC-01 … CC-18)
**Severity taxonomy:** Severity_Guidance.csv (Critical / High / Medium / Low / Info) — challenge severity only, not a legal conclusion
**Submission schema:** Submission_Schema.csv (15 required fields)

> This report supports human review. It contains no approval, award, legal, compliance, or procurement conclusion.

---

## 1. Package inventory and project metadata

| Item | Value | Source |
|---|---|---|
| package_id | DEV-MAPLE-RIDGE | Project_Metadata-c0bb3bae.json |
| project_title | Maple Ridge Maintenance Services | Project_Metadata-c0bb3bae.json |
| federal_aid | No | Project_Metadata-c0bb3bae.json; Proposal p.1 "Federal aid: No" |
| buy_america_baba_applicable | No | Project_Metadata-c0bb3bae.json; Proposal p.1 |
| assumed_contract_value | $650,000 | Project_Metadata-c0bb3bae.json; Proposal p.1 |
| issued_addenda | Addendum 1 | Project_Metadata-c0bb3bae.json |
| subcontracting_planned | No | Project_Metadata-c0bb3bae.json |
| claim_event / delay_event / changed_work_event | No / No / No | Project_Metadata-c0bb3bae.json |
| document_status | Sample material for contract review evaluation; not an executed contract or legal template | Project_Metadata-c0bb3bae.json |

**Documents reviewed (4 PDFs, 1 page each, + metadata JSON):**

1. `Proposal_and_General_Notices-95146a87.pdf` — bid security, non-collusion, contractor registration, licenses, addenda acknowledgment, right to audit
2. `General_Conditions-85f498f3.pdf` — performance/payment bonds, execution & insurance, document coordination, contract changes, change notification
3. `Special_Provisions-d08f0728.pdf` — liquidated damages
4. `Addendum_A-3d7df29c.pdf` — replacement text for Performance and Payment Bonds, and for Delaware business / subcontractor licenses

No Q&A record was supplied with this package.

---

## 2. Precedence resolution applied

Order of precedence used (CC-10 / DelDOT 105.6): **General Description > General Notices > Plans > Special Provisions > Standard Construction Details > Standard Specifications > Electronic Design Data Files**, with the overriding rule that *a later Addendum that expressly revises a named provision governs that revised provision.*

| Provision | Earlier text | Controlling text | Effect |
|---|---|---|---|
| Performance and payment bonds (CC-04) | General Conditions: "Bond coverage equal to **seventy-five percent (75%)** of the contract price is sufficient." | **Addendum A** REPLACEMENT TEXT: "Required bond coverage shall equal **one hundred percent (100%)** of the contract price, subject to the referenced surety conditions." | Deviation **cured**; matches the 100% benchmark. Not flagged. |
| Delaware business / subcontractor licenses (CC-07) | Proposal: "Bidder license evidence is **not required** with the proposal; subcontractor license copies may be provided **sixty (60) days** after engagement." | **Addendum A** REPLACEMENT TEXT: license evidence "shall be furnished within the reference timing stated in the applicable contract documents." | Conflicting 60-day text **superseded**; controlling text defers to reference timing (30 days / 10 days after a >20-day hire). Not flagged; cross-reference precision should be confirmed. |

**Addendum identity note:** metadata lists the issued addendum as "Addendum 1"; the supplied file is titled "Addendum A". These are treated as the same single issued addendum. Confirm the label match before conforming the contract.

---

## 3. Findings (2 flagged)

### FINDING 1 — CC-08 Addenda and Q&A currency — **High**

- **Governing document:** `Proposal_and_General_Notices-95146a87.pdf`, p.1, "Addenda and Q&A currency" — *Addenda Acknowledgment*
- **Draft evidence:** "Only the Addenda expressly listed in the original proposal need be acknowledged; **later issued Addenda may be disregarded**."
- **Reference (CC-08, Attachments / Addenda):** Use the latest provided Addendum/package version; the package must not treat the original proposal as self-updating. A draft that ignores a later issued Addendum is a finding.
- **Why material:** The clause affirmatively permits bidders to disregard later-issued addenda. It is also internally inconsistent with this package: Addendum A issues later replacement text for the bond percentage (CC-04) and the license timing (CC-07). Applied literally, the controlling 100% bond coverage and revised license timing could be treated as optional — re-opening the 75% and 60-day defects that precedence otherwise cured.
- **Precedence check:** No addendum, special provision, or metadata field revises this clause, so the deviation is not cured.
- **Severity rationale (High):** A material required bid workflow/protection is substantially weakened.
- **Confidence:** 0.94
- **Recommended human action:** Strike or replace the "later issued Addenda may be disregarded" language; require acknowledgment of all issued addenda, including Addendum A, prior to bid.

### FINDING 2 — CC-13 Right to audit and record retention — **Medium**

- **Governing document:** `Proposal_and_General_Notices-95146a87.pdf`, p.1, "Right to audit and record retention" — *Right to Audit*
- **Draft evidence:** "**Only prime-contractor records** are subject to audit and records need be retained for **one (1) year** after final payment."
- **Reference (CC-13, Right to Audit):** Relevant **prime-contractor and subcontractor** records supporting contract performance must be available for audit and retained for **three years after final payment**.
- **Why material — two deviations in one clause:**
  1. **Scope narrowed** — subcontractor records removed from audit reach.
  2. **Retention shortened** — three years reduced to one (1) year after final payment (a two-year reduction).
- **Precedence check:** Not revised by Addendum A, Special Provisions, or metadata.
- **Severity rationale (Medium):** Record-retention deviation requiring review, per the Severity_Guidance example "audit retention shortened".
- **Confidence:** 0.92
- **Recommended human action:** Restore audit coverage of subcontractor records and the three-year post-final-payment retention period.

---

## 4. Watch items — not flagged, confirm during conforming

These scored **NO_FLAG** because they defer to the reference rather than contradict it, but they state obligations by cross-reference instead of restating the controlling figures.

| ID | Requirement | Cross-reference used | Figures that should be confirmed |
|---|---|---|---|
| CC-05 | Contract execution and proof of insurance | "within the reference period" | **20 calendar days** after notice of award; proof/certificate of insurance **before** contract execution |
| CC-07 | Delaware business / subcontractor licenses (as revised by Addendum A) | "within the reference timing stated in the applicable contract documents" | Prime license **accompanies the proposal**; subcontractor copies within **30 days** after contract entry, or within **10 days** after a subcontractor is hired more than **20 days** after contract entry |
| CC-10 | Coordination / order of precedence | "the same priority sequence listed in the applicable contract documents" | The DelDOT 105.6 seven-tier order (see §2) |
| CC-12 | Notification of contract changes | "the reference follow-up documentation within the stated period" | **Immediate oral and written** notice; work proceeds **only after written direction**; written follow-up within **7 calendar days** of initial notice |
| CC-14 | Contract subletting (DOES_NOT_APPLY) | metadata `subcontracting_planned = No` | If any work is sublet, re-run CC-14: prime self-performs **no less than 50%** of total original contract price, written consent required |
| CC-17 | Liquidated damages | "the governing contract/reference schedule" | Confirm the DelDOT 108.9 schedule row for the **$650,000** assumed value and the stated time basis |

---

## 5. Criteria matrix — all 18 requirements

| ID | Requirement | Applicability | Label | Severity | Governing document | Conf. |
|---|---|---|---|---|---|---|
| CC-01 | FHWA-1273 physical incorporation | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (federal_aid = No) | 0.95 |
| CC-02 | Proposal guaranty / bid bond | APPLIES | NO_FLAG | Info | Proposal & General Notices | 0.93 |
| CC-03 | Non-collusive bidding certification | APPLIES | NO_FLAG | Info | Proposal & General Notices | 0.92 |
| CC-04 | Performance and payment bonds | APPLIES | NO_FLAG | Info | **Addendum A** (supersedes GC 75%) | 0.88 |
| CC-05 | Contract execution / proof of insurance | APPLIES | NO_FLAG | Info | General Conditions | 0.78 |
| CC-06 | Contractor Registration Act notice | APPLIES | NO_FLAG | Info | Proposal & General Notices | 0.90 |
| CC-07 | Delaware business / subcontractor licenses | APPLIES | NO_FLAG | Info | **Addendum A** (supersedes 60-day text) | 0.72 |
| CC-08 | Addenda and Q&A currency | APPLIES | **FLAG** | **High** | Proposal & General Notices | 0.94 |
| CC-09 | Buy America / BABA applicability | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (BABA = No) | 0.95 |
| CC-10 | Coordination / order of precedence | APPLIES | NO_FLAG | Info | General Conditions | 0.75 |
| CC-11 | Contract changes — written process | APPLIES | NO_FLAG | Info | General Conditions | 0.93 |
| CC-12 | Notification of contract changes | APPLIES | NO_FLAG | Info | General Conditions | 0.62 |
| CC-13 | Right to audit and record retention | APPLIES | **FLAG** | **Medium** | Proposal & General Notices | 0.92 |
| CC-14 | Contract subletting | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (subcontracting = No) | 0.70 |
| CC-15 | Claims procedure | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (claim_event = No) | 0.90 |
| CC-16 | Extensions of contract time | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (delay_event = No) | 0.90 |
| CC-17 | Liquidated damages schedule / rate logic | APPLIES | NO_FLAG | Info | Special Provisions | 0.88 |
| CC-18 | Compensation for changes | DOES_NOT_APPLY | NO_FLAG | Info | Project_Metadata (changed_work = No) | 0.85 |

---

## 6. Severity summary

| Severity | Count | Requirement IDs |
|---|---|---|
| Critical | 0 | — |
| High | 1 | CC-08 |
| Medium | 1 | CC-13 |
| Low | 0 | — |
| Info | 16 | CC-01 … CC-07, CC-09 … CC-12, CC-14 … CC-18 |
| **Total rows** | **18** | |

| Disposition | Count |
|---|---|
| APPLIES | 12 |
| DOES_NOT_APPLY | 6 |
| FLAG | 2 |
| NO_FLAG | 16 |
| Deviations cured by Addendum A precedence | 2 (CC-04, CC-07) |

---

## 7. Submission file

`DEV-MAPLE-RIDGE_CC_Review_Submission.csv` — 18 rows (one per document × requirement pair), columns exactly per Submission_Schema.csv:
`document_id, requirement_id, applicability_decision, applicability_reason, predicted_label, severity, governing_document, draft_location, draft_evidence, reference_id, reference_location, reference_evidence, explanation, confidence, recommended_human_action`

---

## 8. Reviewer notes / limitations

- No Q&A record was provided; CC-08 applicability was established from posted addenda alone.
- Each supplied PDF is a single page of excerpted clause text, not a full contract; findings are limited to the clause text present.
- Metadata records the addendum as "Addendum 1" while the file is titled "Addendum A" — confirm they are the same instrument before relying on the CC-04 and CC-07 precedence resolutions.
- All severity labels are challenge-taxonomy signals for human review, not legal or compliance determinations.
