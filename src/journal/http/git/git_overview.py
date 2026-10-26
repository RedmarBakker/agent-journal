import shutil
import subprocess

from journal.config import Config
from journal.http.git.git_branch import GitBranch
from journal.http.git.git_commit import GitCommit
from journal.http.git.git_finished import GitFinished
from journal.http.git.git_page import GitPage
from journal.http.git.git_pull import GitPull
from journal.http.git.git_pulls import GitPulls

BASES = ("development", "main", "master")
TIMEOUT_SECONDS = 15
REQUEST_ROWS = 30
FAILED = ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE")
PENDING_STATES = ("PENDING", "QUEUED", "IN_PROGRESS", "WAITING", "EXPECTED", "")
# the fields of a pull request, one line each separated by tabs, the title last since it may hold any text
REQUEST_FIELDS = '[.number, .isDraft, .reviewDecision, ([.statusCheckRollup[] | (.conclusion // .state // .status // "")] | join(",")), .headRefName, .author.login, .url, .title] | @tsv'


class GitOverview:
    """The project's repository as the Git page reads it, and nothing is written: its branches with the commits each has beyond the base branch and those it lacks, the recent commits of the current branch, and the open pull requests when gh is there."""

    def __init__(self, config: Config) -> None:
        self.root = config.root.resolve()

    def run(self, *command: str) -> GitFinished:
        finished = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        return GitFinished(finished.returncode == 0, finished.stdout)

    def current(self) -> str:
        return self.run("git", "rev-parse", "--abbrev-ref", "HEAD").text.strip()

    def base(self) -> str:
        return next((name for name in BASES if self.run("git", "rev-parse", "--verify", "--quiet", name).succeeded), "")

    def branches(self, offset: int, last: int) -> GitPage:
        listed = self.run("git", "for-each-ref", "refs/heads", "--sort=-committerdate", "--format=%(refname:short)%09%(committerdate:unix)%09%(authorname)%09%(subject)").text.splitlines()
        current, base = self.current(), self.base()
        return GitPage(rows=[self.branch(line, current, base) for line in listed[offset:offset + last]], is_last_page=offset + last >= len(listed))

    def branch(self, line: str, current: str, base: str) -> GitBranch:
        name, time, author, subject = line.split("\t", 3)
        missing, extra = self.distance(base, name) if base and name != base else (0, 0)
        return GitBranch(name=name, current=name == current, extra_commits=extra, missing_commits=missing, subject=subject, author=author, time=float(time))

    def distance(self, base: str, name: str) -> tuple[int, int]:
        missing, extra = self.run("git", "rev-list", "--left-right", "--count", f"{base}...{name}").text.split()
        return int(missing), int(extra)

    def commits(self, offset: int, last: int) -> GitPage:
        listed = self.run("git", "log", f"--skip={offset}", f"-n{last + 1}", "--format=%H%x09%an%x09%at%x09%s").text.splitlines()
        return GitPage(rows=[self.commit(line) for line in listed[:last]], is_last_page=len(listed) <= last)

    @staticmethod
    def commit(line: str) -> GitCommit:
        sha, author, time, subject = line.split("\t", 3)
        return GitCommit(sha=sha, subject=subject, author=author, time=float(time))

    def pull_requests(self) -> GitPulls:
        if shutil.which("gh") is None:
            return GitPulls(available=False, rows=[])
        listed = self.run("gh", "pr", "list", "--state", "open", "--limit", str(REQUEST_ROWS), "--json", "number,title,headRefName,author,isDraft,reviewDecision,statusCheckRollup,url", "--jq", f".[] | {REQUEST_FIELDS}")
        return GitPulls(available=listed.succeeded, rows=[self.pull_request(line) for line in listed.text.splitlines()])

    @staticmethod
    def pull_request(line: str) -> GitPull:
        number, draft, review, checks, branch, author, url, title = line.split("\t", 7)
        states = [state.upper() for state in checks.split(",")] if checks else []
        failed = sum(1 for state in states if state in FAILED)
        pending = sum(1 for state in states if state in PENDING_STATES)
        return GitPull(number=int(number), title=title, branch=branch, author=author, draft=draft == "true", review=review, checks_passed=len(states) - failed - pending, checks_failed=failed, checks_pending=pending, url=url)
