class ForegroundLimit:
    """How long a command may run in the foreground before it moves to the background."""

    LIMIT_SECONDS = 15

    # @sin CommentAboveMethodDetector
    # a run known to take long moves to the background at once
    def is_long_run(self, line: str) -> bool:
        return line.startswith("pytest")

    # @righteous CommentAboveMethodDetector
    def is_short_run(self, line: str) -> bool:
        return not self.is_long_run(line)

    # @righteous CommentAboveMethodDetector
    def seconds(self) -> int:
        return self.LIMIT_SECONDS


# @sin CommentAboveMethodDetector
# the limit read from a setting
def limit_of(setting: int) -> int:
    return setting


# @righteous CommentAboveMethodDetector
def plain_limit(setting: int) -> int:
    return setting
