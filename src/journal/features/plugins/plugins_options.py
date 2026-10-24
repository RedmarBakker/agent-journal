from journal.support.option import Option


class PluginsOptions:
    """The options of the plugins feature."""

    PLUGIN_ANSWER_WINDOW = Option("plugins.hold_window_ms", "A plugin's hold window at most", "Milliseconds a plugin holding an event may take to answer; a plugin's own window in its manifest is cut to this, and one past its window is skipped and its fault recorded", 50, unit="ms")
