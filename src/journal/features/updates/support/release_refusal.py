class ReleaseRefusal(OSError):
    """GitHub refused to list the releases because this address asked too often: the time its limit resets, after which the journal looks again."""

    def __init__(self, reset_at: float) -> None:
        super().__init__(f"GitHub refuses more looks until {reset_at:.0f}")
        self.reset_at = reset_at
