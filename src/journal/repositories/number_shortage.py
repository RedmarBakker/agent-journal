class NumberShortage(Exception):
    """A shared table has no row number left in this machine's blocks and the team server could not be reached for more: the write fails as a fault, so a hook lets its event through rather than refusing it."""
