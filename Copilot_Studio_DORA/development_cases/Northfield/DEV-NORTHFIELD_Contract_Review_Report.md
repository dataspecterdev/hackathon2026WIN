# Contract Clause Review Report
## Package DEV-NORTHFIELD — Northfield Pavement and Traffic Systems Rehabilitation

**Review date:** 2026-08-19 (UTC)
**Criteria library:** Reference_Checklist.csv — 18 items (CC-01 through CC-18); Baseline Tier CC-01–CC-13, Advanced Tier CC-14–CC-18
**Severity taxonomy:** Severity_Guidance.csv — Critical / High / Medium / Low / Info (challenge severity only; not a legal conclusion)
**Submission schema:** Submission_Schema.csv — 15 required fields
**Document status (per metadata):** Sample material for contract review evaluation; not an executed contract or legal template.

> This report supports human review. It contains no approval, award, legal, compliance, procurement, or contract conclusion.

---

## 1. Package inventory and project metadata

| Item | Value |
|---|---|
| package_id | DEV-NORTHFIELD |
| project_title | Northfield Pavement and Traffic Systems Rehabilitation |
| federal_aid | Yes |
| buy_america_baba_applicable | Yes |
| assumed_contract_value | $1,750,000 |
| issued_addenda | None (empty list) |
| subcontracting_planned | No |
| claim_event | No |
| delay_event | Yes |
| changed_work_event | No |

**Documents reviewed (4):**

| # | Document | Pages | Clauses carried |
|---|---|---|---|
| 1 | Proposal_and_General_Notices-5f4424be.pdf | 1 | Federal requirements; Proposal guaranty; Non-collusion certification; Contractor Registration Act; Licenses; Buy America/BABA; Right to Audit |
| 2 | General_Conditions-b497cf3f.pdf | 1 | Performance/payment bonds; Contract execution & insurance; Coordination/precedence; Contract changes; Change notification; Time extensions |
| 3 | Special_Provisions-83b0013b.pdf | 1 | Liquidated damages |
| 4 | FHWA_1273_Contract_Provisions_Attachment-87ce65ff.pdf | 1 | FHWA-1273 required contract provisions attachment |

---

## 2. Executive summary

- **18 of 18** criteria evaluated. **14 APPLIES**, **4 DOES_NOT_APPLY** (CC-08, CC-14, CC-15, CC-18).
- **5 findings (FLAG)** and **13 NO_FLAG**.
- Severity distribution across all rows: **1 Critical, 2 High, 2 Medium, 13 Info**.
- **No addenda or Q&A were issued** (`issued_addenda: []`; proposal states "Issued addenda: None"), so no precedence resolution via a later addendum was available for any finding. All findings stand against the original package text.

### Findings at a glance

| Severity | ID | Requirement | Governing document | Deviation |
|---|---|---|---|---|
| **Critical** | CC-09 | Buy America / BABA applicability | Proposal_and_General_Notices | Clause states domestic-content requirements "do not apply" while metadata and the same document's summary mark BABA applicable = Yes |
| **High** | CC-02 | Proposal guaranty / bid bond | Proposal_and_General_Notices | Bid security set at **5%** of total bid price vs. required **10%** |
| **High** | CC-12 | Notification of contract changes | General_Conditions | Follow-up deadline extended **7 → 30 calendar days**; "shall" softened to "may"; immediate oral+written notice and written-direction precondition omitted |
| **Medium** | CC-16 | Extensions of contract time | General_Conditions | Automatic day-for-day extension for any delay; excusable-delay, timely-notice and critical-path tests all eliminated |
| **Medium** | CC-17 | Liquidated damages rate logic | Special_Provisions | Universal flat **$10,000 per calendar day** "regardless of contract value or governing schedule" replaces the DelDOT 108.9 schedule |

---

## 3. Findings in detail

