<div align="center">
  <img src="docs/images/logo.png" alt="OpenAgentLab Logo" width="400">
</div>

# OpenAgentLab

> A production-oriented AI platform for document understanding, retrieval, and intelligent workflow orchestration.

OpenAgentLab is an open-source AI orchestration platform for building document-aware agentic applications with production software engineering practices.

The project is more than a chatbot. It combines a FastAPI backend, deterministic document-processing tools, retrieval-augmented generation, LangGraph workflow components, workflow persistence, observability hooks, evaluation tooling, and a small React client for submitting runs.

The project follows a **Design First** approach: architecture, engineering principles, and ADRs live in `docs/` alongside the implementation.

## What It Does

- Upload and persist supported files: PDF, CSV, XLSX, DOCX, TXT, Markdown, and JSON
- Submit natural language questions through API endpoints or the web client
- Attach files to UI message submissions and persist their metadata
- Retrieve relevant document context with OpenAI embeddings and Qdrant
- Build grounded answers with source metadata
- Track workflow execution status and recent workflow runs
- Use LangGraph-based agent components for planning, tool selection, execution, and response generation
- Store structured application data in PostgreSQL through SQLAlchemy and Alembic
- Store files locally by default, with Azure Blob Storage support in the storage layer
- Enable optional Langfuse tracing with redaction helpers
- Run unit, integration, evaluation, and smoke tests

## Architecture Overview

flowchart TB
    UI["React Web Client<br/><small>Vite</small>"]
    API["REST API<br/><small>FastAPI</small>"]

    DOC["Document APIs"]
    MSG["Message APIs"]
    WF["Workflow APIs"]

    FILES["File Storage & Metadata<br/><small>Local / Azure Blob Storage</small>"]
    RAG["RAG Retrieval<br/><small>OpenAI embeddings + Qdrant</small>"]
    DB["PostgreSQL<br/><small>Workflow state</small>"]

    CONTEXT["Context Builder<br/><small>Bounded context + source metadata</small>"]
    LLM["OpenAI Response Generation"]

    UI --> API
    API --> DOC
    API --> MSG
    API --> WF

    DOC --> FILES
    MSG --> RAG
    WF --> DB

    RAG --> CONTEXT
    CONTEXT --> LLM

    classDef client fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e,stroke-width:2px;
    classDef api fill:#ede9fe,stroke:#7c3aed,color:#3b0764,stroke-width:2px;
    classDef service fill:#f0fdf4,stroke:#16a34a,color:#14532d;
    classDef storage fill:#fff7ed,stroke:#ea580c,color:#7c2d12;
    classDef ai fill:#fdf2f8,stroke:#db2777,color:#831843,stroke-width:2px;

    class UI client;
    class API api;
    class DOC,MSG,WF service;
    class FILES,DB storage;
    class RAG,CONTEXT,LLM ai;

Agent modules under `src/openagentlab/agent` provide planning, tool selection, deterministic tool execution, plan validation, and response nodes for orchestrated workflows.

## Technology Stack

| Category | Technology |
| --- | --- |
| Backend | FastAPI, Uvicorn |
| Frontend | React, Vite, TypeScript |
| Workflow engine | LangGraph |
| LLM and embeddings | OpenAI |
| Retrieval | Qdrant |
| Database | PostgreSQL, SQLAlchemy async, Alembic |
| File storage | Local filesystem, Azure Blob Storage layer |
| Document tooling | pypdf, python-docx, openpyxl, CSV, JSON, text readers |
| Observability | Langfuse, structured logging |
| Evaluation | DeepEval, Ragas |
| Packaging | Docker, Docker Compose, uv |
| Cloud direction | Azure Container Apps, Azure PostgreSQL, Azure Blob Storage, Qdrant Cloud |

## Repository Structure

