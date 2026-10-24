class DeskBusy(Exception):
    """The journal server cannot take the sync carrier's call now: it is not running, or it is starting. The carrier waits and tries again, and records no fault of the team's."""
