class JournalMismatch(Exception):
    """The journal server speaks another version of the sync doors than this service, a fault until both run the same code."""
