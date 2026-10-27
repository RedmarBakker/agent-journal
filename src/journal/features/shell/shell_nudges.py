from journal.engine.nudge import Nudge
from journal.models.reader_report import ReaderReport
from journal.support.timeout import Timeout


class ShellNudges:
    """The nudges of the shell feature."""

    REPORT_RAISED = Nudge("shell", "reader_report_raised", "reader report {{n}}: a reader showed a run poorly", "see the fix with `journal reader report {{n}}`", repeat=Timeout.seconds(0))
    REPORT_REFUTED = Nudge("shell", "reader_report_dismissal_refuted", "you dismissed a report that was right: {{verdicts|cap=17}}", "fix the reader: `journal reader add <name> --pattern <regex>`", repeat=Timeout.seconds(0))
    OUTPUT_STORED = Nudge("shell", "output_kept", "output {{n}}: {{counts|cap=91}}{{part}}", repeat=Timeout.seconds(0))
    OUTPUT_PART_STORED = Nudge("shell", "output_part_kept", "output {{n}} also contains part {{part}}: {{counts|cap=71}}", repeat=Timeout.seconds(0))
    BACKGROUND_MOVE = Nudge("shell", "moved_to_the_background", "moved to the background as output {{n}}", repeat=Timeout.seconds(0))
    OUTPUTS_ENDED = Nudge("shell", "outputs_ended", "output {{n}}: {{outcome}}", repeat=Timeout.seconds(0))
    READER_DRAFT = Nudge("shell", "draft_a_reader", "no reader reads {{part}} yet", "fill in `{{command}}` from this run's output and run it", repeat=Timeout.seconds(0))
    READER_HINT = Nudge("shell", "use_the_reader", "reader {{reader}} already reads this: {{about}}", "use `journal output read <n> --reader {{reader}}`", repeat=Timeout.seconds(0))
    PARTIAL_FILE_READ = Nudge("shell", "read_the_file_in_parts", "the file has {{lines|cap=12}} lines; {{cap}} show at each end", "read it by offset and limit, or grep the line you need", repeat=Timeout.seconds(0))
    FOLDER_CHANGE_REFUSAL = Nudge("shell", "folder_change_refused", "do not `cd {{target}}`: use `( cd {{target}} && \u2026 )` or pass the folder, such as `git -C`", "", repeat=Timeout.seconds(0))
    RUN_TOTAL_MISSING = Nudge("shell", "run_counts_without_a_total", "output {{n}} prints no total, so it has no progress bar", "give its reader a `--progress` pattern such as `(\\d+)/(\\d+)`", repeat=Timeout.seconds(0))
    SILENT_RUN_HINT = Nudge("shell", "silent_run_streams", "output {{n}} buffers: silent for {{seconds}} seconds", "run it with `stdbuf -oL`, `python -u` or its streaming flag", repeat=Timeout.seconds(0))
    PROJECT_PATH_REFUSAL = Nudge("shell", "project_path_refused", "do not use this project's absolute path; your shell is already in the project", "run: {{line|cap=35}}", repeat=Timeout.seconds(0))
    JOURNAL_POLL = Nudge("shell", "journal_poll_refused", "do not poll journal commands in a shell loop", "wait with `journal await \"<what you wait for>\" --output {{n}}`", repeat=Timeout.seconds(0))
    JOURNAL_COMMAND_ISOLATION = Nudge("shell", "journal_command_runs_alone", "run journal commands alone, not mixed with other commands", repeat=Timeout.seconds(0))
    BACKGROUND_CHECK = Nudge("shell", "check_the_background", "output {{background_outputs|cap=54}} still running", "check it; if it hangs, stop it and say why", repeat=Timeout.seconds(300), blocks_regardless=True)
    WATCH_VIEW = Nudge("shell", "watched_output", "output {{n}}: {{progress}}", repeat=Timeout.seconds(0))
    UNREAD_OUTPUT = Nudge("shell", "unread_output", "{{outputs|cap=72}}, unread. read it with `journal output read <n>`", repeat=Timeout.seconds(0))
    WATCH_ENDED = Nudge("shell", "watched_output_ended", "output {{n}}: {{outcome}}", repeat=Timeout.seconds(0))
    PIPED_JOURNAL_COMMAND = Nudge("shell", "journal_command_piped_into_a_filter", "do not pipe journal {{command}} into {{filter}}", "run it alone and read its whole answer", repeat=Timeout.seconds(0))
    PIPED_TEST_RUN = Nudge("shell", "test_run_piped_into_a_filter", "do not pipe a test run into {{filter}}", "run `journal suite <args>`, then `journal output read <n> --reader pytest`", repeat=Timeout.seconds(0))
    ALIAS_TIME_LIMIT = Nudge("shell", "drop_alias_time_limit", "alias {{name}} needs no time limit: `journal alias edit {{name}} --line \"{{line|cap=26}}\"`", "", repeat=Timeout.seconds(0))
    LINE_TIME_LIMIT = Nudge("shell", "drop_line_time_limit", "remove the time limit wrapper from {{command}}; it needs none here", repeat=Timeout.seconds(0))
    READER_TOPIC = Nudge("shell", "give_the_reader_a_topic", "{{command}} ran with {{count}} different arguments", "give reader {{reader}} a `--topic` for them", repeat=Timeout.seconds(0))
    ALIASED_LINE = Nudge("shell", "aliased_line_refused", "alias journal {{name}} runs this line: {{line|cap=25}}", "run `journal {{name}} [args]` instead", repeat=Timeout.seconds(0))
    MORE_SPECIFIC_ALIAS = Nudge("shell", "more_specific_alias_refused", "journal {{name}} already runs this line: {{line|cap=23}}", "run `journal {{name}} [args]` instead", repeat=Timeout.seconds(0))
    COMPLETE_PROGRESS_RUN = Nudge("shell", "run_stands_at_100_percent", "output {{n}} at 100% for {{seconds}} seconds", "read `journal output read {{n}}`; give its reader a pattern for that step", repeat=Timeout.seconds(0))
    SHARED_TITLE = Nudge("shell", "give_each_run_its_own_title", "`{{first_line}}` and `{{second_line}}` share a title: give each a `--label \"<words>\"`", "", repeat=Timeout.seconds(0))
    FLAGGED_TITLE = Nudge("shell", "name_the_run_in_words", "output {{n}}'s title {{card_title}} is a flag or path", "title it in words: `journal output watch {{n}} --title \"<words>\"`", repeat=Timeout.seconds(0))
    ALIAS_SUGGESTION = Nudge("shell", "add_an_alias", "you ran {{shape}} often", "add an alias: `journal alias add <name> \"<line less its values>\"{{reader}}`", repeat=Timeout.seconds(0))

    @staticmethod
    def report_refutations(reports: tuple[ReaderReport, ...]) -> str:
        return "; ".join(f"reader report {report.id}: {report.verdict}" for report in reports)
