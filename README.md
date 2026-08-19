# DORA — DelDOT Orchestrated Review Assistant

DORA is an evidence‑grounded contract clause review system built to analyze Delaware Department of Transportation (DelDOT) construction contract packages. It extracts text from PDFs, applies deterministic applicability rules, evaluates clauses against a curated reference checklist, and produces auditable results with file/page/line provenance.

This README targets the generating_rag branch and documents how to set up, run, and contribute to the project. For branch‑specific deployment notes see deploy.md.

Table of contents

- What this is
- Quick facts / stack
- Repository layout
- Setup
  - Prerequisites
  - Python backend
  - Frontend (dora-ui)
  - Optional: Docker
- How to run
  - CLI pipeline (contract_review)
  - API server (dora_api)
  - Frontend (development and production)
- Outputs and file formats
- RAG / Bedrock notes (experimental)
- Testing
- Deployment (high level)
- Contributing
- License & contact

What this is

An end‑to‑end system that: (1) ingests contract PDFs grouped into packages; (2) determines which checklist requirements apply to a package; (3) judges whether a package meets each requirement using a mixture of deterministic logic and model‑backed analysis; and (4) emits auditable outputs (CSV/JSON/PDF) with evidence links to the exact contract lines.

Quick facts / stack

- Languages: Python (backend & pipeline), TypeScript/React (UI), small tooling in top‑level scripts
- Frameworks: FastAPI for API server; React + TypeScript for frontend
- Notable libraries (examples): pdfplumber (extraction), FastAPI, Uvicorn, pytest; Bedrock/LLM integrations are in contract_review/bedrock_client.py

Repository layout (top-level)

```text
.dockerignore           # Docker ignore
.Dockerfile             # Container build for App Runner / ECR
.deploy.md              # Deployment notes (AWS App Runner)
LICENSE
README.md               # (this file) branch: generating_rag
requirements.txt        # Python deps
contract_review/        # Core pipeline: extraction, pipeline, scoring, reporting
dora_api/               # FastAPI server and project management endpoints
dora-ui/                # React + TypeScript frontend
Contract_Clause_Risk_Flagging/  # Challenge data, references, development/validation sets
docs/                   # Sphinx docs + output file reference
infrastructure/         # AWS infra manifests (ECR/App Runner etc.)
output/                 # Example output runs (dev/validation)
generate_kb_metadata.py # helper for knowledge base metadata
spot_check.py           # quick verification scripts
peek.py                 # small utility
src/                    # miscellaneous supporting code
```

How it fits together

- The main CLI entrypoint is contract_review/cli.py. It runs package discovery, invokes ReviewPipeline (contract_review.pipeline), talks to a BedrockClient when configured, and writes outputs.
- The API (dora_api) wraps the CLI/pipeline for interactive usage: upload packages, organize into named packages, trigger background analysis, and download results.
- The dora-ui frontend talks to the API to create projects, upload files, trigger analysis, and present results.

Setup

Prerequisites

- Git
- Python 3.10+
- Node.js 18+ and npm or pnpm (for dora-ui)
- Docker (optional, for container builds)
- AWS account & CLI (optional, for Bedrock or App Runner deployment)

Python backend

1. Create and activate a virtualenv

   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .\.venv\Scripts\activate  # Windows

2. Install dependencies

   pip install -r requirements.txt

3. Common environment variables (examples)

- AWS_REGION or AWS_DEFAULT_REGION
- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (or use an IAM role when running in AWS)
- KB_ID — Knowledge Base ID used by the RAG experiments (if configured)
- Any other env file referenced in dora_api/config or contract_review/config (check those files for exact names)

Frontend (dora-ui)

1. Install packages

   cd dora-ui
   npm install

2. Development server

   npm run dev

3. Build production assets

   npm run build  # emits dora-ui/dist/

Docker (optional)

- The Dockerfile in the repo root builds a container that serves the API and the frontend (if dora-ui/dist exists). Typical workflow:

  docker build -t dora:latest .
  # Tag and push to your registry (ECR for AWS): see deploy.md

How to run

CLI pipeline (quick path)

- Run a single package and produce outputs

  python -m contract_review.cli --package Contract_Clause_Risk_Flagging/Development/Pine_Grove --score

- Run the bundled development set and score

  python -m contract_review.cli --set development --score

- Default output dir is output/ (override with --out)

API server (development)

- Start the FastAPI server (example using Uvicorn):

  python -m uvicorn dora_api.main:app --reload --host 0.0.0.0 --port 8000

- Endpoints of interest (see dora_api/main.py):
  - POST /api/projects — create a project
  - POST /api/projects/{id}/upload — upload PDFs (supports folder uploads)
  - POST /api/projects/{id}/organize — group uploaded files into named packages
  - POST /api/projects/{id}/analyze — trigger analysis (runs in background)
  - GET /api/projects/{id}/outputs — list outputs
  - GET /api/projects/{id}/outputs/{name} — download an output

Frontend (development + production)

- Development: run the dora-ui dev server and point it at the API (see CORS settings in dora_api/config.py)
- Production: run npm run build in dora-ui so the static files are placed in dora-ui/dist; the FastAPI server will serve those files when present.

Outputs and file formats

Analysis produces these canonical outputs (see docs/output_files/ for field-level detail):

- submission.csv — one row per package × requirement (the challenge submission format)
- evidence_trace.csv — audit CSV with file/page/line references and quality metrics
- findings_report.json — nested human readable report with verbatim quotes and criteria
- run_summary.json — bookkeeping (packages processed, token usage, totals)

RAG / Bedrock notes (experimental)

- The generating_rag branch contains experimental code that constructs or queries a knowledge base and uses Bedrock (or configured LLM) to perform model judgments with retrieval context.
- If you use RAG features, ensure the KB_ID and AWS credentials are configured and that your IAM role has the required Bedrock permissions. See generate_kb_metadata.py and contract_review/bedrock_client.py for details.

Testing

- Python tests: run pytest if a tests/ suite is present. Example:

  pytest -q

- Frontend tests: from dora-ui, run npm test (if configured in package.json)

Deployment (high level)

- Build dora-ui: cd dora-ui && npm run build
- Build Docker image: docker build -t dora:latest .
- Push to your registry (ECR for AWS) and deploy via App Runner/ECS/Kubernetes. The repo includes deploy.md with step‑by‑step App Runner instructions.

Security & data handling

- Do not commit secrets or private data; use .env and .gitignore
- The API enforces a maximum upload size; check dora_api/config.py for MAX_UPLOAD_SIZE

Contributing

- Use feature branches: feature/<name> or fix/<name>
- Open a Pull Request against the main integration branch
- Add tests for behavioral changes and ensure CI passes

License & contact

- See LICENSE in the repo root for the project's license.
- For questions about this codebase, contact the repository maintainers or the Deldot Contract Team.

---

What I did

I reviewed the generating_rag branch (top‑level files, the CLI entrypoint, and the FastAPI app) and created a clearer, focused README.md on the generating_rag branch with structured setup and run instructions.

Next steps I can take for you

- Commit the same README to the default branch (main/master) if you want it visible for everyone using the repo.
- Or extend the README with copy snippets from files like contract_review/cli.py, dora_api/main.py, or docs/output_files/ for deeper command examples and exact env var names.

If you want me to commit this README to the generating_rag branch now, confirm and I will write it to the repository.