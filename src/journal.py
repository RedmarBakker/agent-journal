import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from journal.app import App  # noqa: E402
from journal.config import Config  # noqa: E402
from journal.providers.providers import Providers  # noqa: E402
from journal.sync.carrier_process import CarrierProcess  # noqa: E402

AGENTS = ("claude", "codex")


def main(argv: list[str]) -> int:
    # the process this one lives for: the journal server that started a carrier names itself, as a framework build's python starts
    # the real interpreter as a child of its own, which outlives a killed parent; else the parent
    parent = int(os.environ.get("JOURNAL_PARENT_PID") or os.getppid())
    root = Path(os.environ.get("JOURNAL_ROOT") or Path.cwd())
    if argv[:1] and argv[0] in AGENTS:
        from journal.launcher.launch import Launch
        return Launch.parse(argv, root).run()
    if argv[:2] == ["remote", "github"]:
        from journal.launcher.remote_github import RemoteGithub
        return RemoteGithub.parsed(argv[2:], root).run()
    if argv[:1] == ["remote"]:
        from journal.launcher.remote_install import RemoteInstall
        return RemoteInstall.parsed(argv[1:]).run()
    app = App(Config.rooted(root))
    if argv[:1] == ["serve"]:
        app.runtime().run()
        return 0
    if argv[:1] == ["sync"]:
        app.container.get(CarrierProcess).run(parent)
        return 0
    outcome = app.console().run(argv, app.container.get(Providers).caller(os.environ))
    sys.stdout.write(outcome.text)
    sys.stderr.write(outcome.error)
    return outcome.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
