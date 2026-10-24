import json
import subprocess
from pathlib import Path

from journal.chat.moment_cards import MomentCards
from journal.config import Config
from journal.features.git.support.launch_worktrees import LAUNCH_FOLDER, MOVED_ASIDE, LaunchWorktrees
from journal.features.seed import Seed
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.card_kind import CardKind

GIT_SECONDS = 10


class WorktreeTidying(Seed):
    """At boot, what launches of older versions left in their worktrees is tidied: the journal's hooks written into a worktree's own settings are taken out, a tracked settings file put back as committed, the skip-worktree marks on its files cleared, and the folders once moved aside named to the person once, never deleted."""

    def __init__(self, config: Config, environments: Environments, providers: Providers, cards: MomentCards) -> None:
        self.config, self.environments, self.providers, self.cards = config, environments, providers, cards

    def run(self) -> None:
        for name in LaunchWorktrees(self.config, self.environments).names():
            folder = self.config.root / LAUNCH_FOLDER / name
            if not (folder / ".git").is_file():
                continue
            for provider in self.providers.all():
                self.hooks_taken_out(provider, folder, Path(provider.home) / provider.settings_file)
            self.marks_cleared(folder)
        self.moved_aside_named()

    def hooks_taken_out(self, provider: Provider, folder: Path, relative: Path) -> None:
        path = folder / relative
        if path.is_symlink() or not provider.has_journal_hooks(path):
            return
        provider.unwired(path)
        committed = self.git(folder, "show", f"HEAD:{relative}")
        if committed.returncode == 0 and json.loads(committed.stdout or "{}") == json.loads(path.read_text()):
            self.git(folder, "checkout", "--", str(relative))

    def marks_cleared(self, folder: Path) -> None:
        marked = [line[2:] for line in self.git(folder, "ls-files", "-v").stdout.splitlines() if line.startswith("S ")]
        if marked:
            self.git(folder, "update-index", "--no-skip-worktree", "--", *marked)

    def moved_aside_named(self) -> None:
        place = self.config.root / LAUNCH_FOLDER
        moved = sorted(path.name for path in place.iterdir() if MOVED_ASIDE in path.name) if place.is_dir() else []
        key = f"moved-aside:{','.join(moved)}"
        if not moved or self.cards.is_shown(key, Actor.system()):
            return
        line = f"Worktree folders an older version moved aside are kept, never deleted, in {place}: {', '.join(moved)}"
        self.cards.show(self.environments.lookup("main").row_id, None, line, "branch", tone="warn", actor=Actor.system(), key=key, shows=CardKind.WORKTREES)

    @staticmethod
    def git(folder: Path, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(folder), *argv], capture_output=True, text=True, timeout=GIT_SECONDS)
