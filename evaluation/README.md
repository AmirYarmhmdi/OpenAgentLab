# Evaluation

OpenAgentLab owns a small, framework-neutral evaluation layer. Canonical datasets
live as JSONL records and can feed Ragas, DeepEval, or later evaluator adapters
without duplicating goldens. The checked-in smoke dataset currently covers RAG
context-building and agent tool-selection behavior.

## Dataset Format

Each JSONL line is one `EvaluationCase` with:

- `id`: stable case identifier
- `input`: user query or workflow input
- `expected_output`: reference answer when a metric needs one
- `actual_output`: observed answer for stored smoke/regression cases
- `expected_contexts`: gold contexts
- `retrieved_contexts`: contexts returned by the system under evaluation
- `metadata`: arbitrary JSON object
- `tags`: filterable labels
- optional tool fields: `expected_tool_name`, `expected_tool_arguments`,
  `expected_behavior`

Records are validated with a strict schema: unknown fields are rejected, blank
lines are ignored, duplicate IDs fail validation, string values are stripped, and
list-like fields must contain non-empty strings. Use `tags` to select a subset
of cases for local or CI runs.

## Local Commands

Validate the dataset without external API calls:

```bash
uv run python -m openagentlab.evaluation validate --dataset evaluation/datasets/smoke.jsonl
```

Validate only tagged smoke cases:

```bash
uv run python -m openagentlab.evaluation validate --dataset evaluation/datasets/smoke.jsonl --tags smoke
```

Run deterministic evaluation infrastructure tests:

```bash
uv run pytest tests/unit/evaluation
```

Run Ragas smoke evaluation after installing evaluation dependencies and setting
`OPENAI_API_KEY`:

```bash
uv run --group evaluation python -m openagentlab.evaluation ragas --dataset evaluation/datasets/smoke.jsonl --tags smoke
```

Run DeepEval regression tests:

```bash
uv run --group evaluation pytest -m evaluation tests/evaluation
```

The command-line entry point currently exposes `validate` and `ragas`. DeepEval
coverage runs through the pytest marker above.

## Thresholds

Thresholds are centralized in `Settings` and `EvaluationThresholds`. The initial
defaults are baseline values for early CI smoke runs and should be calibrated
against real production goldens:

- answer relevancy: `0.70` minimum
- faithfulness: `0.70` minimum
- context precision: `0.70` minimum
- context recall: `0.70` minimum
- hallucination: `0.30` maximum

## CI

The main CI workflow owns linting, formatting, unit tests, integration tests,
and Docker builds. The separate evaluation workflow owns evaluation-specific
checks.

For pull requests and pushes to `main`, the evaluation workflow runs only when
evaluation-relevant files change. The automatic job validates tagged smoke cases
without external API calls and uploads `dataset-validation.json`.

LLM-backed DeepEval and Ragas smoke checks run only from `workflow_dispatch`.
They use the existing `OPENAI_API_KEY` secret when available. If the secret is
not configured, the workflow records a JSON skip report instead of failing
before any evaluator runs.
