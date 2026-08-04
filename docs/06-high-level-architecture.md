# High-Level Architecture

> This document describes the internal architecture of OpenAgentLab.
>
> It defines the major containers and responsibilities of the platform without specifying implementation details.
>
> This document corresponds to **C4 Model – Level 2 (Container Diagram)**.

---

# Traceability

## Inputs

- 05-system-context.md

## Outputs

- 07-agent-architecture.md
- 08-tool-specification.md
- 09-api-specification.md
- 10-database-design.md

---

# Architectural Philosophy

OpenAgentLab is not a chatbot.

It is an AI orchestration platform where Large Language Models coordinate deterministic tools to solve analytical tasks.

The LLM makes decisions.

Deterministic tools perform computations.

---

# Core Containers

## 1. Web API

Technology

FastAPI

Responsibilities

- REST API
- Authentication (future)
- Session handling
- Request validation
- File upload

---

## 2. Agent Layer

Technology

LangGraph

Responsibilities

- intent understanding
- planning
- workflow orchestration
- tool selection
- reasoning
- execution coordination

This layer contains no business logic.

It coordinates other services.

---

## 3. Tool Layer

Responsibilities

Execute deterministic operations.

Examples

- PDF Reader
- Spreadsheet Analyzer
- CSV Analyzer
- Python Executor
- Report Generator

Tools should be:

- stateless
- deterministic
- independently testable

---

## 4. Retrieval Layer

Responsibilities

- embedding generation
- vector search
- context retrieval

Primary technologies

- OpenAI Embeddings
- Qdrant

---

## 5. Data Layer

Responsibilities

Persistent storage.

Contains:

- metadata
- sessions
- uploaded sources
- execution history

Technology

PostgreSQL

---

## 6. File Storage

Responsibilities

Store uploaded files.

Initial implementation:

Local filesystem.

Future:

Azure Blob Storage
S3-compatible storage

---

## 7. Observability Layer

Responsibilities

Capture:

- traces
- latency
- prompts
- tool execution
- token usage
- workflow execution

Technology

Langfuse

Future

OpenTelemetry

---

## 8. Evaluation Layer

Responsibilities

Evaluate:

- retrieval quality
- answer quality
- tool selection
- workflow quality

Technology

- DeepEval
- Ragas

---

# High-Level Request Flow

1.

User uploads files

↓

2.

FastAPI receives request

↓

3.

Metadata stored

↓

4.

Documents processed

↓

5.

Embeddings generated

↓

6.

Stored in Qdrant

↓

7.

User asks question

↓

8.

Agent plans workflow

↓

9.

Retriever gathers evidence

↓

10.

Agent selects tools

↓

11.

Tools execute

↓

12.

Agent synthesizes response

↓

13.

Execution stored

↓

14.

Response returned

---

# Layer Dependencies

Presentation

↓

Agent

↓

Tools

↓

Retrieval

↓

Persistence

Each layer communicates only with adjacent layers whenever practical.

This minimizes coupling and simplifies maintenance.

---

# Architectural Constraints

The architecture shall satisfy the following constraints:

- LLMs never perform deterministic computations.
- Tools remain independently testable.
- Business logic does not reside inside prompts.
- Retrieval is performed before answer generation whenever external knowledge is required.
- Every workflow should be observable.
- Every answer should be traceable.
- Components should be replaceable with minimal changes.

---

# Scalability Strategy

Future scaling should primarily occur horizontally.

Examples include:

- multiple API instances
- dedicated embedding workers
- separate retrieval services
- distributed tool execution
- Kubernetes deployment

No redesign should be required to support these extensions.

---

# Technology Mapping

| Layer | Initial Technology |
|----------|-------------------|
| API | FastAPI |
| Agent | LangGraph |
| LLM | OpenAI |
| Embeddings | OpenAI |
| Vector Store | Qdrant |
| Database | PostgreSQL |
| File Storage | Local Storage |
| Observability | Langfuse |
| Evaluation | DeepEval, Ragas |
| CI/CD | GitHub Actions |
| Deployment | Docker, Docker Compose, Azure |

---

# Architecture Principles

OpenAgentLab follows these principles:

- Separation of Concerns
- Single Responsibility
- Dependency Inversion
- Human-in-the-loop
- Explainability
- Observability by Design
- Evaluation by Design
- Production-first Engineering

These principles guide every architectural decision throughout the project.