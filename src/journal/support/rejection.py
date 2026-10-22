class Rejection(Exception):
    """The journal refuses a write or a request; nothing happens and the caller is informed why."""
