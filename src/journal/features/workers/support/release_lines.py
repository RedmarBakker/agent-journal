import re

# a shell line that cuts a release: a tag made with git tag and a name, or a release published with gh release create
RELEASE = re.compile(r"^\s*(?:git\s+tag(?:\s+-[asfm]\s*(?:\"[^\"]*\"|'[^']*'|\S+)?)*\s+[^-\s]|gh\s+release\s+create\b)")


class ReleaseLines:
    """The shell lines of a call that tag a version or publish a release."""

    @staticmethod
    def found(parts: tuple[str, ...]) -> list[str]:
        return [part for part in parts if RELEASE.search(part)]
