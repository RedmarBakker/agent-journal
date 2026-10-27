from journal.support.option import Option


class ShellOptions:
    """The options of the shell feature."""

    DISMISSAL_LIMIT = Option("shell.report_dismissals", "Dismissals before a reader finding is not raised", "Times the agent may dismiss the same finding of a reader report, such as a card that showed no progress, for one command before the journal stops raising that finding for that command for the hours below; 0 keeps raising it", 3, unit="dismissals")
    PAUSE_HOURS = Option("shell.report_pause_hours", "Hours a dismissed reader finding is not raised", "Hours the journal does not raise a reader report finding for a command after the agent dismissed it the times above", 24, unit="hours")
    MESSAGE_FOREGROUND_LIMIT = Option("shell.foreground_while_waiting", "In the foreground while a message waits", "The same limit while the user has an unread or unanswered message, so they are not kept waiting", 10, unit="seconds")
    SHOWN = Option("shell.shown_lines", "Show of an output or a file", "The first and last so many lines of a command's output or a file; a file longer than twice this is not read whole", 200, unit="lines")
    READ_SHOWN = Option("shell.read_characters", "Show of a command that reads", "The characters of a reading command's output shown, half from each end, such as cat, grep or git diff; past it the agent reads the rest by the output's number", 8000, unit="characters")
    COMMAND_SHOWN = Option("shell.command_characters", "Show any other command's output up to", "Any other command's output, such as a test run or a build, is shown whole up to this; past it only a line naming the output, which the agent reads by its number", 400, unit="characters")
    SHORT = Option("shell.short_output", "Keep no output under", "A command whose whole output is under this many characters, with no pipe in its line, is shown as it is and kept as no numbered output; a longer one, or a line with a pipe into head, tail, grep or any filter, is kept", 400, unit="characters")
    UNREAD_OUTPUT_INTERVAL = Option("shell.unread_output_every", "Name an unread output again after", "Tool uses after the agent was told a background command ended, while it has not read its output, before it is told again; an idle agent is told again after the seconds a command runs in the foreground", 5, unit="tool uses")
    OUTPUT_DOCK = Option("shell.dock_live_outputs", "Dock live outputs", "A watched command's card is docked above the chat as soon as it runs, and taken down once it ends; a card you dock by hand stays until you close it", True, option_type="switch")
    OUTPUT_COUNT = Option("shell.outputs_kept", "Keep the outputs of the last", "Command outputs kept as numbered rows with their files; past this the oldest go", 250, unit="commands")
    READER_SUGGESTIONS = Option("shell.reader_suggestions", "Reader suggestions in a session", "The most times in one session the journal suggests a reader for a run that ended in the background with no reader to read it; 0 turns the suggestions off", 3, unit="suggestions")
    READER_SUGGESTION_RUNS = Option("shell.reader_suggestion_runs", "Suggest a reader again after", "Runs of a command moved to the background, still with no reader, before its reader is suggested again; 0 suggests it only once", 50, unit="runs")
