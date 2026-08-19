## Worked examples

These four rows show the shape of a correct judgement. Each covers a different way a
requirement resolves. Follow the reasoning pattern, not the specific values — the
requirement, the project, and the invariant change every time.

---

### Example 1 — out of scope, decided before any clause is read

Project metadata alone settles this. No contract text is read, no clause is cited, and no
finding is possible.

```
document_id              DEV-PINE-GROVE
requirement_id           CC-09
applicability_decision   DOES_NOT_APPLY
applicability_reason     Project metadata reports buy_america_baba_applicable=No, so
                         Buy America/BABA is outside scope for this package.
predicted_label          NO_FLAG
severity                 Info
governing_document       Not applicable
draft_location           (empty)
draft_evidence           (empty)
reference_id             CC-09
reference_location       Federal-aid DelDOT proposal General Notices - Buy America Requirement
reference_evidence       Apply Buy America/BABA only when project metadata/reference
                         indicates it applies; if applicable, a clause saying it does not
                         apply is a finding.
explanation              Buy America / BABA applicability is outside the scope of this
                         package. Project metadata reports buy_america_baba_applicable=No.
                         No deviation review is performed and no finding is raised.
confidence               0.97
recommended_human_action No action required; retain as reviewed with no finding.
```

**Why:** the applicability gate runs first and short-circuits. `draft_location` and
`draft_evidence` are empty *because nothing was read* — never fill them in for an
out-of-scope row. A requirement that does not apply cannot produce a finding no matter what
the documents say.

---

### Example 2 — an Addendum supersedes the base document

The General Conditions set bond coverage at 75%. Addendum B replaces that provision with
100%. Precedence is resolved **before** the invariant is tested, so the superseded 75% text
is never judged.

```
document_id              DEV-HARBOR-CROSSING
requirement_id           CC-04
applicability_decision   APPLIES
applicability_reason     Contract execution package governed by Section 103.5; performance
                         and payment bonds apply.
predicted_label          NO_FLAG
severity                 Info
governing_document       Addendum B (Addendum_B.pdf)
draft_location           Addendum_B.pdf > Performance and payment bonds (page 1)
draft_evidence           Required bond coverage shall equal one hundred percent (100%) of
                         the contract price, subject to the referenced surety conditions.
reference_id             CC-04
reference_location       DelDOT Standard Specifications - DelDOT 103.5
reference_evidence       For challenge scoring, required performance and payment bond
                         coverage is 100% of the contract price, subject to the referenced
                         surety conditions. Resolve any later governing Addendum before
                         flagging earlier text.
explanation              Bond coverage equals 100% of the contract price, subject to the
                         referenced surety conditions, matching DelDOT 103.5. Addendum B
                         explicitly revises this named provision with replacement text and
                         therefore governs over the earlier General Conditions text.
confidence               0.93
recommended_human_action Confirm superseding document controls before accepting; no
                         separate action.
```

**Why:** the Addendum carries `Revision to Performance and payment bonds` followed by
`REPLACEMENT TEXT:`, so it governs. Evidence is quoted from the Addendum — the document
that actually controls — not from the General Conditions. Flagging the 75% text would
report a problem the owner has already fixed. Note the distinct recommended action: no
finding, but the reviewer is told to confirm the superseding document controls.

---

### Example 3 — equivalent wording is not a deviation

The reference says three years. The draft says 36 months. Same requirement, different
units.

```
document_id              DEV-HARBOR-CROSSING
requirement_id           CC-13
applicability_decision   APPLIES
applicability_reason     Contract and subcontract performance records exist, so audit
                         rights and retention apply.
predicted_label          NO_FLAG
severity                 Info
governing_document       Proposal and General Notices (Proposal_and_General_Notices.pdf)
draft_location           Proposal_and_General_Notices.pdf > Right to audit and record
                         retention (page 1)
draft_evidence           Prime and subcontract performance records remain reviewable and
                         are retained for 36 months following final payment.
reference_id             CC-13
reference_location       DelDOT proposal General Notices - Right to Audit
reference_evidence       For challenge scoring, relevant prime-contractor and subcontractor
                         records supporting contract performance must be available for
                         audit and retained for three years after final payment.
explanation              Prime and subcontract records remain subject to audit and the
                         retention period is at least three years after final payment.
                         Expressing the period as 36 months is equivalent.
confidence               0.93
recommended_human_action No action required; retain as reviewed with no finding.
```

**Why:** normalise the invariant before comparing — 36 months *is* three years. The same
applies to `one-tenth (10%)` versus `ten percent (10%)`, to reordered or reworded
provisions that keep the obligation, and to clauses that defer to the reference ("within
the reference period"). Wording difference is not deviation. The explanation names the
equivalence explicitly so a reviewer can check the reasoning rather than trust it.

---

### Example 4 — a Critical finding

Metadata says Buy America applies. The draft says it does not. The clause contradicts a
stated applicability rule.

```
document_id              DEV-HARBOR-CROSSING
requirement_id           CC-09
applicability_decision   APPLIES
applicability_reason     Project metadata reports buy_america_baba_applicable=Yes.
predicted_label          FLAG
severity                 Critical
governing_document       Proposal and General Notices (Proposal_and_General_Notices.pdf)
draft_location           Proposal_and_General_Notices.pdf > Buy America / BABA
                         applicability (page 1)
draft_evidence           Domestic-content requirements do not apply to this project.
reference_id             CC-09
reference_location       Federal-aid DelDOT proposal General Notices - Buy America Requirement
reference_evidence       Apply Buy America/BABA only when project metadata/reference
                         indicates it applies; if applicable, a clause saying it does not
                         apply is a finding.
explanation              Project metadata marks this federal-aid project as subject to Buy
                         America/BABA, but the draft states that domestic-content
                         requirements do not apply. The clause directly contradicts a
                         stated applicability rule.
confidence               0.95
recommended_human_action Escalate for priority contract review before award/execution.
```

**Why:** the evidence is one short verbatim sentence — the *specific* span that creates the
problem, not the whole section. Severity comes from the checklist's guidance (a contradicted
mandatory applicability rule is Critical), not from a sense of how serious it feels. The
explanation states the metadata fact, the clause text, and the contradiction between them,
in that order, in two sentences.

---

**Across all four:** every row names a governing document and says why it governs; evidence
is verbatim or deliberately empty; the explanation compares the invariant to the clause
rather than describing the clause; and the recommended action follows from label and
severity, not from judgement. If a row you write cannot answer *which document governs and
why*, *what exact text you judged*, and *which stated rule it violates*, it is not finished.
