# NexusAI

A local-first AI engineering platform. One app that replaces LangSmith, LangFuse, PromptLayer, RAGAS Dashboard, and CrewAI Studio — fully open source, running entirely on your machine.

> Built as a portfolio project to demonstrate production-grade AI engineering — not just calling an API, but versioning, evaluating, tracing, and orchestrating AI systems end to end.

---

## The Problem

AI engineers today juggle 5+ paid tools just to manage prompts, evaluate RAG pipelines, monitor agents, and orchestrate multi-agent systems. These tools are expensive, cloud-dependent, and siloed.

NexusAI brings all of it into one platform that runs on your laptop — no API keys, no cloud costs, no vendor lock-in. Just Ollama + your machine.

---

## Why This Is Different

- **Fully local** — all LLM calls go through Ollama. Your data never leaves your machine.
- **Production patterns** — prompt versioning like git, RAGAS evaluation, OpenTelemetry traces, LLM-as-judge scoring. These are real production concerns, not toy demos.
- **5 tools in one** — instead of switching between LangSmith, LangFuse, RAGAS, CrewAI Studio, and PromptLayer, everything lives in one unified platform.
- **One command to run** — `docker compose up` and you're live.

---

## What It Does

### Prompt Lab ✅
A full prompt engineering workbench — not just a playground.
- Git-style versioning: commit, diff, rollback prompts
- Jinja2 templating: `{{role}}`, `{{context}}`, `{{language}}`
- LLM-as-judge scoring: Ollama evaluates Ollama's own outputs (0–1 score + reason)
- Stage promotion: draft → staging → production workflow
- Deployment API: `GET /api/prompt-lab/prompts/{name}/production` — any external app fetches the live prompt

### RAG Studio 🔧
Build, test, and compare RAG pipelines visually.
- Upload documents (PDF, MD, TXT) and configure chunking + embedding model
- ChromaDB vector storage with Ollama embeddings
- Query pipeline: retrieve relevant chunks, generate grounded answers
- RAGAS evaluation: faithfulness, answer relevancy, context precision, context recall (coming)
- Pipeline comparison: run same questions on different configs, see which wins

### Agent Builder ✅
Visual LangGraph agent construction.
- Create agents with a name, model, and a set of tools
- Built-in tool registry: calculator, echo (web scraper + Python executor coming)
- Run agents and stream execution live via SSE — watch each node fire in real time
- Every run and each step saved as a trace in the DB

### Crew Studio 🔜
Multi-agent orchestration with CrewAI.
- Create agents with name, role, goal, backstory, tools, model
- Assign tasks and assemble crews with sequential or hierarchical process
- Watch agents collaborate in real time
- Save crews as reusable templates

### Observability Dashboard 🔜
The nerve center — aggregates data from all modules.
- Every LLM call tracked: model, latency, token count, prompt, response
- Cost estimator (even for local models — compute time based)
- Prompt performance over time, RAG health monitor, agent reliability stats
- Alerts when eval scores drop below threshold

---

| Module | Status |
|---|---|
| Prompt Lab | ✅ Complete |
| RAG Studio | 🔧 In Progress |
| Agent Builder | ✅ Complete |
| Crew Studio | 🔜 Coming |
| Observability | 🔜 Coming |

---

## Tech Stack

| Layer | Choice |
|---|---|
| LLMs | Ollama (Llama 3, Mistral, Gemma, Nomic Embed) |
| Backend | FastAPI + SQLModel |
| Database | SQLite (dev) → PostgreSQL (prod-ready) |
| Vector Store | ChromaDB |
| Agent Framework | LangGraph |
| Multi-agent | CrewAI |
| RAG Evals | RAGAS |
| Streaming | Server-Sent Events (SSE) |
| Frontend | Next.js 14 + shadcn/ui + Tailwind (coming) |
| Deploy | Docker Compose (coming) |

---

## Running Locally

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- At least one model pulled: `ollama pull llama3.2`
- For embeddings: `ollama pull nomic-embed-text`

### Setup

```bash
git clone https://github.com/bhvsh15/nexus-ai.git
cd nexus-ai/backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## API Endpoints

### Prompt Lab `/api/prompt-lab`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/prompts` | Create a prompt |
| GET | `/prompts` | List all prompts |
| GET | `/prompts/{id}` | Get a prompt |
| POST | `/prompts/{id}/versions` | Commit a new version |
| GET | `/prompts/{id}/versions` | List all versions |
| PATCH | `/prompts/{id}/versions/{vid}/promote` | Promote to draft/staging/production |
| POST | `/prompts/{id}/versions/{vid}/render` | Render Jinja2 template with variables |
| POST | `/prompts/{id}/versions/{vid}/eval` | Run LLM-as-judge eval |
| GET | `/prompts/{name}/production` | Fetch current production version |

### RAG Studio `/api/rag-studio`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/pipelines` | Create a RAG pipeline |
| GET | `/pipelines` | List all pipelines |
| GET | `/pipelines/{id}` | Get a pipeline |
| POST | `/pipelines/{id}/ingest` | Upload and ingest a document |
| POST | `/pipelines/{id}/query` | Query the pipeline |

### Agent Builder `/api/agent-builder`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/agents` | Create an agent |
| GET | `/agents` | List all agents |
| GET | `/agents/{id}` | Get an agent |
| GET | `/agents/{id}/run?input=...` | Run agent, stream steps via SSE |
| GET | `/agents/{id}/runs/{run_id}` | Get a run |
| GET | `/agents/{id}/runs/{run_id}/steps` | Get all steps of a run |

---

## Project Structure

```
nexus-ai/
├── backend/
│   ├── core/
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── database.py        # SQLModel engine + session
│   │   └── ollama_client.py   # Ollama wrapper (chat, embeddings, list models)
│   ├── modules/
│   │   ├── prompt_lab/        # Versioning, evals, deployment API
│   │   ├── rag_studio/        # Ingestion, ChromaDB, RAGAS
│   │   ├── agent_builder/     # LangGraph, tools, SSE traces
│   │   ├── crew_studio/       # CrewAI integration
│   │   └── observability/     # OTel, metrics, alerts
│   └── main.py
├── frontend/                  # Next.js 14 (coming)
└── docker-compose.yml         # One-command startup (coming)
```

---

## Roadmap

- [x] Project scaffold + core setup
- [x] Prompt Lab — full module
- [x] RAG Studio — ingestion + query
- [ ] RAG Studio — RAGAS eval metrics
- [x] Agent Builder — LangGraph + SSE streaming
- [ ] Crew Studio — CrewAI orchestration
- [ ] Observability Dashboard
- [ ] Frontend — Next.js 14
- [ ] Auth — JWT + API keys
- [ ] Docker Compose — one-command setup
