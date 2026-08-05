<div align="center">
  <img src="docs/images/logo.png" alt="OpenAgentLab Logo" width="400">
</div>

# OpenAgentLab

> A production-oriented AI platform for document understanding, retrieval, and intelligent workflow orchestration.

OpenAgentLab is an open-source AI Engineering project that demonstrates how to design, build, evaluate, and deploy modern AI applications using production-grade software engineering practices.

Rather than being a simple chatbot, OpenAgentLab is designed as an extensible platform where an AI Agent orchestrates deterministic tools to answer questions over structured and unstructured documents.

The project follows a **Design First** philosophy, with architecture and engineering decisions documented before implementation.

---

## Key Features

- 📄 Upload PDF documents
- 📊 Upload Excel workbooks
- 📈 Upload CSV datasets
- 💬 Ask natural language questions
- 🤖 AI Agent plans the execution workflow
- 🛠 Intelligent Tool Calling
- 🔍 Retrieval-Augmented Generation (RAG)
- 📚 Multi-document reasoning
- 📑 Structured report generation
- 📡 Production-grade observability
- ✅ Automated AI evaluation

---

# Architecture Overview

```
                +----------------------+
                |      REST API        |
                |      FastAPI         |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      LangGraph       |
                |   Agent Workflow     |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
  PDF Reader        Excel Reader       CSV Reader
        |                  |                  |
        +---------+--------+------------------+
                  |
                  v
            Retrieval Layer
        (Embeddings + Qdrant)
                  |
                  v
              OpenAI LLM
                  |
                  v
           Response Generation
```

---

# Technology Stack

## MVP

The first version of OpenAgentLab is intentionally focused on a modern production AI stack.

| Category | Technology |
|-----------|------------|
| Backend | FastAPI |
| Workflow Engine | LangGraph |
| LLM | OpenAI |
| Tool Calling | OpenAI Tool Calling |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| Vector Extension | pgvector |
| Storage | Local Storage |
| Containerization | Docker |
| Local Orchestration | Docker Compose |
| Observability | Langfuse |
| AI Evaluation | DeepEval |
| RAG Evaluation | Ragas |
| CI | GitHub Actions |
| Cloud | Microsoft Azure |

---

# Planned Phase 2

The architecture has been designed to support additional production capabilities without major refactoring.

| Capability | Purpose |
|------------|---------|
| OpenTelemetry | Distributed tracing and metrics |
| Kubernetes | Container orchestration |
| Promptfoo | Prompt regression testing |
| MCP (Model Context Protocol) | Standardized AI tool integration |
| Azure DevOps *(optional)* | Enterprise CI/CD pipelines |
| Arize Phoenix *(optional)* | Advanced LLM observability and evaluation |

These technologies are intentionally planned for a later phase to keep the MVP focused while maintaining a clear evolution path.

---

# Repository Structure

```
OpenAgentLab/

├── app/
├── tests/
├── docs/
│
├── architecture/
├── ADR/
├── engineering/
│
├── docker/
├── scripts/
├── storage/
├── alembic/
├── .github/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

# Documentation

The project documentation is organized into three sections.

## Architecture

System design and technical specifications.

- Vision
- Personas
- User Stories
- Requirements
- Architecture
- API Design
- Database Design

## Architecture Decision Records (ADR)

Documents the reasoning behind architectural decisions.

Examples include:

- Why FastAPI?
- Why LangGraph?
- Why Qdrant?
- Why Docker?

## Engineering

Development practices and engineering principles.

- Design First
- Observability by Design
- Evaluation First

---

# Engineering Principles

OpenAgentLab follows several software engineering principles.

- Design First
- API First
- Evaluation First
- Observability by Design
- Clean Architecture
- SOLID Principles
- Separation of Concerns

---

# Project Roadmap

## Phase 1 — Architecture

- [x] Vision
- [x] Personas
- [x] User Stories
- [x] Requirements
- [x] Architecture
- [x] ADRs

---

## Phase 2 — Foundation

- [ ] FastAPI
- [ ] Docker
- [ ] Docker Compose
- [ ] PostgreSQL
- [ ] Alembic
- [ ] SQLAlchemy
- [ ] GitHub Actions

---

## Phase 3 — Document Management

- [ ] File Upload
- [ ] Storage Layer
- [ ] Metadata Management

---

## Phase 4 — AI Tools

- [ ] PDF Reader
- [ ] Excel Reader
- [ ] CSV Reader

---

## Phase 5 — RAG

- [ ] Embedding Pipeline
- [ ] Qdrant
- [ ] Retrieval
- [ ] Context Construction

---

## Phase 6 — Agent

- [ ] LangGraph
- [ ] Tool Calling
- [ ] Workflow Engine

---

## Phase 7 — Observability

- [ ] Langfuse
- [ ] Structured Logging
- [ ] Tracing

---

## Phase 8 — Evaluation

- [ ] DeepEval
- [ ] Ragas
- [ ] GitHub Actions Integration

---

## Phase 9 — Cloud Deployment

- [ ] Azure
- [ ] Production Deployment

---

# Future Roadmap

After the MVP, OpenAgentLab will continue evolving toward a production-grade AI platform.

Future milestones include:

- Kubernetes deployment
- OpenTelemetry integration
- Promptfoo regression testing
- MCP support
- Azure DevOps pipelines
- Arize Phoenix integration
- Multi-agent workflows
- Authentication & authorization
- Streaming responses
- Plugin architecture

---

# Current Status

🚧 This project is currently under active development.

The architecture and engineering documentation are complete.

Implementation is currently in progress.

---

# Contributing

Contributions, ideas, discussions, and feedback are welcome.

As the project evolves, contribution guidelines and development workflows will be published.

---

# License

This project is licensed under the MIT License.

---

# Acknowledgements

OpenAgentLab is inspired by modern AI Engineering practices and the open-source ecosystem, including:

- FastAPI
- LangGraph
- OpenAI
- Qdrant
- Langfuse
- PostgreSQL
- Docker