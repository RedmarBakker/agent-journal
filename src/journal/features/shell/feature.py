from journal.features.shell.seeds.stray_reader_cleanup import StrayReaderCleanup
from journal.features.shell.seeds.stray_command_mark_cleanup import StrayCommandMarkCleanup
from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import WORK
from journal.support.card_type import CardType
from journal.support.card_colouring import CardColouring
from journal.events.rows.reader_report_raised import ReaderReportRaised
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.features.feature import Feature
from journal.features.shell.listeners.output_notice import OutputNotice
from journal.features.shell.listeners.quiet_run_record import QuietRunRecord
from journal.features.shell.listeners.untotaled_run_record import UntotaledRunRecord
from journal.features.shell.listeners.stopped_output_end import StoppedOutputEnd
from journal.features.shell.listeners.watch_update import WatchUpdate
from journal.features.shell.listeners.output_card import OutputCard
from journal.features.shell.jobs.run_card_start import RunCardStart
from journal.features.shell.listeners.changed_output_card import ChangedOutputCard
from journal.features.shell.listeners.reader_output_cards import ReaderOutputCards
from journal.features.shell.listeners.reader_judgement import ReaderJudgement
from journal.features.shell.listeners.guessed_reader_card import GuessedReaderCard
from journal.features.shell.listeners.reader_suggestion_clear import ReaderSuggestionClear
from journal.features.shell.listeners.reader_suggestion_record import ReaderSuggestionRecord
from journal.features.shell.shell_conduct import ShellConduct
from journal.features.shell.support.shell_data_reader import ShellDataReader
from journal.features.shell.support.shell_data import ShellData
from journal.features.shell.commands.output_command import OutputCommand
from journal.features.shell.commands.reader_command import ReaderCommand
from journal.support.skill import Skill
from journal.features.shell.seeds.cut_off_outputs import CutOffOutputs
from journal.features.shell.jobs.restart_wait import RestartWait
from journal.features.shell.jobs.watched_run_check import WatchedRunCheck
from journal.features.shell.jobs.watch_refresh import WatchRefresh
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.seeds.default_readers import DefaultReaders
from journal.features.shell.seeds.project_readers_clear import ProjectReadersClear
from journal.features.shell.seeds.journal_output_readers import JournalOutputReaders
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.shell_part import ShellPart
from journal.features.shell.support.streaming_form import COUNTING
from journal.features.shell.support.activity_title import TITLE_RULE