### CC-09 — Buy America / BABA applicability — **Critical** — FLAG
- **Reference:** Reference_Checklist CC-09; General Notices "Buy America Requirement". *Apply Buy America/BABA only when project metadata/reference indicates it applies; if applicable, a clause saying it does not apply is a finding.*
- **Applicability:** APPLIES. `federal_aid: Yes` and `buy_america_baba_applicable: Yes`; the proposal's own project summary also prints "Buy America/BABA applicable — Yes".
- **Draft location:** Proposal_and_General_Notices-5f4424be.pdf, p.1, "Buy America / BABA applicability".
- **Draft evidence:** "Buy America / BABA. Domestic-content requirements do not apply to this project."
- **Analysis:** The operative clause contradicts both the project metadata and the summary table printed on the same page of the same document, and omits the certification language entirely. Because `issued_addenda` is empty there is no later governing document that could validly revise this provision, and the conflict is internal to a single document, so DelDOT 105.6 precedence cannot resolve it. This matches the Critical working definition verbatim: "Buy America explicitly marked applicable but draft says it does not apply."
- **Confidence:** 0.97
- **Recommended human action:** Escalate for human contract review; correct the clause to affirm Buy America/BABA applicability and reinstate the required certification language.

### CC-02 — Proposal guaranty / bid bond — **High** — FLAG
- **Reference:** Reference_Checklist CC-02; DelDOT 102.8. *Proposal guaranty must equal 10% of total bid price.*
- **Draft location:** Proposal_and_General_Notices-5f4424be.pdf, p.1, "Proposal guaranty / bid bond".
- **Draft evidence:** "Proposal Guaranty. Bid security equal to five percent (5%) of the total bid price is sufficient."
- **Analysis:** A required bid protection is halved. Against the assumed contract value of **$1,750,000**, the drafted 5% basis produces roughly **$87,500** of bid security where the 10% reference basis would produce roughly **$175,000** — a reduction of about **$87,500** in protection. This is the express High example ("10% bid guaranty changed to 5%").
- **Confidence:** 0.96
- **Recommended human action:** Review with DelDOT contract administration; restore the 10% guaranty or document an authorized deviation.

### CC-12 — Notification of contract changes — **High** — FLAG
- **Reference:** Reference_Checklist CC-12; DelDOT 104.3. *Immediate oral and written notice; affected work proceeds only after written direction; written follow-up information due within **7 calendar days** of the initial notice unless a later governing document validly revises the provision.*
- **Draft location:** General_Conditions-b497cf3f.pdf, p.1, "Notification of contract changes".
- **Draft evidence:** "Change Notification. Written follow-up documentation may be submitted within thirty (30) calendar days after the alleged change."
- **Analysis:** Three separable deviations compound:
  1. **Deadline:** 7 calendar days → **30 calendar days** (a 23-day extension of the documentation window).
  2. **Obligation strength:** mandatory "shall" → permissive "**may**".
  3. **Omissions:** the immediate oral-and-written notice requirement and the "proceed only after written direction" safeguard are both absent.

  The precedence check confirms no addendum revises DelDOT 104.3 for this package.
- **Confidence:** 0.93
- **Recommended human action:** Escalate for human contract review; restore the 7-calendar-day mandatory follow-up, immediate oral and written notice, and the written-direction precondition.

### CC-16 — Extensions of contract time — **Medium** — FLAG
- **Reference:** Reference_Checklist CC-16; DelDOT 108.7. *An extension requires an excusable delay, a timely written request/notice, and an effect on the critical path/substantial-completion time. Delay does not create an automatic time extension.*
- **Applicability:** APPLIES — `delay_event: Yes`.
- **Draft location:** General_Conditions-b497cf3f.pdf, p.1, "Extensions of contract time".
- **Draft evidence:** "Time Extensions. Any delay automatically extends contract time for the length of the delay without further demonstration or timely supporting notice."
- **Analysis:** The clause inverts the reference rule rather than paraphrasing it, granting an automatic day-for-day extension and expressly eliminating all three reference conditions — the excusable-delay qualification, the timely written notice/request, and the critical-path/substantial-completion impact test.
- **Confidence:** 0.92
- **Recommended human action:** Escalate for human contract review; reinstate the excusable-delay, timely-written-notice, and critical-path impact conditions.

