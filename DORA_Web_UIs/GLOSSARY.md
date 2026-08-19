# Glossary

Every term that appears in the code, the CSVs, or the contract documents, in one
place. Two halves: **contract vocabulary** (words that come from the documents
and the law) and **project vocabulary** (words this codebase invented).

> These are working definitions for reading the code and the outputs. They are
> not legal definitions, and nothing here is a legal conclusion — see
> `recommended_human_action` on every row.

Related: [`README.md`](./README.md) (what and how) ·
[`ONBOARDING.md`](./ONBOARDING.md) (where to edit) ·
[`SOLUTION.md`](./SOLUTION.md) (why)

---

## 1. Contract and regulatory vocabulary

### Documents and who wrote them

| Term | Meaning |
|---|---|
| **DelDOT** | Delaware Department of Transportation. Owner of the *Standard Specifications* this project checks contracts against. |
| **FHWA** | Federal Highway Administration. The federal agency whose requirements attach when a project takes federal money. |
| **FHWA-1273** | "Required Contract Provisions for Federal-Aid Construction Contracts" — a standard federal form. On a federal-aid project it must be **physically included** in the package, not merely referenced. That distinction is the whole of CC-01. |
| **Del. C.** | *Delaware Code*. `19 Del. C. § 3604` = Title 19, section 3604. Cited by CC-06 and CC-07. |
| **Solicitation** | The published invitation to bid, and everything issued with it. |
| **Contract package** | One complete solicitation: the PDFs, plus `Document_Index.csv` and `Project_Metadata.json`. The unit of analysis here — `document_id` is always a *package* ID, never a single PDF. |

### The document types inside a package

Listed in DelDOT 105.6 **order of precedence**, highest authority first. When two
documents conflict, the higher one wins.

| Rank | Document type | What it is |
|---|---|---|
| 1 | **General Description** | Narrative scope of the project. |
| 2 | **General Notices** | Project-specific notices bound with the proposal (often `Proposal_and_General_Notices.pdf`). |
| 3 | **Plans** | Drawings. |
| 4 | **Special Provisions** | Clauses written for *this* project; override the boilerplate below them. |
| 5 | **Standard Construction Details** | Standard drawings. |
| 6 | **Standard Specifications** | DelDOT's statewide boilerplate — the "default" contract terms. |
| 7 | **Electronic Design Data Files** | CAD / design data. |

**General Conditions** — a document type these packages use that has no exact
slot in the ladder above. This codebase maps it to the *Standard Specifications*
rank (6). Flagged as an approximation in SOLUTION.md § Limitations.

### Addenda

| Term | Meaning |
|---|---|
| **Addendum** (pl. **addenda**) | A document issued *after* the solicitation goes out that changes it. Later addenda beat earlier ones and beat the base documents. |
| **Revision to \<X\>** | The heading form an addendum uses to name the provision it is changing. |
| **REPLACEMENT TEXT:** | The marker after that heading introducing the new wording. Both the heading form and this marker must be present for the codebase to treat an addendum as validly superseding. |
| **Addendum ordinal** | Issue order. `Addendum_A` → 1, `_B` → 2, `_C` → 3. Highest ordinal governs. |
| **Addenda currency** | Whether the draft reflects the *latest* addendum. Ignoring a later addendum is a finding (CC-08). |

### Bidding and award

| Term | Meaning |
|---|---|
| **Proposal guaranty / bid bond / bid security** | Money or a bond a bidder posts to guarantee they'll sign the contract if they win. DelDOT requires **10% of the total bid price** (CC-02). |
| **Non-collusive bidding certification** | A signed statement that the bidder didn't rig the bid with competitors (CC-03). |
| **Notice of award** | The owner telling the winning bidder they won. Starts the 20-calendar-day execution clock in CC-05. |
| **Contract execution** | Signing the contract and returning the required documents. |
| **Performance bond** | A surety bond guaranteeing the contractor completes the work. Required at **100% of contract price** (CC-04). |
| **Payment bond** | A surety bond guaranteeing subcontractors and suppliers get paid. Also 100% (CC-04). |
| **Surety** | The third party (usually an insurer) that backs a bond. |
| **Proof / certificate of insurance** | Evidence the contractor carries required insurance; due **before** execution (CC-05). |

### Performing the work