class Shell(Feature[ShellData]):
    FOREGROUND = FOREGROUND_OPTION
    name = ShellPart.name
    card_families = (CardFamily("commands", "Commands", "terminal", WORK, CardColouring.OUTCOME),)
    card_types = (CardTypeEntry(CardType.COMMANDS, "Long commands and outputs", "commands"),)
    title = "Shell commands"
    help = "A chained command is run part by part, each recorded with its output and its duration; one that runs past fifteen seconds, or ten while a message of yours waits, goes to the background and the agent is told when it ends."
    commands = (OutputCommand, ReaderCommand)
    options = (FOREGROUND_OPTION, ShellOptions.DISMISSAL_LIMIT, ShellOptions.PAUSE_HOURS, ShellOptions.MESSAGE_FOREGROUND_LIMIT, ShellOptions.SHOWN, ShellOptions.READ_SHOWN, ShellOptions.COMMAND_SHOWN, ShellOptions.SHORT, ShellOptions.UNREAD_OUTPUT_INTERVAL, ShellOptions.OUTPUT_DOCK, ShellOptions.OUTPUT_COUNT, ShellOptions.READER_SUGGESTIONS, ShellOptions.READER_SUGGESTION_RUNS)
    listeners = (OutputNotice, QuietRunRecord, UntotaledRunRecord, StoppedOutputEnd, WatchUpdate, OutputCard, ChangedOutputCard, ReaderOutputCards, ReaderJudgement, ReaderSuggestionRecord, ReaderSuggestionClear, GuessedReaderCard)
    seeds = (CutOffOutputs, ProjectReadersClear, DefaultReaders, JournalOutputReaders, StrayCommandMarkCleanup, StrayReaderCleanup)
    jobs = (WatchRefresh, RestartWait, RunCardStart, WatchedRunCheck)
    process_cards = (OutputProcessCard,)
    data = (ShellDataReader,)
    conduct = (ShellConduct,)

    nudges = (ShellNudges.JOURNAL_POLL, ShellNudges.PIPED_JOURNAL_COMMAND, ShellNudges.REPORT_REFUTED, ShellNudges.REPORT_RAISED, ShellNudges.OUTPUT_STORED, ShellNudges.OUTPUT_PART_STORED, ShellNudges.ALIAS_TIME_LIMIT, ShellNudges.LINE_TIME_LIMIT, ShellNudges.READER_TOPIC, ShellNudges.READER_WATCH, ShellNudges.ALIAS_WATCH, ShellNudges.ALIASED_LINE, ShellNudges.MORE_SPECIFIC_ALIAS, ShellNudges.ALIAS_SUGGESTION, ShellNudges.WATCH_VIEW, ShellNudges.WATCH_ENDED, ShellNudges.PIPED_TEST_RUN, ShellNudges.BACKGROUND_MOVE, ShellNudges.OUTPUTS_ENDED, ShellNudges.UNREAD_OUTPUT, ShellNudges.JOURNAL_COMMAND_ISOLATION, ShellNudges.FOLDER_CHANGE_REFUSAL, ShellNudges.PROJECT_PATH_REFUSAL, ShellNudges.BACKGROUND_CHECK, ShellNudges.SILENT_RUN_HINT, ShellNudges.RUN_TOTAL_MISSING, ShellNudges.READER_DRAFT, ShellNudges.READER_HINT, ShellNudges.PARTIAL_FILE_READ, ShellNudges.FLAGGED_TITLE, ShellNudges.COMPLETE_PROGRESS_RUN)

    skill = Skill("shell", 'How the journal runs your shell commands: in parts, timed, and in the background past the limit', """
# Shell commands

Every shell command you run goes through the journal's runner.

- A line chained with `&&` or `;` is run part by part; each part is recorded with what it printed and how long it took,
  and a failing part stops the chain where the shell would have.
- A command that runs past fifteen seconds, or ten while a message of the user's is waiting, is moved to the background with
  the rest of its chain: the tool call returns with its output number, and you are informed when output N ends. Until you
  read it, by `journal output read N` or `status N`, it is named again every five tool uses, or after thirty idle seconds.
- A command whose whole output is under 400 characters, with no pipe in its line, prints as it is and is stored as no
  output. Any other command's output is stored as a numbered output, the newest 250 of them. `journal output read N` needs a flag
  naming the part: `--tail 20`, `--head 20`, `--grep "<words>"`, `--lines 100-160`, `--reader <name>`, `--summary` for
  how it ended with its first and last lines, or `--all` for every line when you need it in full. `journal output
  list` names the newest. `journal output status N` says in one line whether it is running, finished or failed with code C;
  without a number it names each of your background outputs with its status. Read an output this way, never by running the command again nor by reading its files raw.
- A reader reads outputs of one shape, such as a test run's failures: `journal reader add <name> --pattern <regex>
  --about "<what it picks>"`, or `--script <file>` for a shell script that receives the output on its input. Use it with
  `journal output read N --reader <name>`; `journal reader list` names the project's readers. The second time you
  read the same shape of output by hand, add a reader for it and say so in the chat.
- `journal output watch N [--reader <name>] [--title "<words>"]` attaches a running output to you: after every tool use you are
  shown the lines its reader picks, or its last ten lines with no reader, and a card in the chat shows the same, updated in
  place. The card is for the user: its title says what the run is doing in plain words, `--title "Running tests"`, else
  the reader's label, else what the command does; the command line shows only when the user opens the card. The
  watch ends by itself when the command ends, and you are informed once how it ended; `journal output unwatch` ends it
  sooner. One output is watched at a time. A reader written for a watch picks few lines that read well in the card, and
  may show how far the command has progressed: `--progress <regex>` takes the last match, its groups a percentage such as
  `\\[(\\d+)%\\]` or a count of a total such as `(\\d+)/(\\d+)`, shown as a bar in the card, and `--label "<words>"` says what the run is doing, such as Running tests or Building the
  application, never a bare name such as Tests nor a half sentence that stops on of or the: """ + TITLE_RULE + """; `--topic '<pattern>'`, read over the command line, adds what a run is about
  after the title, such as the test files or the -k a line names, for a command run with different arguments.
  A run over several suites, packages or shards shows its progress too: """ + COUNTING + """.
  `--finished '<pattern>'` and `--failed '<pattern>'` pick other lines once the command finished or failed, such as its summary
  `--summary '<pattern>'` is the summary reader: the last match in the output, its groups joined, is the summary the card shows when opened, such as '(\\d+ failed), (\\d+ passed)'
  or its failures; a script reader finds which in JOURNAL_OUTPUT_STAGE: running, finished or failed.
- A reader names the commands whose output it reads, `--commands "pytest"`, and a command moved to the background that
  runs one is instructed to watch it with that reader, so one reader serves every later run. When a run moved to the
  background ends and no reader reads it, a test run, a build, an install or a long process, or a command whose output you
  read by hand twice, the line naming its end says once `no reader reads <part> yet` with a `journal reader add` filled
  from that run's output: the starting reader of its kind and the lines it saw. The add tries it on the stored runs and
  refuses it naming what it missed, such as the counts of a passing or a failing run, or a --progress that matches no line;
  fix what it names and add it again. A reader the journal made on its own reads the run at once and the user sees a card
  for it: keep it, or write your own over it. The journal ships readers for pytest, dotnet test and phpunit
  or pest in .journal/readers as examples. Waiting on a command, `journal await "<what>" --output N --reader <name>`
  watches it too, so the user sees it progress while you wait.
- A test run, a build or any other command's output is shown in full up to 400 characters; past that you see only a
  line naming the output to read by its number, with its lines, its characters and the part of the line it belongs to. A command that reads (cat, grep, sed, git diff) is shown up to 8,000
  characters, past that by its two ends. A line of journal commands is shown in full and stored as no output.
- A command that only reads or edits the project's own code, a file, a folder or a glob under the project and outside .journal, runs as written, pipes and all,
  in the shell itself: nothing of it is captured, recorded or stored, and `grep -n x src/app.py | tail -5` answers at once. Any other command's trailing output shapers, `| tail`, `| head`, `| grep`, `| cut`, `| sort`, `| uniq`, `| wc`, `| sed -n`, `| awk`, `| jq` and the like, are removed from the line: the command runs in full, the
  whole output is stored under its number, and your cut is applied to it and shown before the one line naming the
  number, so the lines you asked for come back and the rest stays readable.
- An alias names a command line of the project: `journal alias add <name> "<line>" [--reader <name>] [--about "<what
  it does>"] [--env KEY=VALUE]`, then `journal <name> [args]` runs the line with the args at its end, recorded as your
  own command. A run that moves to the background is watched at once through the alias's reader, so the user sees it
  progress. `journal alias list` names them, `journal alias edit <name> [--line] [--reader] [--about]` changes one and
  `journal alias remove <name>` removes it; a name that is a journal command or an alias already is refused. The
  user types the same `journal <name>` in a terminal, and a plugin may ship aliases with their readers. An alias chains
  with other commands like any command. A line an alias runs, typed by hand, refuses the whole tool use with the alias,
  and so does an alias run whose line a more specific alias runs; a reader of the project never reads a plugin's alias,
  and one that would is deleted when the alias runs. A line you run three times or more with no alias for it is asked
  once to become one, with the reader that reads it.
- A test suite is a long runner: run it on its own and chain the commit after its result in a second call.
- A journal command runs on its own, or chained only with other journal commands; chained with anything else it is
  refused, since it would move to the background with the rest and its answer would be lost. A journal command stays in
  the foreground, but for the few that name themselves background commands, such as `journal worker merge`, which go to
  the background at once with their card and their own reader, streaming their lines as they print them.
- While the journal waits to restart until the commands running now end, a command that would go to the background at
  once (a merge, a test run, a build) is refused, since the restart would cut it off: run it again once the journal is back.
""", keywords=("background", "long-running", "alias"), commands=('output', 'reader', 'alias'), events=(ReaderReportRaised,))
