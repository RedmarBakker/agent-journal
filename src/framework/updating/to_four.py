import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from install import keep_copy
from resources.versions import line_of

LINE = 4
INSTALLER = "https://raw.githubusercontent.com/jessegall/agent-journal/main/install.sh"
KEPT_IN = ".journal/version-3"
# where version 4's installer looks for the Python it runs on, in its order
PYTHONS = ("python3.14", "python3", "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14")
WANTED_PYTHON = (3, 14)
ASKED = """Upgrading to version 4 does this, in order:
  1. backs up the journal into .journal/attic
  2. stops the journal completely: its viewer, its engine and every service it runs
  3. installs version 4 by running its install script from the project root: curl -fsSL {installer} | sh
  4. restarts the journal on version 4
Stopping the journal ends the agent session it runs in, so run it from a plain terminal. Version 4 needs Python 3.14 and git; when either
is missing nothing is stopped and you are told what to install. The installer writes what it does to {log}.
The install script keeps this journal whole in {kept}. To-dos become tasks, plans and everything else come across, and nothing is lost. The board is set aside for now and comes back later, revised.
To go ahead: journal upgrade --to 4 --yes"""


def names_four(version: str | None) -> bool:
    return bool(version) and line_of(version) == LINE


def installer_log() -> Path:
    return Path(tempfile.gettempdir()) / "agent-journal-upgrade-to-4.log"


def asked() -> str:
    return ASKED.format(installer=INSTALLER, kept=KEPT_IN, log=installer_log())


def has_wanted_python(program: str) -> bool:
    found = shutil.which(program) or (program if Path(program).is_file() else None)
    if not found:
        return False
    checked = subprocess.run([found, "-c", f"import sys; sys.exit(sys.version_info[:2] != {WANTED_PYTHON})"], capture_output=True, timeout=10)
    return checked.returncode == 0


def missing_needs() -> list[str]:
    python = "" if any(has_wanted_python(program) for program in PYTHONS) else "Python 3.14"
    git = "" if shutil.which("git") else "git"
    return [need for need in (python, git) if need]


def refusal(needs: list[str]) -> str:
    return (f"version 4 needs {' and '.join(needs)}, and this machine has none: nothing was stopped. Install it, or run version 4's installer "
            f"from a plain terminal in the project, which offers to install it: curl -fsSL {INSTALLER} | sh")


def crossed(ctx) -> str:
    """The way across to version 4: backs the journal up, stops it completely, then runs version 4's installer on its own, since the journal it stops is the one running this."""
    from commands.queries import halt
    needs = missing_needs()
    if needs:
        return refusal(needs)
    root = ctx["record"].root
    backed_up = keep_copy(root)
    stopped = halt(ctx)
    log = installer_log()
    with log.open("a") as printing:
        subprocess.Popen(["sh", "-c", f"curl -fsSL {INSTALLER} | sh"], cwd=str(root.parent), stdin=subprocess.DEVNULL,
                         stdout=printing, stderr=subprocess.STDOUT, start_new_session=True, env={**os.environ, "AGENT_JOURNAL_YES": "1"})
    return "\n".join(filter(None, [backed_up, stopped, f"version 4's installer is running on its own; it writes to {log}"]))
