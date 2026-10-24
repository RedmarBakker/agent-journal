from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class SharingOptions:
    """The options of the sharing feature."""

    HOST = Option("sharing.host", "Tunler server", "The tunler server that gives this journal its web address; empty uses the one tunler is logged in to", "", kind="text", scope=OptionScope.MACHINE, setter=USER)
