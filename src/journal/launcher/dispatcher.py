from pathlib import Path

TEXT = """#!/bin/sh
# agent-journal: the journal command. It finds the project by its .journal folder, walking up from JOURNAL_ROOT when
# set, else from here, and runs the journal that project holds, whichever version: nothing of the journal itself lives
# outside a project.
dir="${JOURNAL_ROOT:-$(pwd)}"
while [ "$dir" != "/" ]; do
    if [ -f "$dir/.journal/src/journal.sh" ]; then
        JOURNAL_ROOT="$dir" exec sh "$dir/.journal/src/journal.sh" "$@"
    fi
    if [ -x "$dir/.journal/journal" ]; then
        exec "$dir/.journal/journal" "$@"
    fi
    dir="$(dirname "$dir")"
done
echo "no .journal/ here or above: install agent-journal in this project first" >&2
exit 1
"""


class Dispatcher:
    """The one command outside a project, at ~/.local/bin/journal: it only finds the project's own journal, from JOURNAL_ROOT when set so an agent working outside the project reaches it, and hands over to it, its journal.sh or the launcher an older install keeps at .journal/journal."""

    def __init__(self, home: Path) -> None:
        self.path = home / ".local" / "bin" / "journal"

    def write(self) -> Path | None:
        if not self.path.parent.is_dir():
            return None
        if not self.path.is_file() or self.path.read_text() != TEXT:
            self.path.write_text(TEXT)
            self.path.chmod(0o755)
        return self.path