```text
.
|-- apps/
|   `-- web/                       # React/Vite workflow client
|-- src/
|   `-- openagentlab/
|       |-- agent/                 # LangGraph-oriented agent components
|       |-- api/                   # FastAPI routers and dependencies
|       |-- core/                  # settings, logging, exception handling
|       |-- database/              # SQLAlchemy engine, session, models
|       |-- evaluation/            # evaluation runner and model helpers
|       |-- observability/         # Langfuse integration
|       |-- rag/                   # loaders, chunking, embeddings, vector stores
|       |-- repositories/          # persistence access layer
|       |-- schemas/               # public API schemas
|       |-- services/              # application services
|       |-- skills/                # document-processing skill and tools
|       |-- storage/               # local and Azure storage providers
|       `-- tools/                 # tool registry and base contracts
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- evaluation/
|   `-- e2e/
|-- docs/
|   |-- architecture/
|   |-- ADR/
|   `-- engineering/
|-- alembic/
|-- deployment/
|-- docker/
|-- evaluation/
|-- storage/
|-- Dockerfile
|-- docker-compose.yml
|-- pyproject.toml
`-- README.md
```

## Quick Start

### Requirements

- Python 3.12+
- `uv`
- Docker and Docker Compose for the full local stack
- Bun or another Node-compatible package manager for `apps/web`
- An `OPENAI_API_KEY` for RAG and answer generation

### Configure Environment

Create a local `.env` file from the checked-in template:

```bash
cp .env.example .env
```

At minimum, set `OPENAI_API_KEY` before using question answering or message submission. The backend can start without it, but RAG-backed answers need it.

### Run The Backend Locally

Install Python dependencies:

```bash
uv sync
```

Start the API:

```bash
uv run uvicorn openagentlab.main:app --reload --host 0.0.0.0 --port 8000
```

Check the service:

```bash
curl http://localhost:8000/api/v1/health
```

API documentation is available from FastAPI at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Run The Full Local Stack

Start OpenAgentLab, PostgreSQL, Qdrant, Langfuse, ClickHouse, Redis, and MinIO:

```bash
docker compose up -d --build
```

Useful local endpoints:

- OpenAgentLab API: `http://localhost:8000`
- API health: `http://localhost:8000/api/v1/health`
- API readiness: `http://localhost:8000/api/v1/ready`
- FastAPI docs: `http://localhost:8000/docs`
- Qdrant API and dashboard: `http://localhost:6333`
- Qdrant gRPC: `localhost:6334`
- Langfuse: `http://localhost:3000`
- MinIO API for Langfuse blob storage: `http://localhost:9090`
- MinIO console: `http://localhost:9091`

Inspect or stop the stack:

```bash
docker compose ps
docker compose logs -f
docker compose down
```

`docker compose down` keeps named volumes. Use `docker compose down -v` only when you want to remove local persisted data.

### Run Database Migrations

When using PostgreSQL-backed services, apply migrations from the repository root:

```bash
uv run alembic upgrade head
```

## Web Client

The web client lives in `apps/web`. It submits multipart message requests to the backend, supports file attachments, lists recent workflow runs, and opens workflow details.

Start the backend first, then run the client:

```bash
cd apps/web
bun install
bun run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

Useful web commands:

```bash
bun run test
bun run build
```

## API Surface

Current v1 endpoints:

`GET /`, `GET /api/v1/health`, and `GET /api/v1/ready` are public and return
only minimal service/readiness metadata. Data-bearing endpoints below require the
configured authentication boundary. Local development may use `AUTH_MODE=disabled`
to map requests to one local development user; production-like environments must
use standards-based OIDC JWT validation.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Basic service health |
| `GET` | `/api/v1/ready` | Readiness check |
| `POST` | `/api/v1/documents` | Upload a supported document |
| `GET` | `/api/v1/documents` | List logical documents and linked file metadata |
| `POST` | `/api/v1/questions` | Ask a question, optionally scoped to document IDs |
| `POST` | `/api/v1/messages` | Submit or continue a persistent conversation message |
| `GET` | `/api/v1/sessions` | List reusable conversation sessions |
| `GET` | `/api/v1/sessions/{session_id}` | Fetch one session with ordered messages |
| `GET` | `/api/v1/workflows` | List recent workflow runs |
| `GET` | `/api/v1/workflows/{workflow_id}` | Inspect workflow execution status |

Example document upload:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -F "file=@example.pdf" \
  http://localhost:8000/api/v1/documents
```

