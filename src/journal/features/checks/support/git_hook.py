from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GitHook:
    """One of the repository's git hooks: its name, whether git runs it (present, executable and in the folder git uses), the folder, what its comments say it is for and the commands it runs."""

    name: str
    is_active: bool
    folder: str
    purpose: str
    commands: tuple[str, ...]

    def as_data(self) -> dict:
        return asdict(self)
