import argparse
import importlib
import json
from pathlib import Path
import sys
from uuid import uuid4

from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner


VERBS = ("organizations", "simulate", "compare", "plan-real", "approve", "run-real", "calibrate", "report")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="python3 -m tests.lab", description="run bounded local journal lab batches")
    verbs = command.add_subparsers(dest="verb", required=True)
    for name in VERBS:
        subcommand = verbs.add_parser(name)
        if name == "simulate":
            subcommand.add_argument("--recipe", type=Path, required=True)
            subcommand.add_argument("--runner", required=True, help="simulation adapter as module:function")
            subcommand.add_argument("--lab-home", type=Path)
            subcommand.add_argument("--workers", type=int)
    return command


def main(arguments: list[str]) -> int:
    command = parser()
    options = command.parse_args(arguments)
    if options.verb != "simulate":
        print(f"{options.verb} is not available; no real run or other action was started", file=sys.stderr)
        return 2
    try:
        recipe = json.loads(options.recipe.read_text())
        recipe.setdefault("batch_id", uuid4().hex)
        batch = Batch.from_mapping(recipe)
        run_one = runner(options.runner)
        path = BatchRunner(run_one, options.lab_home, workers=options.workers).run(batch)
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