### CC-17 — Liquidated damages schedule / rate logic — **Medium** — FLAG
- **Reference:** Reference_Checklist CC-17; DelDOT 108.9. *Use the governing Section 108.9 schedule/rate logic for the applicable contract value and time basis after resolving Addenda and precedence. A universal invented flat daily rate is a material deviation.*
- **Draft location:** Special_Provisions-83b0013b.pdf, p.1, "Liquidated damages schedule / rate logic".
- **Draft evidence:** "Liquidated Damages. A fixed rate of $10,000 per calendar day applies to every contract regardless of contract value or governing schedule."
- **Precedence note:** Under DelDOT 105.6, Special Provisions rank above the Standard Specifications, so a Special Provision would ordinarily control. The CC-17 challenge rule nevertheless treats a **universal invented flat daily rate** as a material deviation, and the clause disclaims the governing schedule and contract-value basis outright ("regardless of contract value or governing schedule"). No addendum supports the rate, and it is unscaled against the assumed contract value of **$1,750,000**.
- **Confidence:** 0.90
- **Recommended human action:** Escalate for human contract review; tie the rate to the DelDOT 108.9 schedule for the applicable contract value and time basis, or document the basis for a project-specific rate.

---

## 4. Applicable requirements with no finding (NO_FLAG / Info)

| ID | Requirement | Governing document | Basis for NO_FLAG |
|---|---|---|---|
| CC-01 | FHWA-1273 physical incorporation | FHWA_1273_Contract_Provisions_Attachment | A discrete FHWA-1273 attachment document is present in the package, not merely referenced. Proposal: "FHWA-1273 is physically included in this package as an attachment." Conf. 0.90 |
| CC-03 | Non-collusive bidding certification | Proposal_and_General_Notices | "NON-COLLUSION CERTIFICATION — The required certification is to be completed and included with the proposal." Styling differs; the DelDOT 102.15 obligation is intact. Conf. 0.88 |
| CC-04 | Performance and payment bonds | General_Conditions | "one hundred percent (100%) of the contract price, subject to the referenced surety conditions" — matches the DelDOT 103.5 challenge baseline exactly. Conf. 0.95 |
| CC-05 | Contract execution and proof of insurance | General_Conditions | Both obligations retained by express incorporation of "the reference period" (20 calendar days after notice of award) plus proof of insurance before execution; no deadline substituted or omitted. Conf. 0.78 |
| CC-06 | Contractor Registration Act notice | Proposal_and_General_Notices | Registration required "before beginning covered field work" — does not permit registration only after work begins (19 Del. C. § 3604). Conf. 0.92 |
| CC-07 | Delaware business / subcontractor licenses | Proposal_and_General_Notices | Clause is reorganized but states licensing evidence "remains due within the same reference deadlines" — the 30-day and 10-day/20-day timing under 29 Del. C. § 6967 is preserved, not shortened. Conf. 0.72 |
| CC-10 | Coordination / order of precedence | General_Conditions | Documents declared complementary; conflicts resolved by the incorporated order of precedence. No reordering of the DelDOT 105.6 hierarchy. Conf. 0.75 |
| CC-11 | Contract changes must follow written process | General_Conditions | "Scope, price, or time changes require the documented written process; oral direction alone does not modify the contract" — substantively identical to DelDOT 104.2. Conf. 0.94 |
| CC-13 | Right to audit and record retention | Proposal_and_General_Notices | Audit availability preserved and records "retained for three (3) years after final payment" — matches the reference retention period exactly; not shortened. Conf. 0.95 |

**Verification points flagged for human confirmation (not findings):** CC-05, CC-07 and CC-10 each satisfy the reference by *incorporating* it ("the reference period", "the same reference deadlines", "the order of precedence supplied in the applicable contract documents") rather than restating the explicit figures. These carry the three lowest confidence scores in the set (0.78 / 0.72 / 0.75). Restating the explicit 20-day period, the 30-day and 10-day/20-day license timing, and the DelDOT 105.6 seven-level sequence would remove the ambiguity.