| Term | Meaning |
|---|---|
| **Prime contractor** | The party holding the contract with DelDOT. |
| **Subcontractor** | A party the prime hires to do part of the work. |
| **Subletting** | Subcontracting out portions of the work. DelDOT 108.1 requires the prime to self-perform **no less than 50%** of the original contract price and to get **written consent** to sublet (CC-14). |
| **Specialty items** | Work excluded from that 50% calculation, as designated by the reference. |
| **Public works** | Government-funded construction. Triggers Delaware licensing rules (CC-07). |
| **Contractor Registration Act** | Delaware law requiring contractors to register **before** work begins — registering afterward is a finding (CC-06). |
| **Right to audit / record retention** | The owner's right to inspect contract records, which must be kept **three years after final payment** (CC-13). |

### Changes, delays, and money

| Term | Meaning |
|---|---|
| **Changed work / change order** | Work added, removed, or altered after the contract is signed. |
| **Written change process** | Changes must be documented in writing; **oral direction alone must not immediately alter scope, price, or time** (CC-11). This is the single most-often-violated provision in the dataset. |
| **Notice of change** | The contractor's obligation to give immediate oral *and* written notice of an alleged change, with written follow-up due **within 7 calendar days** (CC-12). |
| **Claim** | A formal demand for extra money or time. Written claim due **within 30 calendar days** after the work described in the notice of intent is complete (CC-15). |
| **Notice of intent** | The advance warning that a claim is coming. |
| **Excusable delay** | A delay not the contractor's fault, which can justify more time. |
| **Critical path** | The chain of tasks that determines the project's finish date. A delay only earns a time extension if it hits the critical path (CC-16). |
| **Substantial completion** | The point where the work is usable for its intended purpose. |
| **Time extension** | More contract time. **Never automatic** — requires an excusable delay, timely written request, and critical-path effect (CC-16). |
| **Liquidated damages** | A pre-agreed daily amount the contractor owes for finishing late. DelDOT 108.9 sets a *schedule* that varies by contract value and time basis; a single invented flat daily rate is a material deviation (CC-17). |
| **Unit price** | A pre-agreed price per unit of work in the contract. First choice for pricing changed work. |
| **Negotiated price** | An agreed price when no unit price applies. Second choice. |
| **Force account** | Cost-plus pricing (actual labour, equipment, materials) used when the parties can't agree. Last resort. The required CC-18 sequence is **unit price → negotiated → force account**; a fixed arbitrary markup that replaces this workflow is a material deviation. |
| **Buy America / BABA** | Federal domestic-sourcing rules (*Build America, Buy America Act*). Applies only when the project metadata says it does — and when it applies, a clause saying it *doesn't* is a finding (CC-09). |
| **Federal-aid project** | A project receiving federal highway funds. Triggers FHWA-1273 (CC-01) and, where indicated, BABA (CC-09). |

---

## 2. Project vocabulary

Words this codebase uses in a specific way.

### The data

| Term | Code | Meaning |
|---|---|---|
| **Requirement** | `Requirement` | One row of `Reference_Checklist.csv` — one thing to check, `CC-01` … `CC-18`. |
| **Checklist** | `ReferenceChecklist` | All 18 requirements, plus the heading→requirement lookup. The **scoring authority**: when the checklist and a contract document disagree, the checklist is right by definition. |
| **Clause** | `Clause` | A heading-anchored block of text lifted out of one PDF: file, doc type, heading, body, page. The atomic unit everything compares against. |
| **Package** | `Package` | One contract package: metadata + document index + all its parsed clauses. |
| **Split** | — | `Development/` (has labels, used for scoring) or `Validation/` (no labels, produces the deliverable). |
| **Verdict** | `Verdict` | A detector's raw output: label, explanation, confidence, `rule_id`, evidence, `uncertain`. |
| **Finding** | `Finding` | One finished submission row. |
| **Grain** | — | The shape of the output: **one row per package × requirement**, always. 8 packages × 18 requirements = 144 rows total. No row is ever omitted, including not-applicable ones. |

### The pipeline stages

