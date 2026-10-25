import shlex
from pathlib import Path

from journal.features.git.support.git_facts import GitFacts

FILES_NOTE = "file"


class GitTitles:
    """The plain title of the live card of a git commit or a git push, said from the repository the command runs in: the branch pushed and the remote it goes to, or the files a commit takes in."""

    def title(self, command: str, folder: str) -> str:
        words = self.words(command)
        if words[:2] == ["git", "push"]:
            return self.push(words[2:], Path(folder))
        if words[:2] == ["git", "commit"]:
            return self.commit(words[2:], Path(folder))
        return ""

    @staticmethod
    def words(command: str) -> list[str]:
        part = command.split("&&")[-1].split(";")[-1].strip()
        try:
            return shlex.split(part)
        except ValueError:
            return []

    @staticmethod
    def push(rest: list[str], folder: Path) -> str:
        names = [word for word in rest if not word.startswith("-")]
        remote = names[0] if names else "origin"
        branch = names[1].split(":")[-1] if len(names) > 1 else (GitFacts.branch(folder) if folder.is_dir() else "")
        return f"Pushing {branch} to {remote}" if branch else f"Pushing to {remote}"

    @staticmethod
    def commit(rest: list[str], folder: Path) -> str:
        if not folder.is_dir():
            return "Committing"
        taking_all = any(word == "-a" or (word.startswith("-") and not word.startswith("--") and "a" in word[1:]) for word in rest) or "--all" in rest
        staged = set(GitFacts.run(folder, "diff", "--cached", "--name-only").splitlines())
        if taking_all:
            staged |= set(GitFacts.run(folder, "diff", "--name-only").splitlines())
        return f"Committing {len(staged)} {FILES_NOTE}{'' if len(staged) == 1 else 's'}" if staged else "Committing"
