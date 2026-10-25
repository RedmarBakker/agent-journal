import json
from pathlib import Path

from journal.support.inner_repositories import InnerRepositories
from journal.config import Config
from journal.features.git.support.launch_worktrees import LAUNCH_FOLDER, LaunchWorktrees
from journal.features.seed import Seed
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.repositories.environments import Environments


class WorktreeTidying(Seed):
    """At boot, what launches of older versions left in their worktrees is tidied: the journal's hooks written into a worktree's own settings are taken out, a tracked settings file put back as committed, the skip-worktree marks on its files cleared."""

    def __init__(self, config: Config, environments: Environments, providers: Providers) -> None:
        self.config, self.environments, self.providers = config, environments, providers

    def run(self) -> None:
        for name in LaunchWorktrees(self.config, self.environments).names():
            folder = self.config.root / LAUNCH_FOLDER / name
            if not (folder / ".git").is_file():
                continue
            for provider in self.providers.all():
                self.clear_hooks(provider, folder, Path(provider.home) / provider.settings_file)
            self.clear_worktree_flags(folder)

    def clear_hooks(self, provider: Provider, folder: Path, relative: Path) -> None:
        path = folder / relative
        if path.is_symlink() or not provider.has_journal_hooks(path):
            return
        provider.unwired(path)
        committed = InnerRepositories.git(folder, "show", f"HEAD:{relative}")
        if committed.returncode == 0 and json.loads(committed.stdout or "{}") == json.loads(path.read_text()):
            InnerRepositories.git(folder, "checkout", "--", str(relative))

    def clear_worktree_flags(self, folder: Path) -> None:
        flagged_paths = [line[2:] for line in InnerRepositories.git(folder, "ls-files", "-v").stdout.splitlines() if line.startswith("S ")]
        if flagged_paths:
            InnerRepositories.git(folder, "update-index", "--no-skip-worktree", "--", *flagged_paths)
