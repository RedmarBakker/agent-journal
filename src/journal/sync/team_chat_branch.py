import time

from journal.events.announcer import Announcer
from journal.events.moments.team_chat_files_diverged import TeamChatFilesDiverged
from journal.config import Config
from journal.repositories.environments import Environments
from journal.support.worktree import Worktree
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount

TEAM_CHAT = "team"
REMOTE = "origin"
SHARED_BRANCH = "journal/team-chat"
COMMIT_DELAY_SECONDS = 15
# git holds the index for a moment while another git command of the same worktree reads or refreshes it: staging waits for it this many times
STAGE_ATTEMPTS = 25
STAGE_WAIT_SECONDS = 0.2


class TeamChatBranch:
    """The Team chat's files, the same on every machine: the holder commits its worktree of the Team chat once its files have not changed for 15 seconds and pushes it to the branch journal/team-chat on origin, which every member fetches from; every other machine moves its own worktree of the Team chat to that branch's last commit when the worktree has no changes of its own, and says in the Team chat when it has. Files git ignores, the journal's folder and secrets among them, are never committed; repositories inside the project are not part of an environment's worktree, so they are not shared."""

    def __init__(self, config: Config, account: TeamAccount, environments: Environments, announcer: Announcer, status: SyncStatus) -> None:
        self.account, self.environments, self.announcer, self.status = account, environments, announcer, status
        self.worktree = Worktree(config.root, TEAM_CHAT)
        self.files_hash, self.files_hash_at, self.remote_head, self.warning_tip = "", 0.0, "", ""

    def push(self, time: float) -> None:
        if not self.worktree.path.is_dir():
            return
        files_hash = self.staged_hash()
        if not files_hash:
            return
        if files_hash != self.files_hash:
            self.files_hash, self.files_hash_at = files_hash, time
        elif time - self.files_hash_at >= COMMIT_DELAY_SECONDS:
            self.commit(files_hash)
        head = self.worktree.local_branch()
        if head != self.remote_head:
            self.push_head(head)

    def push_all(self) -> None:
        if not self.worktree.path.is_dir():
            return
        files_hash = self.staged_hash()
        if files_hash:
            self.commit(files_hash)
            self.push_head(self.worktree.local_branch())

    def staged_hash(self) -> str:
        for _ in range(STAGE_ATTEMPTS):
            added = self.worktree.run_git("add", "-A")
            if added.returncode == 0:
                return self.worktree.run_git("write-tree").stdout.strip()
            time.sleep(STAGE_WAIT_SECONDS)
        self.status.failed(f"the Team chat's files were not staged: {added.stderr.strip()}")
        return ""

    def commit(self, files_hash: str) -> None:
        if files_hash != self.worktree.run_git("rev-parse", "HEAD^{tree}").stdout.strip():
            self.worktree.run_git("commit", "-q", "-m", "The Team chat's files")

    def push_head(self, head: str) -> None:
        pushed = self.worktree.run_git("push", "-q", REMOTE, f"{head}:refs/heads/{SHARED_BRANCH}")
        if pushed.returncode != 0:
            self.status.failed(f"the Team chat's files were not pushed to {REMOTE}: {pushed.stderr.strip()}")
            return
        self.remote_head = head

    # this machine claims the Team chat: its worktree is made now, never on joining, and brought to the holder's last push
    def claim(self) -> None:
        self.worktree.created()
        self.pull()

    def pull(self) -> None:
        if not self.worktree.path.is_dir():
            return
        listed = self.worktree.git("ls-remote", "--heads", REMOTE, SHARED_BRANCH)
        if listed.returncode != 0:
            self.status.failed(f"the Team chat's files were not fetched from {REMOTE}: {listed.stderr.strip()}")
            return
        tip = listed.stdout.split("\t")[0].strip()
        if not tip or tip == self.worktree.local_branch():
            return
        self.worktree.run_git("fetch", "-q", REMOTE, SHARED_BRANCH)
        if self.worktree.run_git("status", "--porcelain").stdout.strip():
            self.warn(tip)
            return
        self.worktree.run_git("reset", "-q", "--hard", tip)

    def warn(self, tip: str) -> None:
        if tip == self.warning_tip:
            return
        self.warning_tip = tip
        device = self.account.device_name()
        self.announcer.announce(TeamChatFilesDiverged(environment_id=self.environments.existing(TEAM_CHAT).id, device=device, local=self.worktree.local_branch(), tip=tip))
