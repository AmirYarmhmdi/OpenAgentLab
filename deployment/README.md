# Deployment Configuration

OpenAgentLab is configuration-driven. The same container image can run locally,
under Docker Compose, in Azure Container Apps, or in another provider-neutral
runtime as long as the application environment variables are supplied.

This repository does not provision or mutate live cloud resources. Treat this
document as the runtime contract for deployment assets and release runbooks.

## Application Settings

These names are consumed by `openagentlab.core.config.Settings`.

| Variable | Local default | Azure Container Apps | Notes |
| --- | --- | --- | --- |
| `APP_NAME` | `OpenAgentLab` | optional | Display name only. |
| `APP_VERSION` | `0.1.0` | image/release version | Safe to log. |
| `ENVIRONMENT` | `development` | `production` or environment name | Safe to log. |
| `DEBUG` | `false` | `false` | Do not enable in production. |
| `API_V1_PREFIX` | `/api/v1` | `/api/v1` | API routing prefix. |
| `LOG_LEVEL` | `INFO` | `INFO` | No secrets are logged by config diagnostics. |
| `HOST` | `0.0.0.0` | `0.0.0.0` | Uvicorn binding. |
| `PORT` | `8000` | `8000` | Container port. |
| `DATABASE_URL` | local PostgreSQL URL | required secret | Async SQLAlchemy URL. |
| `OPENAI_API_KEY` | developer secret | required secret | Required for embeddings, planning, response generation. |
| `QDRANT_URL` | `http://localhost:6333` | required | Qdrant endpoint. |
| `QDRANT_API_KEY` | empty | secret if Qdrant requires it | Optional for unauthenticated local Qdrant. |
| `QDRANT_COLLECTION_NAME` | `openagentlab_rag_chunks` | required | Must not be empty. |
| `OPENAI_PLANNER_MODEL` | `gpt-4o-mini` | required | Planner model. |
| `OPENAI_RESPONSE_MODEL` | `gpt-4o-mini` | required | Response model. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | required | Embedding model. |
| `OPENAGENTLAB_TOOL_SELECTOR_MODEL` | `gpt-4.1-mini` | required | Tool selector model. |
| `RAG_EMBEDDING_DIMENSION` | `1536` | required | Must match embedding model/vector collection. |
| `RAG_CHUNK_SIZE` | `800` | required | Positive integer. |
| `RAG_CHUNK_OVERLAP` | `100` | required | Must be smaller than `RAG_CHUNK_SIZE`. |
| `RAG_RETRIEVAL_TOP_K` | `5` | required | Positive integer. |
| `RAG_CONTEXT_MAX_CHARS` | `12000` | required | Positive integer. |
| `CONVERSATION_HISTORY_MAX_TURNS` | `6` | required | `0` disables prior turns. |
| `CONVERSATION_HISTORY_MAX_CHARS` | `4000` | required | Positive integer. |
| `MAX_UPLOAD_BYTES` | `10485760` | required | Upload limit in bytes. |
| `STORAGE_BACKEND` | `local` | `azure_blob` recommended | Allowed: `local`, `azure_blob`. |
| `LOCAL_STORAGE_ROOT` | `storage` | unused in Azure Blob mode | Local-only writable path. |
| `AZURE_STORAGE_ACCOUNT_NAME` | empty | required for Azure Blob | Not required for local storage. |
| `AZURE_STORAGE_CONTAINER_NAME` | empty | required for Azure Blob | Not required for local storage. |
| `AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID` | empty | optional | Set only for user-assigned managed identity. |
| `LANGFUSE_ENABLED` | `false` | optional | Langfuse remains optional. |
| `LANGFUSE_PUBLIC_KEY` | empty | required only if enabled | Secret/config value from Langfuse project. |
| `LANGFUSE_SECRET_KEY` | empty | required only if enabled | Secret. |
| `LANGFUSE_BASE_URL` | `http://localhost:3000` | Langfuse endpoint if enabled | Used by Langfuse SDK. |
| `LANGFUSE_HOST` | `http://localhost:3000` | optional alias | Used as fallback for base URL. |

Evaluation settings are also in `Settings`, but they are used by evaluation
runners rather than the serving API.

## Storage Modes

| Mode | Required variables | Behavior |
| --- | --- | --- |
| Local filesystem | `STORAGE_BACKEND=local`, `LOCAL_STORAGE_ROOT` | Original uploaded files are stored under the configured writable directory. Docker Compose mounts `/app/storage` to a named volume. |
| Azure Blob, managed identity | `STORAGE_BACKEND=azure_blob`, `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME` | Original uploaded files are read/written through Azure Blob Storage. Omit `AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID` for the default identity. |
| Azure Blob, user-assigned identity | Azure Blob variables above plus `AZURE_STORAGE_MANAGED_IDENTITY_CLIENT_ID` | Uses the supplied managed identity client id. |

Azure-specific settings are not required in local mode. Local filesystem paths
are not required in Azure Blob mode.

## Migration Strategy

Migrations are external to application replica startup. Do not run Alembic in
every app container replica.

Local migration:

```bash
uv run alembic upgrade head
```

Docker Compose migration:

```bash
docker compose run --rm openagentlab uv run alembic upgrade head
```

Azure deployment-oriented procedure:

1. Build and publish the OpenAgentLab image.
2. Ensure the target database and secrets/configuration exist.
3. Run one explicit migration command/job using the same image and production
   settings:

   ```bash
   uv run alembic upgrade head
   ```

4. After the migration succeeds, roll out or restart application replicas.

The checked-in `Dockerfile` starts only Uvicorn. It does not run migrations.

## Local-to-Cloud Sequence

1. Validate locally:

   ```bash
   uv run pytest tests/unit/test_settings.py tests/unit/test_configuration_parity.py
   uv run alembic upgrade head
   uv run uvicorn openagentlab.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Validate the local container stack:

   ```bash
   docker compose up -d --build
   docker compose run --rm openagentlab uv run alembic upgrade head
   curl http://127.0.0.1:8000/api/v1/health
   curl http://127.0.0.1:8000/api/v1/ready
   ```

3. Validate end-to-end runtime parity with disposable local services:

   ```bash
   bash scripts/run_e2e.sh
   ```

   This does not use Azure, production data, live OpenAI, or live Langfuse.

4. Configure Azure Container Apps with the Azure matrix above.
5. Run the one-off deployment migration command/job.
6. Deploy or restart the app revision.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Startup fails with `STORAGE_BACKEND` validation | Unknown backend or missing local root | Use `local` or `azure_blob`; set `LOCAL_STORAGE_ROOT` for local mode. |
| Startup fails with Azure storage settings | Blob mode missing account/container | Set `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_CONTAINER_NAME`. |
| Upload works locally but fails in Azure | Local storage selected in cloud | Set `STORAGE_BACKEND=azure_blob` and configure managed identity access. |
| Questions fail with Qdrant unavailable | `QDRANT_URL` missing or unreachable | Set the correct internal/cloud Qdrant endpoint and key if required. |
| Model calls fail | `OPENAI_API_KEY` missing | Configure the secret in the runtime environment. |
| Langfuse disabled despite being intended | Missing project keys | Set `LANGFUSE_ENABLED=true`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY`. |
| Multiple replicas race migrations | Alembic run in app startup | Remove startup migration hooks and use a one-off migration job/command. |
