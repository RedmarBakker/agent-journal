from journal.engine.nudge import Nudge


class ShellNudges:
    """The nudges of the shell feature."""

    READER_COUNTDOWN = Nudge("shell", "writes_held_soon_until_read_through_a_reader", "reader due for {{commands}}: {{count}}", "`journal reader add <name> --commands \"<command>\" --about '<what it picks>' --label '<what it does>' --pattern '<the lines worth seeing: failures and summary>' --progress '<a percent or a count of a total>'`", repeat_interval=0)
    READER_LAST_USE = Nudge("shell", "next_write_held_until_read_through_a_reader", "reader due for {{commands}}: 0", "your next write waits until a reader with a label reads it", repeat_interval=0)
    READER_REFUSAL = Nudge("shell", "write_held_until_read_through_a_reader", "no reader reads {{commands}}, run in the background", "`journal reader add <name> --commands \"<command>\" --about '<what it picks>' --label '<what it does>' --pattern '<lines worth seeing>' --progress '<progress>'` before any other write", repeat_interval=0)
    BACKGROUND_MOVE = Nudge("shell", "moved_to_the_background", "moved to the background as output {{n}}", repeat_interval=0)
    OUTPUTS_ENDED = Nudge("shell", "outputs_ended", "{{outputs}}", "`journal output read {{n}} --summary` says how", repeat_interval=0)
    READER_HINT = Nudge("shell", "use_the_reader", "reader {{reader}} already reads this: {{about}}", "`journal output read N --reader {{reader}}`", repeat_interval=0)
    READER_SUGGESTION = Nudge("shell", "add_a_reader", "you read outputs this way again: {{command}}", "`journal reader add <name> --pattern <regex> --about \"<what it picks>\"`, then `journal output read N --reader <name>`", repeat_interval=0)
    PARTIAL_FILE_READ = Nudge("shell", "read_the_file_in_parts", "the file has {{lines}} lines, more than the {{cap}} shown at each end", "read it in parts with offset and limit, or grep for the line you need", repeat_interval=0)
    FOLDER_CHANGE_REFUSAL = Nudge("shell", "folder_change_refused", "cd {{target}} would move your shell for every later command", "use a subshell, ( cd {{target}} && … ), or give the command the folder (git -C, npm --prefix, an absolute path)", repeat_interval=0)
    JOURNAL_COMMAND_ISOLATION = Nudge("shell", "journal_command_runs_alone", "You cannot mix journal commands with other commands.", repeat_interval=0)
    BACKGROUND_CHECK = Nudge("shell", "check_the_background", "output {{background_outputs}} still running", "look at it; hung or stuck: stop it and say why", repeat_interval=300, blocks_regardless=True)
    WATCH_VIEW = Nudge("shell", "watched_output", "output {{n}}, which you watch:\n{{lines}}", repeat_interval=0)
    UNREAD_OUTPUT = Nudge("shell", "unread_output", "{{outputs}}, and you have not read it yet", repeat_interval=0)
    WATCH_ENDED = Nudge("shell", "watched_output_ended", "output {{n}}, which you watched, {{ending}}:\n{{lines}}", repeat_interval=0)
    WATCH_SUGGESTION = Nudge("shell", "watch_it_live", "watch it: `journal output watch {{n}}{{reader}} --title \"<what it is doing>\"`", "or `journal await \"<what>\" --output {{n}}{{reader}}` to wait on it", repeat_interval=0)
    PIPED_TEST_RUN = Nudge("shell", "test_run_piped_into_a_filter", "a test run piped into {{filter}} hides the lines its reader reads, so its mark shows no progress and its output is cut", "run it whole with `journal suite <args>`, then read its output by its number with `journal output read N --reader pytest` or `--grep \"<words>\"`", repeat_interval=0)
    COUNTING_READER_SUGGESTION = Nudge("shell", "counting_reader_suggestion", "optional: no reader counts passed and failed for {{command}}", "`journal reader add <name> --commands \"{{command}}\" --pattern '<failures>' --progress '<count of a total>' --finished '<summary>' --failed '<failures>' --label 'Running tests'`", repeat_interval=0)
    NEW_READER_SUGGESTION = Nudge("shell", "make_its_reader", "no reader reads {{command}} yet", "`journal reader add <name> --commands \"{{command}}\" --pattern '<failures and summary>' --progress '<percent or count of a total>' --label 'Running tests'`", repeat_interval=0)
    ALIAS_TIME_LIMIT = Nudge("shell", "drop_alias_time_limit", "the journal watches alias {{name}}, so it needs no time limit wrapper", "edit it with journal alias edit {{name}} --line and this line: {{line}}", repeat_interval=0)
    LINE_TIME_LIMIT = Nudge("shell", "drop_line_time_limit", "{{command}} needs no time limit wrapper here", repeat_interval=0)
    READER_FIX = Nudge("shell", "fix_the_reader", "the reader {{reader}} put a line on output {{n}}'s card that does not read well: {{line}}", "narrow its pattern to short lines such as the summary: `journal reader add {{reader}} --pattern '<those lines>' ...`", repeat_interval=0)
    READER_REWRITE_REQUEST = Nudge("shell", "fix_the_reader_first", "the reader {{reader}} was asked three times to read better", "write it anew first, `journal reader add {{reader}} --pattern '<short lines>' ...`; your other tools wait until then", repeat_interval=0)
    READER_REWRITE_NOTICE = Nudge("shell", "reader_written_anew", "the reader {{reader}} is written anew, and your tools are free", repeat_interval=0)
    SUMMARY_REQUEST = Nudge("shell", "make_the_run_print_its_summary", "output {{n}}'s card ends on counts from its dots: the run printed no summary line", "for pytest, take a doubled -q (-qq) out of the command and the project's pytest settings", repeat_interval=0)
    READER_DETAIL = Nudge("shell", "give_the_reader_its_summary", "output {{n}}'s card showed only its title: the reader {{reader}} picked nothing", "`journal reader add {{reader}} --pattern '<failures and summary>' --progress '<percent or count>' --label '<what it is doing>'`", repeat_interval=0)
    SILENT_CARD = Nudge("shell", "silent_card", "output {{n}}'s card has shown nothing for 30 seconds{{reader}}", "{{advice}}", repeat_interval=0)
    READER_TOPIC = Nudge("shell", "give_the_reader_a_topic", "{{command}} has run with {{count}} different arguments", "give the reader {{reader}} a --topic pattern over the command line, such as the files or the -k it names", repeat_interval=0)
    READER_WATCH = Nudge("shell", "watched_reader_output", "output {{n}} ({{command}}) is in the background, watched through {{reader}}", repeat_interval=0)
    ALIAS_WATCH = Nudge("shell", "watched_alias_output", "output {{n}}, the run of journal {{name}}, is watched{{reader}}", repeat_interval=0)
    ALIAS_HINT = Nudge("shell", "use_the_alias", "journal {{name}} runs this line: {{line}}", "use `journal {{name}} [args]` next time", repeat_interval=0)
    ALIAS_SUGGESTION = Nudge("shell", "add_an_alias", "you ran {{shape}} three times or more", "`journal alias add <name> \"<the line without the values that change>\"{{reader}}`, then `journal <name> <values>`", repeat_interval=0)

    @classmethod
    def reader_countdown(cls, commands: tuple[str, ...], remaining_uses: int) -> Nudge:
        listing = ", ".join(commands)
        return cls.READER_COUNTDOWN.create(count=remaining_uses, commands=listing) if remaining_uses else cls.READER_LAST_USE.create(commands=listing)
