from dataclasses import dataclass


@dataclass(frozen=True)
class ClientError:
    """One distinct console error of the viewer, its stack, and how many times it was posted."""

    message: str
    stack: str
    count: int = 1

    def repeated(self) -> "ClientError":
        return ClientError(self.message, self.stack, self.count + 1)

    def line(self) -> str:
        return f"{self.count}x {self.message}" + (f"\n{self.stack}" if self.stack else "")