---

## 5. Requirements determined not applicable

| ID | Requirement | Applicability rule | Reason for DOES_NOT_APPLY |
|---|---|---|---|
| CC-08 | Addenda and Q&A currency | Project has posted addenda and/or Q&A | `issued_addenda: []`; proposal prints "Issued addenda: None". No addenda or Q&A exist to reconcile. Conf. 0.94 |
| CC-14 | Contract subletting (DelDOT 108.1) | Contract uses subcontractors | `subcontracting_planned: No`. Absence of the 50% self-performance / written-consent clause is therefore not scored as a missing-clause finding. Conf. 0.80 |
| CC-15 | Claims procedure (DelDOT 105.15) | Unresolved contract-change/claim scenario | `claim_event: No`. Conf. 0.80 |
| CC-18 | Compensation for changes (DelDOT 109.4) | Changed-work pricing scenario | `changed_work_event: No`. Conf. 0.80 |

Per the review method, absent clauses are **not** flagged where the applicability precondition is not met.

**Conditional dependencies to monitor:** DelDOT 105.15 (CC-15) depends on Section 104.3 notice compliance — the CC-12 finding weakens exactly that notice process, so if a claim event later arises the CC-12 deviation becomes material to CC-15. Re-run CC-14 if subcontracting is later proposed, CC-18 if changed work is directed, and CC-08 if any addendum or Q&A is issued before bid opening.

---

## 6. Precedence resolution log

| Step | Result |
|---|---|
| Later addenda / Q&A | **None issued** (`issued_addenda: []`; proposal "Issued addenda: None"). No provision in this package is superseded by an addendum. |
| Special Provisions vs. Standard Specifications | Engaged at CC-17 only. Special Provisions outrank the Standard Specifications under DelDOT 105.6, but the CC-17 challenge rule treats a universal invented flat daily rate as a material deviation regardless of placement. Flagged. |
| Intra-document conflict | CC-09: the proposal's project summary ("Buy America/BABA applicable — Yes") conflicts with its own operative clause ("do not apply"). Precedence cannot resolve a conflict internal to one document; project metadata controls the applicability determination. |
| Metadata as applicability control | Governed CC-08, CC-09, CC-14, CC-15, CC-16, CC-18. |

**DelDOT 105.6 order of precedence applied:** General Description > General Notices > Plans > Special Provisions > Standard Construction Details > Standard Specifications > Electronic Design Data Files.

---

## 7. Severity summary

| Severity | Count | Requirement IDs | Guidance note |
|---|---|---|---|
| Critical | 1 | CC-09 | Challenge severity only; not a legal conclusion |
| High | 2 | CC-02, CC-12 | Requires human contract review |
| Medium | 2 | CC-16, CC-17 | Requires human contract review |
| Low | 0 | — | May be used sparingly |
| Info | 13 | CC-01, CC-03, CC-04, CC-05, CC-06, CC-07, CC-08, CC-10, CC-11, CC-13, CC-14, CC-15, CC-18 | Do not escalate |

**By document:** Proposal_and_General_Notices — 2 findings (CC-09 Critical, CC-02 High). General_Conditions — 2 findings (CC-12 High, CC-16 Medium). Special_Provisions — 1 finding (CC-17 Medium). FHWA-1273 attachment — 0 findings.

---

## 8. Deliverables

| File | Contents |
|---|---|
| DEV-NORTHFIELD_CC_Review_Submission.csv | 18 rows (one per CC requirement), 15 columns in Submission_Schema.csv field order; all required fields populated |
| DEV-NORTHFIELD_Contract_Review_Report.md | This narrative review report |

---

*Prepared to support human contract review. Challenge severity labels are taken verbatim from Severity_Guidance.csv and carry no legal, compliance, procurement, or award determination.*