Successful uploads store the original bytes through the configured storage backend, create owner-scoped PostgreSQL `documents` and `file_metadata` rows, and synchronously attempt deterministic extraction, chunking, embedding, and Qdrant indexing for PDF, TXT, Markdown, CSV, JSON, DOCX, and XLSX files. The response includes the logical `document_id`, final lifecycle `status` (`indexed` or `failed` after the indexing attempt), normalized extension, file size, checksum, timestamps, and safe indexing failure details. Storage keys/backend references remain internal metadata. Scanned or encrypted PDFs, malformed structured files, corrupt Office files, and empty documents fail safely without deleting the original file or metadata.

Example question:

```bash
curl -X POST http://localhost:8000/api/v1/questions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the key points?","document_ids":["00000000-0000-4000-8000-000000000000"]}'
```

Persisted-document question answering is strictly scoped to explicit logical
document IDs owned by the authenticated user. The API validates each ID against
PostgreSQL, only queries documents whose lifecycle status is `indexed`, retrieves
Qdrant chunks with both logical `document_id` and local `user_id` filters, and
returns structured citations derived from the retrieved chunks. Documents in
`uploaded` or `processing` return `not_ready`;
documents in `failed` return `indexing_failed`; indexed documents with no
retrieved evidence return `no_evidence` without calling the response model.

Example message submission:

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Authorization: Bearer $TOKEN" \
  -F "message=Summarize this file" \
  -F "files=@example.pdf"
```

If `session_id` is omitted, the backend creates a reusable PostgreSQL
conversation session and returns it with `user_message_id`,
`assistant_message_id`, `workflow_id`, answer status, citations, and sources.
Follow-up messages can send the same `session_id`; the backend loads bounded
recent history from PostgreSQL and routes the request. Simple factual and
summarization questions use the direct RAG/attachment QA fast path. Explicit
comparison, gap analysis, contradiction/duplicate detection, table/report
creation, requirements extraction, and CSV/XLSX-style structured-data requests
use the LangGraph orchestration path with registered deterministic document
capabilities. Messages may also include repeated `document_ids` to scope
persisted document retrieval. Conversation tables store text turns and logical
Document/FileMetadata references only, never raw file bytes.

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -F "session_id=00000000-0000-4000-8000-000000000001" \
  -F "document_ids=00000000-0000-4000-8000-000000000002" \
  -F "message=How does that change the recommendation?"
```

## Configuration

Settings are loaded from environment variables and `.env` through `pydantic-settings`.

