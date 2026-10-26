from argparse import Action, ArgumentParser, Namespace
from dataclasses import replace

from journal.features.sequences.support.step_argument import STEPS_DESTINATION


class StepGuardArgument(Action):
    """A guard written after a --step, --hold-edits or --allow-commands '<pattern>', set on the step before it."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values, option_string=None) -> None:
        steps = getattr(namespace, STEPS_DESTINATION, None) or ()
        if not steps:
            parser.error(f"{option_string} sets a guard of the step before it: write it after a --step")
        last = steps[-1]
        guarded = replace(last, file_edits_allowed=False) if option_string == "--hold-edits" else replace(last, allowed_commands=(*last.allowed_commands, str(values)))
        setattr(namespace, STEPS_DESTINATION, (*steps[:-1], guarded))