| Term | Meaning |
|---|---|
| **Ingest** | PDF → clauses. Splits on **known headings**, not token windows. |
| **Heading resolution** | Matching a document heading to a requirement ID by normalised string match. This is what replaces vector retrieval — 137/137 clauses resolve. |
| **Alias** | An entry in `HEADING_ALIASES` for a heading that doesn't literally repeat the requirement name (e.g. `"federal requirements"` → CC-01). |
| **Normalise** | Fold case, strip punctuation, collapse whitespace — so `"Addenda and Q&A; currency"` matches `"Addenda and Q&A currency"`. |
| **Applicability gate** | Layer 1. Decides `APPLIES` / `DOES_NOT_APPLY` from project metadata **before any clause is read**, so an out-of-scope requirement structurally cannot produce a flag. |
| **Precedence resolution** | Layer 2. Picks the one clause that governs, out of possibly several addressing the same requirement. |
| **Governing document / governing clause** | The winner of that resolution — the text that actually controls. |
| **Superseded** | A clause that addresses the requirement but lost to a higher-authority document or a later addendum. Still reported (in the explanation), never tested. |
| **Invariant** | The checkable core of a requirement: a number, a deadline, a retention period, or a modal obligation. `10%`, `20 calendar days`, `three years`, `written consent required`. |
| **Detector** | Layer 3. One hand-written function per requirement that tests that invariant against the governing clause. |
| **Deferral** | Clause language that hands the substance back to the reference — "within the reference period", "as stated in the applicable contract documents". **Preserves** the requirement; not a finding. |
| **Material vs benign** | *Material* = the invariant changed (different number, removed protection, reversed order, inverted applicability, replaced workflow). *Benign* = wording changed but the invariant didn't. Only material differences are flagged. |
| **Adjudication** | Layer 4. The LLM call, made **only** when a detector returns `uncertain=True`, and only about the one clause precedence already selected. |
| **Null provider** | The default LLM provider: makes no network call and keeps the rule verdict. `--llm null` is the default, so nothing hits the network unless you ask. |
| **Fall-through path** | A detector branch that returns a default because nothing matched (`unclear`, `no_value`, `missing`). A verdict resting on one of these is right by luck, not by evidence — the robustness suite treats it as a failure. |

### Provenance and outputs

| Term | Meaning |
|---|---|
| **Submission CSV** | `out/submission_*.csv` — the 15 schema fields in schema order. The deliverable. |
| **Audit CSV** | `out/audit_*.csv` — the same rows plus `decided_by` and `rule_id`. For humans, not for submission. |
| **`rule_id`** | Which branch of which detector fired, e.g. `CC02.wrong_percent`. The trace back from any row to the exact line of code. |
| **`decided_by`** | Which layer settled the row: `applicability`, `rule`, or `llm`. |
| **Evidence grounding** | The guarantee that `draft_evidence` is a **verbatim substring** of the document named in `governing_document`. Machine-checked, not eyeballed. |
| **Conformance** | `crf/conformance.py` — 11 machine checks that the submission CSV honours the schema contract. Has zero internal imports so a shared bug can't fool it. |

### The robustness suite

| Term | Meaning |
|---|---|
| **Perturbation** | A deliberate mutation of a package whose correct answer is known **by construction** — so it needs no labels. |
| **Baseline** | The unperturbed run the perturbed run is compared against. |
| **Invariance case** | Meaning preserved → **no** decision may move. |
| **Directional case** | Meaning changed → **one named** requirement must move to a stated label, and nothing else may. |
| **Collateral damage** | An untargeted requirement that changed anyway — the signal that a detector is reading text belonging to a different requirement. |

---

## 3. Enumerated values

Every constrained field, and its complete set of legal values.

| Field | Values |
|---|---|
| `applicability_decision` | `APPLIES` · `DOES_NOT_APPLY` |
| `predicted_label` | `FLAG` · `NO_FLAG` — every `DOES_NOT_APPLY` row **must** be `NO_FLAG` |
| `severity` | `Critical` · `High` · `Medium` · `Low` · `Info` — challenge taxonomy only. Looked up from the checklist, never decided by a detector. `Info` on every non-FLAG row. |
| `confidence` | `0.00`–`1.00`, two decimals |
| `decided_by` *(audit only)* | `applicability` · `rule` · `llm` |

**`recommended_human_action`** — four fixed strings:

| When | Text |
|---|---|
| FLAG, Critical or High | *Escalate for priority contract review before award/execution.* |
| FLAG, other severity | *Route to contract reviewer for confirmation; human decision required.* |
| No flag, but something was superseded | *Confirm superseding document controls before accepting; no separate action.* |
| No flag, nothing superseded | *No action required; retain as reviewed with no finding.* |

**Robustness failure codes** — printed by `run.py robustness`:

