from dataclasses import dataclass


@dataclass(frozen=True)
class HookMeasure:
    """What a hook's thread read of its own time before it answered, the time since the hook script started and the wait for the boot, stored on the hook's entry after the answer."""

    elapsed_ms: int
    boot_wait_ms: int

    def recorded(self) -> dict:
        return {"hook_ms": self.elapsed_ms, "boot_wait_ms": self.boot_wait_ms}
