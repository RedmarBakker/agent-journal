from journal.support.option import Option


class ShellOptions:
    """The options of the shell feature."""

    REPORT_READ_LIMIT = Option("shell.report_read_after", "Hold the write after a reader report for", "Tool uses the agent may make after the reader judge reports a reader that fell short, each told how many are left, before its next write waits until it reads the report", 5, unit="tool uses")
    REPORT_FIX_LIMIT = Option("shell.report_fix_after", "Hold the write after a reader report was read for", "Tool uses the agent may make after reading a reader report, each told how many are left, before its next write waits until the reader is written anew or the report dismissed", 10, unit="tool uses")
    READER_LIMIT = Option("shell.reader_after", "Hold the write after", "Tool uses the agent may make after a command first runs in the background with no reader, each told how many are left, before its next write waits for a reader with a label that reads it", 5, unit="tool uses")
    MESSAGE_FOREGROUND_LIMIT = Option("shell.foreground_while_waiting", "In the foreground while a message waits", "The same limit while the user has an unread or unanswered message, so they are not kept waiting", 10, unit="seconds")
    SHOWN = Option("shell.shown_lines", "Show of an output or a file", "The first and last so many lines of a command's output or a file; a file longer than twice this is not read whole", 200, unit="lines")
    READ_SHOWN = Option("shell.read_characters", "Show of a command that reads", "The characters of a reading command's output shown, half from each end, such as cat, grep or git diff; past it the agent reads the rest by the output's number", 8000, unit="characters")
    COMMAND_SHOWN = Option("shell.command_characters", "Show any other command's output up to", "Any other command's output, such as a test run or a build, is shown whole up to this; past it only a line naming the output, which the agent reads by its number", 400, unit="characters")
    SHORT = Option("shell.short_output", "Keep no output under", "A command whose whole output is under this many characters, with no pipe in its line, is shown as it is and kept as no numbered output; a longer one, or a line with a pipe into head, tail, grep or any filter, is kept", 400, unit="characters")
    UNREAD_OUTPUT_INTERVAL = Option("shell.unread_output_every", "Name an unread output again after", "Tool uses after the agent was told a background command ended, while it has not read its output, before it is told again; an idle agent is told again after the seconds a command runs in the foreground", 5, unit="tool uses")
    OUTPUT_DOCK = Option("shell.dock_live_outputs", "Dock live outputs", "A watched command's card is docked above the chat as soon as it runs, and taken down once it ends; a card you dock by hand stays until you close it", True, kind="switch")
    OUTPUT_COUNT = Option("shell.outputs_kept", "Keep the outputs of the last", "Command outputs kept as numbered rows with their files; past this the oldest go", 250, unit="commands")
