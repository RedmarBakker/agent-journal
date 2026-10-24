class JournalBusy(Exception):
    """The journal server is down, starting, or started again with a new secret: the sync waits quietly and tries again."""
