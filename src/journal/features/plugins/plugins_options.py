from journal.support.option import Option


class PluginsOptions:
    """The options of the plugins feature."""

    STREAK_LIMIT = Option("plugins.holds_in_a_row", "Pass a plugin over after holds in a row", "Holds by one plugin in a row, with nothing of the agent's getting through, after which its holds are passed over for a while so it can never hold the agent in a loop; 0 never passes it over", 5, unit="holds")
    IGNORE_MINUTES = Option("plugins.passed_over_minutes", "Pass a looping plugin over for", "Minutes a plugin that held the agent too many times in a row has its holds passed over before it is heard again", 3, unit="minutes")
    CLOCK_OUT_WINDOW_SECONDS = Option("plugins.clock_out_window_seconds", "A plugin may hold a worker's clock-out for", "Seconds a plugin that holds a worker's clock-out, such as a judge of the worker's own commit, may take to answer, before the journal rebases the work and runs its tests; its own window in its manifest is cut to this", 180, unit="seconds")
    PLUGIN_ANSWER_WINDOW = Option("plugins.hold_window_ms", "A plugin's hold window at most", "Milliseconds a plugin holding an event may take to answer; a plugin's own window in its manifest is cut to this, and one past its window is skipped and its fault recorded", 50, unit="ms")
