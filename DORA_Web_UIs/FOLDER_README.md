# DORA_Web_UIs — Nikki's contribution

The deterministic review pipeline plus three chat UIs for DORA, each on its own port
and backend. All three share one FastAPI server (`deploy/dora_chat.py`) run as
separate instances, one localhost port each:

| Port | UI | Backend |
|---|---|---|
| 8081 | `website/` (blue) | Deterministic rule pipeline (`crf/`) — no LLM, no key. Scores DEV packages against `Development_Labels.csv`, exports the 15-field submission CSV. |
| 8082 | `website-gemini/` (violet) | Gemini function-calling loop with local tools — sees uploaded packages. Needs `GOOGLE_API_KEY`. Falls back across models on quota (429) and retries on capacity (503). |
| 8083 | `website-copilot/` (teal) | Microsoft Copilot Studio agent — custom Bot Framework WebChat with per-package projects and resumable history (needs the agent's Direct Line token endpoint + No authentication); `iframe.html` is the zero-setup embed fallback. |

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r deploy/requirements-dora-chat.txt
export GOOGLE_API_KEY=...        # for 8082 only
./deploy/run_both.sh             # starts all three
```

Expects the challenge dataset at `Contract_Clause_Risk_Flagging/` (repo root here) —
set `CRF_DATA_ROOT` if it lives elsewhere.

Packages uploaded through any UI land in a shared `uploads/` directory and are
immediately reviewable by the 8081/8082 backends. Hosted agents (Copilot, Gemini
Enterprise) cannot reach localhost — the 8083 UI hands them uploads as pasted
text/one-file bundles via `/api/packages/{id}/briefing`.

`prompts/dora_agent_prompt_v2.xml` is the DORA persona used by the LLM backends.
Full architecture write-up: `SOLUTION.md`; codebase map: `ONBOARDING.md`.

Decision support only — findings are flags for human review, not approval, award,
or legal determinations.
