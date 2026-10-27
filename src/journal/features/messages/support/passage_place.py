from journal.models.support.ref import Ref
from journal.repositories.docs import Docs
from journal.repositories.reports import Reports


class PassagePlace:
    """Where a comment's passage sits in its document or report as it stands now, by its section and line, found by the passage's own text since lines move with every edit, or that it is there no more."""

    def __init__(self, docs: Docs, reports: Reports) -> None:
        self.docs, self.reports = docs, reports

    def line(self, ref: Ref, quote: str) -> str:
        texts: dict[str, tuple[str, Docs | Reports]] = {"docs": ("doc", self.docs), "reports": ("report", self.reports)}
        if ref.type not in texts:
            return ""
        noun, repository = texts[ref.type]
        lines = repository.find(ref.id).body.split("\n")
        first = quote.split("\n")[0].strip()
        start = next((i for i, line in enumerate(lines) if line.strip() == first), -1)
        if start < 0:
            return f"  the passage is not in {noun} {ref.id} as it stands now"
        end = start + quote.count("\n")
        section = sum(1 for line in lines[: start + 1] if line.startswith("## "))
        heading = next((line[3:] for line in reversed(lines[: start + 1]) if line.startswith("## ")), "")
        line_numbers = f"lines {start + 1}-{end + 1}" if end > start else f"line {start + 1}"
        location = f"section {section}, {heading}, {line_numbers}" if section else line_numbers
        return f"  the passage sits in {noun} {ref.id} at {location}: `journal {noun} show {ref.id} --section {section or 1}` or `--grep`"
