from argparse import Action, ArgumentParser, Namespace

from journal.models.support.report_choice import ReportChoice


class ReportArgument(Action):
    """--report's words, queue or each alone or every with its number, so the words after them are kept as the job text."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: list[str], option_string: str | None = None) -> None:
        taken = ReportChoice.word_count(values[0])
        setattr(namespace, self.dest, values[:taken])
        namespace.job_text = " ".join(values[taken:])
