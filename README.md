# OS-APOW - Headless Agentic Orchestration Platform

**Application:** workflow-orchestration-queue (OS-APOW)  
**Type:** Headless Agentic Orchestration Platform  
**Version:** 0.1.0

---

## Overview

OS-APOW transforms interactive AI coding into autonomous background service. It converts GitHub Issues into "Execution Orders" that AI agents fulfill without human intervention, moving the agent from a passive co-pilot role to a background production service.

The system is designed to be **Self-Bootstrapping** - the initial deployment is seeded from a template repository, and once the "Sentinel" is active, the system uses its own orchestration capabilities to refine its components.

---

## Architecture

OS-APOW consists of four core pillars:

### 1. The "Ear" (Work Event Notifier)
- **Technology:** Python 3.12, FastAPI, Pydantic
- **Phase:** Phase 2
- **Responsibilities:** Secure webhook ingestion with HMAC SHA256 validation, intelligent event triage, queue initialization

### 2. The State (Work Queue)
- **Philosophy:** "Markdown as a Database"
- **State Machine:** Label-based workflow (`agent:queued` → `agent:in-progress` → `agent:success`/`agent:error`)
- **Concurrency Control:** GitHub "Assignees" as distributed lock semaphore

### 3. The "Brain" (Sentinel Orchestrator)
- **Technology:** Python (Async Background Service)
- **Phase:** Phase 1 (MVP)
- **Responsibilities:** Polling discovery, task claiming, shell-bridge dispatch, telemetry

### 4. The "Hands" (Opencode Worker)
- **Technology:** opencode CLI, LLM Core
- **Environment:** DevContainer from template repository
- **Responsibilities:** Code generation, testing, PR creation

---

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)
- GitHub token with appropriate permissions

### Installation

```bash
# Clone the repository
git clone https://github.com/intel-agency/workflow-orchestration-queue-hotel41-a.git
cd workflow-orchestration-queue-hotel41-a

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Configuration

Set the required environment variables:

```bash
# Required
export GITHUB_TOKEN="your-github-token"
export GITHUB_ORG="your-org"
export GITHUB_REPO="your-repo"

# Optional
export SENTINEL_BOT_LOGIN="your-bot-login"  # For assign-then-verify locking
export WEBHOOK_SECRET="your-webhook-secret"  # For notifier service
```

### Running the Services

#### Sentinel Orchestrator (Polling Service)

```bash
# Using uv
uv run sentinel

# Or directly
python -m src.orchestrator_sentinel
```

#### Notifier Service (Webhook Receiver)

```bash
# Using uv
uv run notifier

# Or with uvicorn directly
uvicorn src.notifier_service:app --host 0.0.0.0 --port 8000
```

#### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Development

### Project Structure

```
workflow-orchestration-queue/
├── src/
│   ├── __init__.py
│   ├── notifier_service.py      # FastAPI webhook ingestion (Phase 2)
│   ├── orchestrator_sentinel.py # Background polling and dispatch
│   ├── models/
│   │   ├── __init__.py
│   │   ├── work_item.py         # Unified WorkItem, TaskType, WorkItemStatus
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── queue/
│       ├── __init__.py
│       └── github_queue.py      # ITaskQueue ABC + GitHubQueue
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_work_item.py
│   │   └── test_github_queue.py
│   └── integration/
│       └── test_integration.py
├── scripts/
│   ├── devcontainer-opencode.sh # Core shell bridge
│   └── gh-auth.ps1              # GitHub App auth sync
├── docs/
│   └── [architecture and planning docs]
├── plan_docs/
│   └── [planning documents]
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only unit tests
uv run pytest -m unit

# Run only integration tests (requires setup)
uv run pytest -m integration
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check .

# Format with ruff
uv run ruff format .

# Type check with mypy
uv run mypy src/
```

---

## API Documentation

When the notifier service is running, access the auto-generated API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## State Machine

| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | Waiting | Task validated, awaiting Sentinel |
| `agent:in-progress` | Claimed | Sentinel has claimed the issue |
| `agent:reconciling` | Recovery | Stale task being recovered |
| `agent:success` | Complete | Terminal success state |
| `agent:error` | Failed | Technical failure occurred |
| `agent:infra-failure` | Infra Error | Container/build failure |
| `agent:stalled-budget` | Budget | Cost threshold exceeded |

---

## Security

- **Webhook Validation:** HMAC SHA256 signature verification
- **Credential Scoping:** Ephemeral environment variables
- **Credential Scrubbing:** Regex-based sanitization before public posting
- **Network Isolation:** Dedicated Docker bridge network
- **Resource Constraints:** 2 CPUs / 4GB RAM per worker

---

## References

- [Architecture Guide](plan_docs/OS-APOW%20Architecture%20Guide%20v3.2.md)
- [Development Plan](plan_docs/OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Spec](plan_docs/OS-APOW%20Implementation%20Specification%20v1.2.md)
- [Tech Stack](plan_docs/tech-stack.md)
- [Architecture Summary](plan_docs/architecture.md)
- [Repository Summary](.ai-repository-summary.md)

---

## License

MIT License - See [LICENSE](LICENSE) for details.
