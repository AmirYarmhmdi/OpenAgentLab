# API Specification

> This document defines the public REST API of OpenAgentLab.
>
> The API follows a **Design First** approach. Endpoints are specified before implementation to ensure consistency, testability, and maintainability.
>
> All endpoints exchange JSON unless otherwise specified.

---

# Traceability

## Inputs

- 03-functional-requirements.md
- 06-high-level-architecture.md
- 08-tool-specification.md
- 09-tool-contracts.md

## Outputs

- FastAPI Implementation
- OpenAPI Specification
- Integration Tests
- SDK Generation

---

# API Design Principles

The API shall:

- be RESTful
- use JSON
- expose deterministic endpoints
- provide consistent error responses
- support versioning
- remain stateless
- be fully documented

---

# Base URL

```
/api/v1
```

---

# Authentication

## MVP

Authentication is outside the MVP scope.

Future versions may support:

- OAuth2
- JWT
- Azure Entra ID
- API Keys

---

# Common Response Format

## Success

```json
{
  "status": "success",
  "data": {}
}
```

---

## Error

```json
{
  "status": "error",
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "Requested file does not exist."
  }
}
```

---

# Resource Model

OpenAgentLab exposes the following resources:

- Sessions
- Files
- Questions
- Workflows
- Reports
- Traces

---

# Session API

## Create Session

POST

```
/sessions
```

Response

```json
{
  "session_id": "uuid"
}
```

---

## Get Session

GET

```
/sessions/{session_id}
```

---

## Delete Session

DELETE

```
/sessions/{session_id}
```

---

# File API

## Upload File

POST

```
/files
```

Content-Type

```
multipart/form-data
```

Supported formats

- PDF
- XLSX
- CSV

Response

```json
{
  "file_id": "...",
  "filename": "...",
  "type": "pdf",
  "status": "uploaded"
}
```

---

## List Uploaded Files

GET

```
/sessions/{session_id}/files
```

---

## Get File Metadata

GET

```
/files/{file_id}
```

---

## Delete File

DELETE

```
/files/{file_id}
```

---

# Question API

## Ask Question

POST

```
/questions
```

Request

```json
{
  "session_id": "...",
  "question": "Compare these two reports."
}
```

Response

```json
{
  "answer": "...",
  "workflow_id": "...",
  "trace_id": "...",
  "citations": []
}
```

---

# Workflow API

## Get Workflow

GET

```
/workflows/{workflow_id}
```

Response

```json
{
  "status": "completed",
  "steps": [],
  "tools": []
}
```

---

## List Workflow Steps

GET

```
/workflows/{workflow_id}/steps
```

---

# Evidence API

## Get Retrieved Evidence

GET

```
/workflows/{workflow_id}/evidence
```

Response

```json
{
  "chunks": [],
  "sources": []
}
```

---

# Tool API

## List Available Tools

GET

```
/tools
```

Response

```json
[
  {
    "name": "document_reader",
    "category": "document"
  }
]
```

---

## Get Tool Metadata

GET

```
/tools/{tool_name}
```

---

# Report API

## Generate Report

POST

```
/reports
```

Request

```json
{
  "workflow_id": "...",
  "format": "markdown"
}
```

Supported formats

- markdown

Future

- pdf
- docx

---

## Download Report

GET

```
/reports/{report_id}
```

---

# Trace API

## Get Execution Trace

GET

```
/traces/{trace_id}
```

Response

```json
{
  "events": [],
  "tools": [],
  "latency": {},
  "llm_calls": []
}
```

---

# Evaluation API

## Run Evaluation

POST

```
/evaluation/run
```

Response

```json
{
  "evaluation_id": "...",
  "status": "started"
}
```

---

## Get Evaluation Results

GET

```
/evaluation/{evaluation_id}
```

---

# Health API

## Health Check

GET

```
/health
```

Response

```json
{
  "status": "healthy"
}
```

---

# Error Codes

| Code | Meaning |
|--------|----------|
| FILE_NOT_FOUND | Uploaded file not found |
| INVALID_FILE | Unsupported format |
| EMPTY_DOCUMENT | No readable content |
| INVALID_REQUEST | Invalid request payload |
| TOOL_FAILURE | Tool execution failed |
| VECTOR_DB_ERROR | Retrieval failed |
| LLM_ERROR | Model request failed |
| INTERNAL_ERROR | Unexpected server error |

---

# HTTP Status Codes

| Status | Usage |
|----------|-------|
| 200 | Success |
| 201 | Resource created |
| 400 | Invalid request |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation failed |
| 500 | Internal error |

---

# API Versioning

The API follows URI versioning.

Example

```
/api/v1/questions
```

Future breaking changes shall introduce a new version.

```
/api/v2/...
```

---

# Pagination

Endpoints returning collections should support:

```
?page=1

&page_size=20
```

Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 145
}
```

---

# Idempotency

The following operations are idempotent:

- GET
- DELETE

POST endpoints creating resources are not idempotent unless an Idempotency-Key is provided in future versions.

---

# Rate Limiting

Not implemented in MVP.

Future implementation may include:

- per-user quotas
- API keys
- request throttling

---

# OpenAPI Compatibility

The API is designed to generate a complete OpenAPI 3.1 specification.

Future implementation should automatically expose:

```
/docs
```

Swagger UI

and

```
/openapi.json
```

OpenAPI Schema

---

# API Design Philosophy

The REST API is intentionally thin.

Business logic does not reside in the API layer.

The API is responsible for:

- validation
- serialization
- routing
- authentication (future)

Application logic resides inside the Agent and Tool layers.

This separation keeps the API stable while allowing the internal AI workflow to evolve independently.