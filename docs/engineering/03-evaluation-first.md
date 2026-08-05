# Evaluation First

> AI systems should be evaluated continuously rather than only during manual testing.

---

## Philosophy

Evaluation is an engineering activity.

Quality should be measured automatically.

Every significant change should be validated before deployment.

---

## Evaluation Layers

### Unit Tests

Validate deterministic code.

---

### Integration Tests

Validate workflows and tool interactions.

---

### RAG Evaluation

Ragas

Measures:

- Context Precision
- Context Recall
- Faithfulness
- Answer Relevance

---

### LLM Evaluation

DeepEval

Measures:

- Correctness
- Hallucination
- Tool Usage
- Faithfulness

---

## CI Integration

Evaluation should become part of GitHub Actions.

Code should not be merged if quality gates fail.

---

## Principles

- Evaluation is automated.
- Benchmarks are reproducible.
- Metrics are versioned.
- Results are comparable across releases.

---

## Future

- Promptfoo
- Phoenix
- Human evaluation datasets