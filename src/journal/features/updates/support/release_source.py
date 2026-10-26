import json
import shutil
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from journal.features.updates.support.release_check import ReleaseCheck
from journal.features.updates.support.release_check_memory import ReleaseCheckMemory
from journal.features.updates.support.release_refusal import ReleaseRefusal
from journal.support.time_source import TimeSource

REPOSITORY = "https://github.com/jessegall/agent-journal"
TAGS_PATH = "repos/jessegall/agent-journal/git/matching-refs/tags/{prefix}"
TAGS = "https://api.github.com/" + TAGS_PATH
READ_SECONDS = 10
LIST_SECONDS = 60
# how long GitHub is left alone when it refuses without saying when its limit resets
REFUSAL_SECONDS = 3600


class ReleaseSource:
    """The journal's tags on GitHub: asked through the GitHub CLI when it is installed and logged in, whose own limit is far higher, else over HTTP without a login; every look and every refusal for asking too often is stored for the whole machine, and a refusal is waited out until GitHub's limit resets."""

    def __init__(self, memory: ReleaseCheckMemory, time_source: TimeSource) -> None:
        self.memory, self.time_source = memory, time_source

    def tags(self, prefix: str) -> list[str]:
        try:
            tags = self.cli_tags(prefix) if self.has_cli_login() else self.http_tags(prefix)
        except ReleaseRefusal as refused:
            self.memory.store(ReleaseCheck(self.time_source.seconds(), refused.reset_at, self.memory.last().tags))
            raise
        self.memory.store(ReleaseCheck(self.time_source.seconds(), 0.0, tuple(tags)))
        return tags

    def next_check_time(self, interval_seconds: float) -> float:
        return self.memory.last().next_check_time(interval_seconds)

    def stored_tags(self, prefix: str) -> list[str]:
        return self.memory.last().prefixed_tags(prefix)

    @staticmethod
    def has_cli_login() -> bool:
        return shutil.which("gh") is not None and subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=READ_SECONDS).returncode == 0

    def cli_tags(self, prefix: str) -> list[str]:
        listed = subprocess.run(["gh", "api", TAGS_PATH.format(prefix=prefix)], capture_output=True, text=True, timeout=LIST_SECONDS)
        if listed.returncode != 0:
            return self.http_tags(prefix)
        return [row["ref"].removeprefix("refs/tags/") for row in json.loads(listed.stdout)]

    def http_tags(self, prefix: str) -> list[str]:
        request = Request(TAGS.format(prefix=prefix), headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-journal"})
        try:
            with urlopen(request, timeout=READ_SECONDS) as answer:
                return [row["ref"].removeprefix("refs/tags/") for row in json.load(answer)]
        except HTTPError as error:
            if error.code in (403, 429) and error.headers.get("X-RateLimit-Remaining", "") in ("0", ""):
                raise ReleaseRefusal(float(error.headers.get("X-RateLimit-Reset") or self.time_source.seconds() + REFUSAL_SECONDS)) from error
            raise

    def head_commit(self, address: str, branch: str) -> str:
        listed = subprocess.run(["git", "ls-remote", "--heads", address, branch], capture_output=True, text=True, timeout=LIST_SECONDS)
        if listed.returncode != 0 or not listed.stdout.strip():
            raise OSError(f"could not read the branch {branch} of {address}: {listed.stderr.strip()[-200:] or 'no such branch'}")
        return listed.stdout.split()[0]

    def release_tags(self, address: str) -> list[str]:
        listed = subprocess.run(["git", "ls-remote", "--tags", "--refs", address], capture_output=True, text=True, timeout=LIST_SECONDS)
        if listed.returncode != 0:
            raise OSError(f"could not list the releases of {address}: {listed.stderr.strip()[-200:]}")
        return [line.split("refs/tags/", 1)[1] for line in listed.stdout.splitlines() if "refs/tags/" in line]
