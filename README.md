# README (branch: evweyer-test-1)

This README describes branch-specific details for the evweyer-test-1 branch of the Deldot-Contract-team repository.

## Purpose
This branch is an experimental / work-in-progress branch used by @evweyer for testing changes to the repository structure and documentation. The README here documents branch-specific instructions, known differences from the default branch, and how to run quick checks against the package.

## Branch-specific changes
- Documentation updates and README scaffolding localized to this branch only.
- Intended for exploratory edits; do not treat outputs on this branch as final.
- This branch contains instruction and output for testing a specialized Microsoft Copilot agent. The agent's prompts, configuration, and any generated outputs are included here for development and evaluation purposes only.

## Copilot agent testing (branch-local)
- Purpose: validate behaviors and integration of a specialized Microsoft Copilot agent configured to assist with contract-clause risk flagging tasks.
- Contents: example prompts, agent configuration files (if present), and sample agent outputs.
- Safety: review generated outputs carefully before using them in production; remove or redact any sensitive information before merging to main branches.

## How to validate locally
1. Clone the repository and check out the branch:

   git clone https://github.com/NSF-DARSE/Deldot-Contract-team.git
   cd Deldot-Contract-team
   git checkout evweyer-test-1

2. Review the `Contract_Clause_Risk_Flagging/` package files and any Development or Validation data in that directory.

3. If the branch includes code changes later, run unit or integration tests as appropriate (project-specific commands aren't included in this branch README).

## Notes for reviewers
- This branch README is intentionally minimal and intended to make the branch's purpose clear to reviewers.
- If you plan to merge these changes into the default branch, confirm that README content is merged or revised to match project-level documentation.

## Contact / Author
Branch owner: @evweyer

---

(Branch-local README created to document changes and usage for evweyer-test-1.)