Common variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | Async SQLAlchemy database URL | unset |
| `OPENAI_API_KEY` | OpenAI API key for RAG and generation | unset |
| `QDRANT_URL` | Qdrant endpoint | unset |
| `QDRANT_COLLECTION_NAME` | Vector collection name | `openagentlab_rag_chunks` |
| `OPENAI_PLANNER_MODEL` | Planner model | `gpt-4o-mini` |
| `OPENAI_RESPONSE_MODEL` | Response model | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `OPENAGENTLAB_TOOL_SELECTOR_MODEL` | Tool selector model | `gpt-4.1-mini` |
| `RAG_CHUNK_SIZE` | Chunk size for indexing | `800` |
| `RAG_CHUNK_OVERLAP` | Chunk overlap for indexing | `100` |
| `RAG_RETRIEVAL_TOP_K` | Retrieved chunks per document query | `5` |
| `RAG_CONTEXT_MAX_CHARS` | Final evidence context character budget | `12000` |
| `CONVERSATION_HISTORY_MAX_TURNS` | Prior conversation turns loaded for `/messages` | `6` |
| `CONVERSATION_HISTORY_MAX_CHARS` | Character budget for loaded conversation history | `4000` |
| `STORAGE_BACKEND` | Storage provider, `local` or `azure_blob` | `local` |
| `LOCAL_STORAGE_ROOT` | Local file storage path | `storage` |
| `AUTH_MODE` | `disabled`, `dev_jwt`, or `oidc`; production requires `oidc` | `disabled` |
| `AUTH_OIDC_ISSUER` | Trusted JWT issuer when `AUTH_MODE=oidc` | unset |
| `AUTH_OIDC_AUDIENCE` | Expected JWT audience when `AUTH_MODE=oidc` | unset |
| `AUTH_OIDC_JWKS_URL` | OIDC JWKS endpoint, unless `AUTH_OIDC_JWKS_JSON` is used | unset |
| `CORS_ALLOWED_ORIGINS` | Comma-separated browser origins allowed for CORS | unset |
| `LANGFUSE_ENABLED` | Enable Langfuse callbacks | `false` |

See `.env.example` for the complete local development configuration.

### Local And Azure Configuration Matrix

