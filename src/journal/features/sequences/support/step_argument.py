from argparse import Action, ArgumentParser, Namespace

from journal.models.support.sequence_step import SequenceStep

# where the steps written with --step gather on the parsed arguments
STEPS_DESTINATION = "step_records"


class StepArgument(Action):
    """--step 'title | instructions' on a sequence command: each adds a step, file edits allowed, which the guard arguments after it change."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values, option_string=None) -> None:
        title, separator, instructions = str(values).partition("|")
        step = SequenceStep(title=title.strip(), instructions=instructions.strip()) if separator else SequenceStep(instructions=title.strip())
        setattr(namespace, STEPS_DESTINATION, (*(getattr(namespace, STEPS_DESTINATION, None) or ()), step))
