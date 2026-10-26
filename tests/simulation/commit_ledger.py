from journal.features.git.support.head_commit import HeadCommit

BRANCH = "main"


class CommitLedger:
    """The commits a simulated run made, kept in place of git: the lines written since the last commit per path, and each commit's sha, subject, time and lines per path, answered as git would answer the journal's reads of the head."""

    def __init__(self) -> None:
        self.pending: dict[str, int] = {}
        self.commits: list[tuple[str, str, int, tuple[tuple[str, int], ...]]] = []

    def wrote(self, path: str, lines: int) -> None:
        self.pending[path] = self.pending.get(path, 0) + lines

    def committed(self, subject: str, moment: int) -> str:
        sha = f"{len(self.commits) + 1:040x}"
        self.commits.append((sha, subject, moment, tuple(self.pending.items())))
        self.pending.clear()
        return sha

    def git(self, *arguments: str) -> str:
        if not self.commits:
            return ""
        sha, subject, _, paths = self.commits[-1]
        answers = {"log": f"{sha}\0{subject}", "show": "\n".join(f"{lines}\t0\t{path}" for path, lines in paths), "rev-parse": BRANCH}
        return answers.get(arguments[0], "")

    def head(self) -> HeadCommit | None:
        if not self.commits:
            return None
        sha, subject, moment, _ = self.commits[-1]
        return HeadCommit(sha, subject, BRANCH, subject, moment)

    def lines(self) -> int:
        return sum(lines for *_, paths in self.commits for _, lines in paths)
