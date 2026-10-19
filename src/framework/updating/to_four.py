import subprocess
import tempfile
from pathlib import Path

from install import keep_copy
from resources.versions import line_of

LINE = 4
INSTALLER = "https://raw.githubusercontent.com/jessegall/agent-journal/main/install.sh"
KEPT_IN = ".journal/version-3"
ASKED = """Upgrading to version 4 does this, in order:
  1. backs up the journal into .journal/attic
  2. stops the journal completely: its viewer, its engine and every service it runs
  3. installs version 4 by running its install script from the project root: curl -fsSL {installer} | sh
  4. restarts the journal on version 4
The install script keeps this journal whole in {kept}. To-dos become tasks, plans and everything else come across, and nothing is lost. The board is set aside for now and comes back later, revised.
To go ahead: journal upgrade --to 4 --yes"""


def names_four(version: str | None) -> bool:
    return bool(version) and line_of(version) == LINE


def asked() -> str:
    return ASKED.format(installer=INSTALLER, kept=KEPT_IN)


def crossed(ctx) -> str:
    """The way across to version 4: backs the journal up, stops it completely, then runs version 4's installer on its own, since the journal it stops is the one running this."""
    from commands.queries import halt
    root = ctx["record"].root
    backed_up = keep_copy(root)
    stopped = halt(ctx)
    log = Path(tempfile.gettempdir()) / "agent-journal-upgrade-to-4.log"
    with log.open("a") as printing:
        subprocess.Popen(["sh", "-c", f"curl -fsSL {INSTALLER} | sh"], cwd=str(root.parent), stdin=subprocess.DEVNULL,
                         stdout=printing, stderr=subprocess.STDOUT, start_new_session=True)
    return "\n".join(filter(None, [backed_up, stopped, f"version 4's installer is running on its own; it writes to {log}"]))
