from threading import Timer
import time


class ProductionWatchdog:
    """Stop only processes created for this batch when an approved deadline arrives."""

    def __init__(self) -> None:
        self.drivers = {}
        self.timers = {}
        self.active = None

    def register(self, driver) -> None:
        self.drivers[driver.run_id] = driver
        self.active = driver

    def arm(self, owner: str, deadline: float) -> bool:
        self.stop_timer(owner)
        timer = Timer(max(0.0, deadline - time.monotonic()), self.expire, args=(owner,))
        timer.daemon = True
        self.timers[owner] = timer
        timer.start()
        return True

    def stop(self, owner: str, reason: str) -> bool:
        self.stop_timer(owner)
        driver = self.active if owner.startswith("batch:") else self.drivers.get(owner)
        return True if driver is None else driver.stop_owned(reason)

    def expire(self, owner: str) -> None:
        driver = self.active if owner.startswith("batch:") else self.drivers.get(owner)
        if driver is None or driver.caps is None:
            self.stop(owner, "approved wall-time cap reached")
            return
        cap = "batch_elapsed_minutes" if owner.startswith("batch:") else "run_wall_minutes"
        try:
            driver.caps.refuse_at_cap(driver.caps.read(), cap, "approved wall-time cap reached")
        except ValueError:
            return

    def stop_timer(self, owner: str) -> None:
        timer = self.timers.pop(owner, None)
        if timer:
            timer.cancel()