| Code | Meaning |
|---|---|
| `TARGET` | The perturbed requirement did not reach the expected decision. |
| `DRIFT` | An **untargeted** requirement changed decision. Usually more serious than `TARGET` — a detector is reading someone else's text. |
| `GOVERN` | Precedence picked the wrong governing document. |
| `DEGRADE` | The decision survived but stopped resting on positive evidence — right answer, dead reasoning. |

---

## 4. The 18 requirements

| ID | Name | Authority | Severity | The invariant in one line |
|---|---|---|---|---|
| CC-01 | FHWA-1273 physical incorporation | FHWA-1273 I.1 | Critical | On federal-aid work the form must be **physically in the package**; a reference is not enough. |
| CC-02 | Proposal guaranty / bid bond | DelDOT 102.8 | High | Guaranty = **10%** of total bid price. |
| CC-03 | Non-collusive bidding certification | DelDOT 102.15 | High | The certification must be **present**; formatting changes are not deviations. |
| CC-04 | Performance and payment bonds | DelDOT 103.5 | High | Both bonds at **100%** of contract price. |
| CC-05 | Contract execution and proof of insurance | DelDOT 103.7 | High | Execution documents within **20 calendar days** of notice of award; insurance **before** execution. |
| CC-06 | Contractor Registration Act notice | 19 Del. C. § 3604 | High | Registration must not be allowed to happen **only after work begins**. |
| CC-07 | Delaware business / subcontractor licenses | 29 Del. C. § 6967 | High | Prime licence with the proposal; sub licences within **30 days** of contract entry (or **10 days** if hired more than 20 days in). |
| CC-08 | Addenda and Q&A currency | Attachments / Addenda | High | Use the **latest** addendum; ignoring a later one is a finding. |
| CC-09 | Buy America / BABA applicability | Buy America Requirement | Critical | Apply only when metadata says it applies — and when it does, a clause saying it doesn't is a finding. |
| CC-10 | Coordination / order of precedence | DelDOT 105.6 | High | Documents are complementary; conflicts resolve down the **105.6 ladder**. |
| CC-11 | Contract changes must follow written process | DelDOT 104.2 | High | **Oral direction alone must not immediately alter scope, price, or time.** |
| CC-12 | Notification of contract changes | DelDOT 104.3 | High | Immediate oral + written notice; written follow-up within **7 calendar days**; work proceeds only after written direction. |
| CC-13 | Right to audit and record retention | Right to Audit | Medium | Records auditable and retained **three years** after final payment. |
| CC-14 | Contract subletting | DelDOT 108.1 | High | Prime self-performs **≥ 50%** of original contract price; subletting needs **written consent**. |
| CC-15 | Claims procedure | DelDOT 105.15 | Medium | Written claim within **30 calendar days** after the noticed work completes, with 104.3 notice compliance. |
| CC-16 | Extensions of contract time | DelDOT 108.7 | Medium | Needs excusable delay + timely written request + critical-path effect. **Never automatic.** |
| CC-17 | Liquidated damages schedule / rate logic | DelDOT 108.9 | Medium | Use the governing **schedule** for the contract value and time basis; a universal invented flat daily rate is a deviation. |
| CC-18 | Compensation for changes | DelDOT 109.4 | Medium | Pricing sequence **unit price → negotiated → force account**; a fixed arbitrary markup replacing it is a deviation. |

---

## 5. Abbreviations

| | |
|---|---|
| **BABA** | Build America, Buy America Act |
| **CC-NN** | Contract Clause requirement ID, `CC-01` … `CC-18` |
| **CDK** | AWS Cloud Development Kit — used by `deploy/` |
| **Del. C.** | Delaware Code |
| **DelDOT** | Delaware Department of Transportation |
| **F1** | Harmonic mean of precision and recall; the finding-detection metric |
| **FHWA** | Federal Highway Administration |
| **LD** | Liquidated damages |
| **OCR** | Optical character recognition (for scanned PDFs — not exercised here) |
| **Q&A** | Solicitation questions and answers, issued alongside addenda |
| **RAG** | Retrieval-augmented generation — considered and rejected; see SOLUTION.md |
| **Skill** | Rules supplied to a model in a prompt and re-derived each run — considered and rejected in favour of compiling the same rules into code; its *shape* (one judgement unit per requirement, fixed order, verbatim evidence, explicit "I don't know") is kept. See SOLUTION.md |
