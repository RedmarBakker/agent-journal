import shutil
from pathlib import Path


def copied(template: Path, root: Path) -> Path:
    """A copy of the booted template journal at root, with no project id, so it makes one of its own."""
    shutil.copytree(template, root, dirs_exist_ok=True)
    (root / ".journal" / "project-id").unlink(missing_ok=True)
    return root
