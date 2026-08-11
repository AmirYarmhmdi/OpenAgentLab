"""Developer entry point for OpenAgentLab evaluation."""

import argparse
import json
from pathlib import Path

from openagentlab.evaluation.dataset import load_evaluation_dataset
from openagentlab.evaluation.ragas_evaluator import RAGAS_METRICS, RagasEvaluator
from openagentlab.evaluation.runner import EvaluationRunner
from openagentlab.evaluation.thresholds import thresholds_from_settings

DEFAULT_DATASET = "evaluation/datasets/smoke.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m openagentlab.evaluation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--dataset", default=DEFAULT_DATASET)
    validate_parser.add_argument("--tags", nargs="*", default=())

    ragas_parser = subparsers.add_parser("ragas")
    ragas_parser.add_argument("--dataset", default=DEFAULT_DATASET)
    ragas_parser.add_argument("--tags", nargs="*", default=())
    ragas_parser.add_argument("--metrics", nargs="*", default=list(RAGAS_METRICS))

    args = parser.parse_args()

    if args.command == "validate":
        cases = load_evaluation_dataset(Path(args.dataset), tags=args.tags)
        print(json.dumps({"dataset": args.dataset, "case_count": len(cases)}))
        return

    thresholds = thresholds_from_settings()
    runner = EvaluationRunner(evaluator=RagasEvaluator(), thresholds=thresholds)
    result = runner.run_dataset(args.dataset, metrics=args.metrics, tags=args.tags)
    print(
        json.dumps(
            {
                "evaluator": result.evaluator,
                "case_count": result.case_count,
                "passed": result.passed,
                "passed_count": result.passed_count,
                "failed_count": result.failed_count,
                "average_scores": result.average_scores,
            },
            sort_keys=True,
        )
    )
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
