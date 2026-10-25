from enum import StrEnum


class DocEditMode(StrEnum):
    """Who may change a document: only its owner and an admin when it is on the hub read-only, any member when it is on the hub free to edit, and its own environment's when it is not on the hub."""

    LOCAL = "local"
    READ_ONLY = "read_only"
    FREE = "free"
