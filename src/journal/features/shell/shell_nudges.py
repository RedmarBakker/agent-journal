from journal.engine.nudge import Nudge
from journal.models.reader_report import ReaderReport
from journal.support.timeout import Timeout


class ShellNudges:
    """The nudges of the shell feature."""

    READER_NEEDED = Nudge("shell", "reader_needed", "no reader reads {{commands}}, run in the background", "`journal reader add <name> --commands \"<command>\" --about '<what it picks>' --label '<what it does>' --pattern '<the lines worth seeing: failures and summary>' --progress '<a percent or a count of a total>'`", repeat=Timeout.seconds(0))
    REPORT_RAISED = Nudge("shell", "reader_report_raised", "reader report {{n}}: its reader showed a run poorly", "`journal reader report {{n}}` shows how to fix it", repeat=Timeout.seconds(0))
    REPORT_REFUTED = Nudge("shell", "reader_report_dismissal_refuted", "your dismissal was checked against the run's output and found wrong, {{verdicts}}", "write the reader anew with `journal reader add`: a refuted report is never dismissed again", repeat=Timeout.seconds(0))
    OUTPUT_STORED = Nudge("shell", "output_kept", "output {{n}}: {{counts}}{{part}}", repeat=Timeout.seconds(0))
    OUTPUT_PART_STORED = Nudge("shell", "output_part_kept", "output {{n}} also holds part {{part}}: {{counts}}", repeat=Timeout.seconds(0))
    BACKGROUND_MOVE = Nudge("shell", "moved_to_the_background", "moved to the background as output {{n}}", repeat=Timeout.seconds(0))
    OUTPUTS_ENDED = Nudge("shell", "outputs_ended", "{{outputs}}", "`journal output read {{n}} --summary` says how", repeat=Timeout.seconds(0))
    READER_HINT = Nudge("shell", "use_the_reader", "reader {{reader}} already reads this: {{about}}", "`journal output read N --reader {{reader}}`", repeat=Timeout.seconds(0))
    READER_GUESSED = Nudge("shell", "guessed_a_reader", "reading it with {{reader}}: {{about}}", "it stays when you do nothing more; write your own with `journal reader add <name> --commands \"{{command}}\" ...`", repeat=Timeout.seconds(0))
    READER_SUGGESTION = Nudge("shell", "add_a_reader", "you read outputs this way again: {{command}}", "`journal reader add <name> --pattern <regex> --about \"<what it picks>\"`, then `journal output read N --reader <name>`", repeat=Timeout.seconds(0))
    PARTIAL_FILE_READ = Nudge("shell", "read_the_file_in_parts", "the file has {{lines}} lines, more than the {{cap}} shown at each end", "read it in parts with offset and limit, or grep for the line you need", repeat=Timeout.seconds(0))
    FOLDER_CHANGE_REFUSAL = Nudge("shell", "folder_change_refused", "cd {{target}} would move your shell for every later command", "use a subshell, ( cd {{target}} && … ), or give the command the folder (git -C, npm --prefix, a path relative to the project)", repeat=Timeout.seconds(0))
    SILENT_RUN_HINT = Nudge("shell", "silent_run_streams", "output {{n}} has printed nothing for {{seconds}} seconds while it runs: the command buffers its output, which no reader can show", "run it so it prints as it goes: stdbuf -oL before it, python -u or PYTHONUNBUFFERED=1 for Python, go test -json in place of -v, or the flag of its own that streams; a reader change cannot fix it", repeat=Timeout.seconds(0))
    PROJECT_PATH_REFUSAL = Nudge("shell", "project_path_refused", "the command uses the absolute path of this project, so its card and its process show only the path", "your shell is already in the project folder: run it relative to it, {{line}}", repeat=Timeout.seconds(0))
    JOURNAL_POLL = Nudge("shell", "journal_poll_refused", "a shell loop that polls journal commands is refused", "wait with journal await \"<what you wait for>\" --output {{n}}, which ends when the output does", repeat=Timeout.seconds(0))
    JOURNAL_COMMAND_ISOLATION = Nudge("shell", "journal_command_runs_alone", "You cannot mix journal commands with other commands.", repeat=Timeout.seconds(0))
    BACKGROUND_CHECK = Nudge("shell", "check_the_background", "output {{background_outputs}} still running", "look at it; hung or stuck: stop it and say why", repeat=Timeout.seconds(300), blocks_regardless=True)
    WATCH_VIEW = Nudge("shell", "watched_output", "output {{n}}, {{command}}:\n{{lines}}", repeat=Timeout.seconds(0))
    UNREAD_OUTPUT = Nudge("shell", "unread_output", "{{outputs}}, and you have not read it yet", repeat=Timeout.seconds(0))
    WATCH_ENDED = Nudge("shell", "watched_output_ended", "output {{n}}, {{command}}, {{ending}}:\n{{lines}}", repeat=Timeout.seconds(0))
    WATCH_SUGGESTION = Nudge("shell", "watch_it_live", "watch it: `journal output watch {{n}}{{reader}} --title \"<what it is doing>\"`", "or `journal await \"<what>\" --output {{n}}{{reader}}` to wait on it", repeat=Timeout.seconds(0))
    PIPED_JOURNAL_COMMAND = Nudge("shell", "journal_command_piped_into_a_filter", "journal {{command}} piped into {{filter}} hides the lines the journal speaks", "run it on its own and read all of its answer", repeat=Timeout.seconds(0))
    PIPED_TEST_RUN = Nudge("shell", "test_run_piped_into_a_filter", "a test run piped into {{filter}} hides the lines its reader reads, so its mark shows no progress and its output is cut", "run it whole with `journal suite <args>`, then read its output by its number with `journal output read N --reader pytest` or `--grep \"<words>\"`", repeat=Timeout.seconds(0))
    COUNTING_READER_SUGGESTION = Nudge("shell", "counting_reader_suggestion", "optional: no reader counts passed and failed for {{command}}", "`journal reader add <name> --commands \"{{command}}\" --pattern '<failures>' --progress '<count of a total>' --finished '<summary>' --failed '<failures>' --label 'Running tests'`", repeat=Timeout.seconds(0))
    NEW_READER_SUGGESTION = Nudge("shell", "make_its_reader", "no reader reads {{command}} yet", "`journal reader add <name> --commands \"{{command}}\" --pattern '<failures and summary>' --progress '<percent or count of a total>' --label 'Running tests'`", repeat=Timeout.seconds(0))
    ALIAS_TIME_LIMIT = Nudge("shell", "drop_alias_time_limit", "the journal watches alias {{name}}, so it needs no time limit wrapper", "edit it with journal alias edit {{name}} --line and this line: {{line}}", repeat=Timeout.seconds(0))
    LINE_TIME_LIMIT = Nudge("shell", "drop_line_time_limit", "{{command}} needs no time limit wrapper here", repeat=Timeout.seconds(0))
    READER_TOPIC = Nudge("shell", "give_the_reader_a_topic", "{{command}} has run with {{count}} different arguments", "give the reader {{reader}} a --topic pattern over the command line, such as the files or the -k it names", repeat=Timeout.seconds(0))
    READER_WATCH = Nudge("shell", "watched_reader_output", "output {{n}} ({{command}}) is in the background, watched through {{reader}}", repeat=Timeout.seconds(0))
    ALIAS_WATCH = Nudge("shell", "watched_alias_output", "output {{n}}, the run of journal {{name}}, is watched{{reader}}", repeat=Timeout.seconds(0))
    ALIASED_LINE = Nudge("shell", "aliased_line_refused", "journal {{name}} runs this line: {{line}}", "run `journal {{name}} [args]` instead: its reader and its card come with the alias", repeat=Timeout.seconds(0))
    MORE_SPECIFIC_ALIAS = Nudge("shell", "more_specific_alias_refused", "journal {{name}} runs what this run of journal {{called}} runs: {{line}}", "run `journal {{name}} [args]` instead: its reader and its card come with that alias", repeat=Timeout.seconds(0))
    ALIAS_SUGGESTION = Nudge("shell", "add_an_alias", "you ran {{shape}} three times or more", "`journal alias add <name> \"<the line without the values that change>\"{{reader}}`, then `journal <name> <values>`", repeat=Timeout.seconds(0))

    @staticmethod
    def report_refutations(reports: tuple[ReaderReport, ...]) -> str:
        return "; ".join(f"reader report {report.id}: {report.verdict}" for report in reports)