| Mode | Required application settings |
| --- | --- |
| Local Python | `DATABASE_URL`, `QDRANT_URL`, `OPENAI_API_KEY`, `STORAGE_BACKEND=local`, `LOCAL_STORAGE_ROOT` |
| Docker Compose | Same canonical app settings; Compose wires `DATABASE_URL` to `postgres`, `QDRANT_URL` to `qdrant`, and `LOCAL_STORAGE_ROOT=/app/storage` |
| Azure Container Apps | `DATABASE_URL`, `QDRANT_URL`, `OPENAI_API_KEY`, `AUTH_MODE=oidc`, OIDC issuer/audience/JWKS settings, `STORAGE_BACKEND=azure_blob`, `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME`; optional `AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID` for user-assigned identity |
| Optional Langfuse | `LANGFUSE_ENABLED=true`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_BASE_URL` or `LANGFUSE_HOST` |

Migrations are run explicitly, not by every application replica:

```bash
uv run alembic upgrade head
docker compose run --rm openagentlab uv run alembic upgrade head
```

For Azure, run the same Alembic command as a one-off deployment job/command
using the target environment settings, then deploy or restart app replicas.
See `deployment/README.md` for the full configuration matrix and troubleshooting
table.

### Observability

Langfuse tracing is optional and disabled by default. When
`LANGFUSE_ENABLED=true` and Langfuse project keys are configured, OpenAgentLab
creates correlated traces for real runtime workflows:

- `document.upload_index`: storage write, PostgreSQL document/file metadata
  persistence, storage read, extraction, chunking, embeddings, Qdrant
  delete/upsert, and final document lifecycle status.
- `message.workflow`: session resolution, bounded history loading, document
  reference loading, attachment storage/extraction, user/assistant message
  persistence, route selection, direct RAG or LangGraph invocation, and
  workflow completion.
- `message.direct_rag` and `message.langgraph`: workflow execution rows,
  route metadata, document lifecycle validation, retrieval/context metrics,
  graph invocation, generation, and final status.

Workflow executions created for question answering and LangGraph orchestration
persist the Langfuse trace reference in `workflow_executions.trace_id`, which is
returned by the workflow status APIs. Telemetry payloads are intentionally
bounded to operational metadata such as workflow IDs, session IDs, message IDs,
routes, document IDs, counts, statuses, model names, and provider usage. Raw
file bytes, extracted document text, full chat history, storage keys, local
paths, credentials, and unbounded prompts are not sent through the application
observability helpers. Observability failures are logged at debug level and do
not fail user workflows.

## Tests And Quality

Run all Python tests:

```bash
uv run pytest
```

Run a focused test module:

```bash
uv run pytest tests/unit/test_messages_api.py
```

Run format and lint checks:

```bash
uv run black --check .
uv run ruff check .
```

Run the isolated end-to-end workflow suite with disposable PostgreSQL/Qdrant
and deterministic model doubles:

```bash
bash scripts/run_e2e.sh
```

Evaluation dependencies are in the `evaluation` dependency group:

```bash
uv sync --group evaluation
```

The evaluation package includes DeepEval and Ragas adapters, threshold configuration, dataset loading, static smoke validation, and an opt-in live runtime evaluation command under `src/openagentlab/evaluation`.

Static evaluation validates checked-in JSONL observations:

```bash
uv run python -m openagentlab.evaluation validate --dataset evaluation/datasets/smoke.jsonl --tags smoke
```

Live runtime evaluation is intentionally disabled unless you set
`RUN_LIVE_EVALUATION=1` and provide OpenAI, PostgreSQL, and Qdrant:

```bash
RUN_LIVE_EVALUATION=1 uv run --group evaluation python -m openagentlab.evaluation live-deepeval --dataset evaluation/datasets/live_smoke.jsonl --tags live smoke --max-cases 1 --include-report-text
```

See `evaluation/README.md` for prerequisites, report output, and cost controls.

## Documentation

Documentation is organized into three areas:

- `docs/architecture/`: vision, personas, requirements, system design, API design, database design, workflow architecture, and tool contracts
- `docs/ADR/`: architecture decision records for platform, persistence, infrastructure, and quality decisions
- `docs/engineering/`: design-first, observability, and evaluation-first engineering practices

Start with:

- `docs/readme.md`
- `docs/architecture/readme.md`
- `docs/ADR/readme.md`
- `docs/engineering/readme.md`

## Deployment Direction

OpenAgentLab is packaged as a Docker image. The production direction is a stateless container app backed by managed services:

- Azure Container Apps for the API container
- Azure PostgreSQL for structured application state and metadata
- Azure Blob Storage for uploaded files and generated artifacts
- Qdrant Cloud for vector search
- Langfuse for optional LLM observability

The local Docker Compose stack mirrors the main production dependencies while staying developer-friendly.

## Roadmap

Completed or in place:

- Design documentation and ADRs
- FastAPI backend foundation
- Docker and Docker Compose development stack
- PostgreSQL, SQLAlchemy, Alembic data layer
- Logical document upload, lifecycle metadata, listing, and storage abstraction
- Deterministic document readers for PDF, Excel, CSV, TXT, JSON, and DOCX
- RAG loaders, chunking, embeddings, Qdrant vector store, retrieval, and context builder
- LangGraph-oriented agent components
- Workflow persistence, status lookup, and recent-run APIs
- UI message submission API with attachments
- React/Vite workflow client
- Langfuse observability hooks
- DeepEval and Ragas evaluation scaffolding

Planned next work:

- Production dashboards and alerting
- Larger golden datasets
- Tenant/organization roles and sharing
- Streaming responses
- Richer artifact handling
- Production Azure deployment hardening
- OpenTelemetry integration
- MCP support
- Plugin architecture
- Multi-agent workflows

## Current Status

This project is under active development. The backend, RAG infrastructure, agent components, workflow persistence, document-processing tools, local infrastructure, observability hooks, evaluation scaffolding, authentication/user ownership foundation, and web client are present. Remaining work is focused on operational hardening, production deployment, richer evaluation datasets, tenant/organization roles, streaming, and broader workflow capabilities.

## License

This project is licensed under the GNU Affero General Public License v3.0. See `LICENSE`.

## Acknowledgements

OpenAgentLab is inspired by modern AI engineering practices and the open-source ecosystem, including FastAPI, LangGraph, OpenAI, Qdrant, Langfuse, PostgreSQL, Docker, DeepEval, and Ragas.
