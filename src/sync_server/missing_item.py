from sync_server.refusal import Refusal


class MissingItem(Refusal):
    """Something asked for that is not there, a library item or version or a stored file, answered 404 rather than refused."""
