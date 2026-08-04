# Database Design

> This document defines the persistence architecture of OpenAgentLab.
>
> Rather than relying on a single database, OpenAgentLab uses multiple specialized storage systems.
>
> Each storage technology is responsible for a specific type of data.

---

# Traceability

## Inputs

- 03-functional-requirements.md
- 06-high-level-architecture.md
- 10-api-specification.md

## Outputs

- PostgreSQL Schema
- Qdrant Collections
- ORM Models
- Database Migrations

---

# Persistence Philosophy

OpenAgentLab separates data according to its characteristics.

| Storage | Responsibility |
|----------|----------------|
| PostgreSQL | Structured relational data |
| Qdrant | Vector embeddings |
| Local Storage | Uploaded files |
| Langfuse | Traces and observability |

This separation improves scalability, maintainability, and performance.

---

# Persistence Overview

```text
                    OpenAgentLab

                          │

        ┌─────────────────┼──────────────────┐

        │                 │                  │

 PostgreSQL          Qdrant            Local Storage

        │                 │                  │

 Metadata          Embeddings          Uploaded Files

        │

   Langfuse

Execution Traces
```

---

# PostgreSQL Schema

The relational database stores application metadata.

Main entities:

- Session
- File
- Workflow
- ToolExecution
- Report

---

# Entity: Session

Purpose

Represents a user analysis session.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| created_at | Timestamp |
| updated_at | Timestamp |
| status | Enum |

Relationships

One Session

↓

Many Files

↓

Many Workflows

---

# Entity: File

Purpose

Represents an uploaded document.

Fields

| Field | Type |
|--------|------|
| id | UUID |
| session_id | UUID |
| filename | String |
| file_type | Enum |
| storage_path | String |
| checksum | String |
| uploaded_at | Timestamp |

Relationships

Many Files

↓

One Session

---

# Entity: Workflow

Purpose

Represents a completed analytical workflow.

Fields

| Field | Type |
|--------|------|
| id | UUID |
| session_id | UUID |
| question | Text |
| status | Enum |
| started_at | Timestamp |
| completed_at | Timestamp |

Relationships

One Workflow

↓

Many Tool Executions

---

# Entity: ToolExecution

Purpose

Stores every deterministic tool execution.

Fields

| Field | Type |
|--------|------|
| id | UUID |
| workflow_id | UUID |
| tool_name | String |
| execution_time_ms | Integer |
| status | Enum |
| trace_id | UUID |

---

# Entity: Report

Purpose

Generated reports.

Fields

| Field | Type |
|--------|------|
| id | UUID |
| workflow_id | UUID |
| format | Enum |
| location | String |
| generated_at | Timestamp |

---

# Entity Relationship Diagram

```text
Session

│

├──────────────┐

│              │

Files      Workflows

               │

               │

        ToolExecutions

               │

               │

           Reports
```

---

# PostgreSQL Indexing

Recommended indexes:

Session

- created_at

File

- session_id
- file_type

Workflow

- session_id
- status

ToolExecution

- workflow_id
- tool_name

---

# Qdrant Design

Purpose

Store semantic embeddings.

Collection

documents

Payload

```json
{
  "file_id": "...",
  "page": 2,
  "chunk": 14,
  "session_id": "...",
  "document_type": "pdf"
}
```

Vector

```
1536 dimensions
```

(OpenAI embedding model)

---

# Chunk Strategy

Initial Strategy

- Recursive Character Splitter

Chunk Size

```
1000 characters
```

Overlap

```
200 characters
```

Future strategies may include:

- Semantic chunking
- Markdown chunking
- Table-aware chunking

---

# Local File Storage

Purpose

Store uploaded source files.

Example

```
storage/

    session_id/

        document.pdf

        budget.xlsx

        sales.csv
```

The database stores only metadata.

---

# Langfuse Storage

Langfuse stores:

- prompt traces
- workflow traces
- token usage
- latency
- LLM costs

The application stores only the Langfuse Trace ID.

---

# Data Lifecycle

Upload

↓

Metadata

↓

Store File

↓

Extract Text

↓

Generate Embeddings

↓

Store Vector

↓

Answer Questions

↓

Generate Report

↓

Persist Workflow

---

# Soft Delete Strategy

Files should not be physically removed immediately.

Recommended fields:

```
deleted_at

is_deleted
```

This simplifies recovery and auditing.

---

# Migration Strategy

Schema evolution shall use:

Alembic

Migration principles:

- forward-only migrations
- reproducible environments
- version-controlled schema

---

# ORM Strategy

ORM

SQLAlchemy 2.x

Model style

Declarative

Primary Key

UUID

Relationships

Lazy loading where appropriate.

---

# Future Database Extensions

Future versions may introduce:

- User entity
- Team entity
- Shared workspaces
- Conversation history
- Evaluation datasets
- Tool registry
- MCP registry

These additions should require minimal schema changes.

---

# Database Design Principles

The persistence layer follows these principles:

- Separation of Concerns
- Single Source of Truth
- Immutable execution history
- Metadata over file duplication
- Retrieval optimized for semantic search
- Production-ready schema evolution