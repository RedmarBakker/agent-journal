class Propagation:
    """The pass of one event down a state's listeners: a listener that stops it means the ones after it do not receive it, and the next pass starts it again."""

    def __init__(self) -> None:
        self.ongoing = True

    def stop(self) -> None:
        self.ongoing = False

    def reset(self) -> None:
        self.ongoing = True
