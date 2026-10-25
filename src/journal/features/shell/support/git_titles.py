import shlex
from pathlib import Path

from journal.features.git.support.git_facts import GitFacts


class GitTitles:
    """The plain title of the live card of a git commit or a git push, said from the repository the command runs in: the branch pushed and the remote it goes to, or the files a commit takes in."""

    def title(self, command: str, folder: str) -> str:
        tokens = self.tokens(command)
        if tokens[:2] == ["git", "push"]:
            return self.push(tokens[2:], Path(folder))
        if tokens[:2] == ["git", "commit"]:
            return self.commit(tokens[2:], Path(folder))
        return ""

    @staticmethod
    def tokens(command: str) -> list[str]:
        part = command.split("&&")[-1].split(";")[-1].strip()
        try:
            return shlex.split(part)
        except ValueError:
            return []

    @staticmethod
    def pushed_branch(arguments: list[str], folder: Path) -> str:
        if len(arguments) > 1:
            return arguments[1].split(":")[-1]
        return GitFacts.branch(folder) if folder.is_dir() else ""

    @staticmethod
    def push(options: list[str], folder: Path) -> str:
        arguments = [token for token in options if not token.startswith("-")]
        remote = arguments[0] if arguments else "origin"
        branch = GitTitles.pushed_branch(arguments, folder)
        return f"Pushing {branch} to {remote}" if branch else f"Pushing to {remote}"

    @staticmethod
    def takes_all(options: list[str]) -> bool:
        short = [token for token in options if token.startswith("-") and not token.startswith("--")]
        return "--all" in options or any("a" in token[1:] for token in short)

    @staticmethod
    def staged(options: list[str], folder: Path) -> set[str]:
        if not folder.is_dir():
            return set()
        changed = set(GitFacts.run(folder, "diff", "--cached", "--name-only").splitlines())
        return changed | set(GitFacts.run(folder, "diff", "--name-only").splitlines()) if GitTitles.takes_all(options) else changed

    @staticmethod
    def commit(options: list[str], folder: Path) -> str:
        count = len(GitTitles.staged(options, folder))
        return f"Committing {count} {GitTitles.noun(count)}" if count else "Committing"

    @staticmethod
    def noun(count: int) -> str:
        return "file" if count == 1 else "files"
