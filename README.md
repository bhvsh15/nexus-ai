# NexusAI

A local-first AI engineering platform. One app that replaces LangSmith, LangFuse, PromptLayer, RAGAS Dashboard, and CrewAI Studio — fully open source, running entirely on your machine.

---

## What It Does

| Module | Status | Description |
|---|---|---|
| Prompt Lab | ✅ Complete | Prompt versioning, Jinja2 templating, A/B testing, LLM-as-judge eval, deployment API |
| RAG Studio | 🔧 In Progress | Document ingestion, ChromaDB retrieval, pipeline querying, RAGAS eval |
| Agent Builder | 🔜 Coming | LangGraph agents, tool registry, live SSE trace streaming |
| Crew Studio | 🔜 Coming | CrewAI multi-agent orchestration, real-time collaboration trace |
| Observability | 🔜 Coming | LLM call tracking, latency, cost estimation, alerts |

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
- [ ] Agent Builder — LangGraph + SSE streaming
- [ ] Crew Studio — CrewAI orchestration
- [ ] Observability Dashboard
- [ ] Frontend — Next.js 14
- [ ] Auth — JWT + API keys
- [ ] Docker Compose — one-command setup
