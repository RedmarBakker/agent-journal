import socket


class FreePort:
    """A port on this machine that nothing listens on now, as the system hands one out."""

    @staticmethod
    def number() -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]
