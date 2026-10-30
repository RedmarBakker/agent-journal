import argparse
import importlib
import json
from pathlib import Path
import sys
from uuid import uuid4

from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner
from tests.lab.drift_report import DriftReport


VERBS = ("organizations", "simulate", "regression", "compare", "plan-real", "approve", "run-real", "calibrate", "report")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="python3 -m tests.lab", description="run bounded local journal lab batches")
    verbs = command.add_subparsers(dest="verb", required=True)
    for name in VERBS:
        subcommand = verbs.add_parser(name)
        if name in {"simulate", "regression"}:
            recipe_help = "pinned batch recipe; omit batch_id so each regression invocation gets a fresh batch" if name == "regression" else "pinned batch recipe"
            subcommand.add_argument("--recipe", type=Path, required=True, help=recipe_help)
            subcommand.add_argument("--runner", required=True, help="simulation adapter as module:function")
            subcommand.add_argument("--lab-home", type=Path)
            subcommand.add_argument("--workers", type=int)
            if name == "regression":
                subcommand.add_argument("--baseline-batch", required=True, help="pinned simulated batch to compare against")
                subcommand.description = "run one simulated regression batch for an external schedule"
    return command


def main(arguments: list[str]) -> int:
    command = parser()
    options = command.parse_args(arguments)
    if options.verb not in {"simulate", "regression"}:
        print(f"{options.verb} is not available; no real run or other action was started", file=sys.stderr)
        return 2
    try:
        recipe = json.loads(options.recipe.read_text())
        if options.verb == "regression":
            if "batch_id" in recipe:
                raise ValueError("a regression recipe omits batch_id so each scheduled invocation gets a fresh batch")
            recipe["batch_id"] = uuid4().hex
        else:
            recipe.setdefault("batch_id", uuid4().hex)
        batch = Batch.from_mapping(recipe)
        run_one = runner(options.runner)
        batch_runner = BatchRunner(run_one, options.lab_home, workers=options.workers)
        if options.verb == "regression":
            drift = DriftReport(batch_runner.private_home(), options.baseline_batch, batch)
            drift.validate()
            batch_runner.run(batch)
            path = drift.write()
        else:
            path = batch_runner.run(batch)
    except (ImportError, OSError, ValueError, TypeError, KeyError, AttributeError) as failure:
        print(str(failure), file=sys.stderr)
        return 2
    print(path)
    return 0


def runner(specification: str):
    module_name, separator, function_name = specification.partition(":")
    if not separator or not module_name or not function_name:
        raise ValueError("runner must be named module:function")
    selected = getattr(importlib.import_module(module_name), function_name)
    if not callable(selected):
        raise ValueError("the selected simulation adapter is not callable")
    return selected


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
