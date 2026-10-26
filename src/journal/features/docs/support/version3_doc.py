import json
from pathlib import Path

from journal.models.doc import Doc
from journal.models.support.abstract_text import AbstractText

FENCE = "---"


class Version3Doc:
    """A document as version 3 stored it: a folder with doc.md, its row as JSON between two --- lines, then its text."""

    @staticmethod
    def read(folder: Path) -> Doc | None:
        file = folder / "doc.md"
        text = file.read_text(errors="replace") if file.is_file() else ""
        if not text.startswith(f"{FENCE}\n"):
            return None
        _, head, body = text.split(f"{FENCE}\n", 2)
        row = json.loads(head)
        if row.get("deleted"):
            return None
        title = str(row.get("title", folder.name))
        return Doc(title=title, abstract=AbstractText.fitted(str(row.get("abstract", "")), body.strip(), title), body=body.strip())
