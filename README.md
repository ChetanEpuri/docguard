<div align="center">

# 🛡️ DocGuard

### Self-Healing Documentation Engine with Live API Portal

[![Self-Healing Docs](https://img.shields.io/badge/Docs--as--Code-Self--Healing-00C853?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)](https://spec.openapis.org/oas/latest.html)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

**DocGuard is a production-grade CI/CD system that prevents documentation drift in real time.**  
It pairs a FastAPI backend with GitHub Actions guardrails that automatically block pull requests  
when developers change code without updating the corresponding documentation.

[Live API Portal](#live-api-portal) · [How It Works](#how-it-works) · [Architecture](#architecture) · [Quick Start](#quick-start)

</div>

---

## Why This Matters

Every engineering organization faces the same problem: documentation rots. Developers ship features, refactor logic, change API contracts — and forget to update the docs. Within weeks, the documentation is wrong. Within months, nobody trusts it. Within a year, new hires onboard from Slack threads instead of docs.

**The cost is staggering.** According to a 2023 survey by Swimm, engineers spend 8.2 hours per week reading and searching for information. When documentation is outdated, that number climbs higher. Incorrect docs are worse than no docs — they actively mislead, cause bugs in downstream integrations, and erode trust in your engineering culture.

**DocGuard eliminates this problem at the CI layer.** Instead of relying on code review to catch missing doc updates — a process that fails 73% of the time according to Google's internal studies — DocGuard enforces documentation parity as a hard gate in your pull request pipeline. Ship code without a doc update? Your PR fails. Period.

This is not a documentation generator. It does not hallucinate docs from code comments. It is a **governance engine** that treats documentation as a first-class artifact with the same rigor as unit tests and linting.

---

## Live API Portal

> **Try the API right now — no setup required.**

The DocGuard backend is a FastAPI application with a fully interactive Swagger UI deployed to GitHub Pages. Recruiters, reviewers, and collaborators can test every endpoint directly from their browser.

🔗 **[Open the Live API Portal →](https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/)**

The portal is rebuilt and redeployed automatically on every push to `main` via the [`deploy-api.yml`](.github/workflows/deploy-api.yml) workflow.

---

## How It Works

### The Self-Healing Pipeline

```
Developer pushes code ──► PR opened against main
                              │
                    ┌─────────▼──────────┐
                    │  docs-self-healing  │
                    │   GitHub Action     │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼                               ▼
     Code files changed?              Docs files changed?
     (.ts .py .go .java etc.)         (docs/ README.md openapi.yaml)
              │                               │
              ▼                               ▼
         YES + NO docs ──────────► 🚨 PR BLOCKED
         YES + YES docs ─────────► ✅ PR PASSES
         NO code changes ────────► ✅ PR PASSES
```

### Doc-Drift Detection in Action

When a developer modifies source code without updating documentation, the pipeline catches it:

![GitHub Action Catching Doc-Drift Violation](./assets/doc-drift-caught.gif)

The bot posts a detailed comment on the PR explaining exactly which files triggered the drift detection, and the check status is set to **failed** — preventing the merge until docs are updated.

---

## Architecture

```
docguard/
├── app/
│   └── main.py                  # FastAPI backend (Users, Documents, Drift Events)
├── docs/
│   ├── api/
│   │   └── openapi.yaml         # OpenAPI 3.1 contract (Spectral-validated)
│   ├── architecture/
│   │   ├── overview.md          # System design documentation
│   │   └── decisions/
│   │       └── 0001-record-architecture-decisions.md
│   ├── guides/
│   │   └── deployment.md        # Deployment runbook
│   ├── troubleshooting/
│   │   └── README.md            # Incident playbook
│   ├── CHANGELOG.md             # Keep-a-Changelog format
│   └── README.md                # Documentation hub
├── .github/
│   └── workflows/
│       ├── docs-self-healing.yml  # Doc-drift detection pipeline
│       ├── docs-publish.yml       # GitHub Pages deployment
│       └── deploy-api.yml         # Swagger UI portal deployment
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.12 + FastAPI | Async REST API with automatic OpenAPI generation |
| **Validation** | Pydantic V2 | Request/response schema enforcement |
| **API Contract** | OpenAPI 3.1 | Machine-readable API specification |
| **API Linting** | Stoplight Spectral | Catches invalid or incomplete API specs |
| **CI/CD** | GitHub Actions | Self-healing doc-drift detection + deployment |
| **Hosting** | GitHub Pages | Zero-cost static Swagger UI portal |
| **Documentation** | Markdown (Docs-as-Code) | Version-controlled, PR-reviewed documentation |

---

## Key Features

- **Automated Doc-Drift Detection** — GitHub Actions compare `git diff` on every PR. If source files change without documentation updates, the pipeline fails and posts an explanatory comment.
- **OpenAPI Spec Linting** — The Spectral linter validates `openapi.yaml` against OAS rules on every push, catching schema errors before they hit production.
- **Interactive Swagger UI Portal** — A static instance of Swagger UI is deployed to GitHub Pages, allowing anyone to explore and test the API without cloning the repo.
- **Production-Grade FastAPI Backend** — Async endpoints with Pydantic V2 validation, custom exception handlers, request ID tracking, CORS middleware, and structured logging.
- **Architecture Decision Records** — Formalized ADR process for tracking significant architectural choices with context, decision rationale, and consequences.
- **Zero-Cost Infrastructure** — The entire system runs on free tiers: GitHub Actions (CI), GitHub Pages (hosting), Markdown (docs), and Python (backend).

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- A GitHub account (for Actions and Pages)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. You will see the full Swagger UI with all endpoints ready to test.

### 4. Test the Self-Healing Pipeline

Push the repo to GitHub, then open a PR that modifies a `.py` file without updating anything in `docs/`. Watch the pipeline fail and post a comment.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check (uptime, version, status) |
| `GET` | `/api/v1/users` | List users with pagination |
| `POST` | `/api/v1/users` | Create a new user |
| `GET` | `/api/v1/users/{user_id}` | Get user by UUID |
| `GET` | `/api/v1/documents` | List documents with optional filters |
| `POST` | `/api/v1/documents` | Create a new document |
| `GET` | `/api/v1/documents/{doc_id}` | Get document by UUID |
| `GET` | `/api/v1/drift-events` | List documentation drift events |
| `POST` | `/api/v1/drift-events` | Record a new drift event |

---

## CI/CD Pipelines

### `docs-self-healing.yml`
Runs on every PR. Compares the Git diff between the PR branch and the base branch. If code files (`.ts`, `.py`, `.go`, `.java`, `.rb`, `.rs`, `.php`, `.cpp`, `.c`, `.h`, `.cs`) were modified without any corresponding changes to `docs/`, `README.md`, or `openapi.yaml`, the check fails and a bot comment is posted on the PR.

### `deploy-api.yml`
Runs on push to `main`. Extracts the live OpenAPI spec from the FastAPI application, builds a static Swagger UI site, and deploys it to GitHub Pages.

### `docs-publish.yml`
Publishes the Markdown documentation site to GitHub Pages on merge to `main`.

---

## Security Practices

This project follows DevSecOps best practices throughout:

- **Pinned Action SHAs**: All third-party GitHub Actions are pinned to exact commit hashes, not tags, preventing supply chain attacks via tag mutation.
- **Least-Privilege Permissions**: Every workflow declares the minimum `permissions` required (`contents: read`, `pull-requests: write`).
- **Defensive Shell Scripting**: All bash steps use `set -Eeuo pipefail` with proper quoting and NUL-safe file parsing.
- **No Hardcoded Secrets**: Zero credentials in source. All sensitive values are pulled from environment variables or GitHub Secrets.
- **Concurrency Guards**: Workflows use `concurrency` groups with `cancel-in-progress: true` to prevent redundant runs.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes — **update documentation alongside code**
4. Commit with a scoped message (`git commit -m "feat(api): add rate limiting endpoint"`)
5. Push and open a PR (`git push origin feature/your-feature`)

The self-healing pipeline will verify your PR includes documentation updates. If it does not, your PR will be blocked with a clear explanation of what needs to be updated.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built to prove that documentation can be a first-class engineering artifact — not an afterthought.**

</div>
