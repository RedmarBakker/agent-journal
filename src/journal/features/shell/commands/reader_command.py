import shlex
from datetime import datetime, timezone
import re
from argparse import Namespace
from pathlib import Path

from journal.engine.clock import Clock
from journal.repositories.reader_reports import ReaderReports
from journal.events.announcer import Announcer
from journal.events.moments.reader_added import ReaderAdded
from journal.repositories.aliases import Aliases
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.run_history import RunHistory
from journal.features.shell.support.command_mark_policy import CommandMarkPolicy
from journal.features.shell.support.activity_title import TITLE_RULE, ActivityTitle
from journal.console.command import Command
from journal.support.caller import Caller
from journal.support.command_shape import CommandShape
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_judge import ReaderJudge
from journal.features.shell.support.reader_probes import ReaderProbes
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.reader_backfill import ReaderBackfill
from journal.repositories.scope import Scope
from journal.support.rejection import Rejection

NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
# the newest stored runs a reader being added is tried on before it is accepted
QUICK_RUNS = 2

class ReaderCommand(Command):
    """The project's output readers: add one for a shape of output read again and again, list them, and remove one."""

    noun = "reader"

    def __init__(self, readers: Readers, outputs: CommandOutputs, announcer: Announcer, reports: ReaderReports, clock: Clock, judge: ReaderJudge, aliases: Aliases, backfill: ReaderBackfill, scope: Scope, history: RunHistory) -> None:
        self.backfill, self.scope, self.history = backfill, scope, history
        self.readers, self.outputs, self.announcer, self.reports, self.clock, self.judge = readers, outputs, announcer, reports, clock, judge
        self.aliases = aliases

    def arguments(self, verbs) -> None:
        addition = self.verb(verbs, "add", "a reader kept in .journal/readers/: the lines a pattern matches, or what a script handed the output prints; writing an existing one anew keeps each setting a flag leaves out, and an empty value takes one away")
        addition.add_argument("name")
        source = addition.add_mutually_exclusive_group()
        source.add_argument("--pattern", help="the lines it picks; a new reader needs this or --script, an existing one keeps its own")
        source.add_argument("--script", type=Path, help="a shell script given the output on its input")
        addition.add_argument("--about", help="what it picks, in a few words; a new reader needs it")
        addition.add_argument("--progress", help="a pattern whose last match says how far the command has come: one group for a percentage, two for a count of a total")
        addition.add_argument("--topic", help="a pattern read over the command line whose matches say what a run is about, after the card's title: the test files a line names, or its -k, such as '(\\S+\\.py)'")
        addition.add_argument("--label", help=f"the card's title and the words before its progress: {TITLE_RULE}")
        addition.add_argument("--step", help="a pattern for one step, such as a test's dot, that moves the progress between two of its counts")
        addition.add_argument("--finished", help="a pattern for the lines it picks once the command finished, such as its summary; the pattern picks them while it runs")
        addition.add_argument("--failed", help="a pattern for the lines it picks once the command failed, such as its failures; the pattern picks them while it runs")
        addition.add_argument("--summary", help="a pattern whose last match in the output is the summary its card shows once opened, a few words such as '(\\d+ failed), (\\d+ passed)': its groups are joined, or the whole match without any")
        addition.add_argument("--commands", help="the commands whose output it reads, comma-separated, such as pytest or dotnet test: a command moved to the background that runs one is told to watch it with this reader")
        self.verb(verbs, "list", "the project's readers, each with what it picks")
        self.verb(verbs, "remove", "take a reader away, with its files; an alias it read for runs with no reader, and a reader a plugin ships goes only with its plugin").add_argument("name")
        self.verb(verbs, "default", "make a reader the one that reads its commands, over every other reader of them").add_argument("name")
        self.verb(verbs, "report", "read a reader report: what the reader judge found a reader showed poorly, and how to fix it").add_argument("n", type=int)
        dismissal = self.verb(verbs, "dismiss", "set a reader report aside as wrong, saying why; the reason is kept for the user")
        dismissal.add_argument("n", type=int)
        dismissal.add_argument("--why", required=True, help="why the report is wrong")

    # the options a reader written again keeps from the one before because the line left them out, each with the value it keeps
    @staticmethod
    def kept_options(prior: Reader, args: Namespace) -> list[str]:
        options = {"progress": prior.progress_pattern, "label": prior.label, "commands": prior.commands.text(), "step": prior.step_pattern, "topic": prior.topic_pattern, "finished": prior.finished_pattern, "failed": prior.failed_pattern, "summary": prior.summary_pattern}
        return [f"--{option} {shlex.quote(value)}" for option, value in options.items() if value and getattr(args, option) is None]

    def add(self, args: Namespace, caller: Caller) -> int:
        if not NAME.fullmatch(args.name):
            raise Rejection(f"a reader's name is lowercase words joined by -, such as failed-tests, not {args.name}")
        self.readers.refuse_locked(args.name, "replaced")
        prior = self.readers.stored_reader(args.name)
        if prior is None and not (args.pattern or args.script):
            raise Rejection("a new reader says what it picks with --pattern or --script")
        if prior is not None and prior.script and not args.script and args.pattern is None:
            raise Rejection(f"the reader {args.name} is a script: change it with --script, or write it as a pattern with --pattern")
        if prior is None and not args.about:
            raise Rejection("a new reader says what it picks with --about")
        unread_commands = [command.strip() for command in (args.commands or "").split(",") if CommandMarkPolicy.takes_no_reader(command.strip())]
        if unread_commands:
            raise Rejection(f"{', '.join(unread_commands)} gets no reader: a search, a read and a git or GitHub command show no card in the chat")
        reader = (prior or Reader(args.name, args.about)).revised(subject=args.about, progress_pattern=args.progress, label=None if args.label is None else ActivityTitle.checked(args.label), commands=None if args.commands is None else ReaderCommands.parsed(args.commands), step_pattern=args.step, topic_pattern=args.topic, finished_pattern=args.finished, failed_pattern=args.failed, summary_pattern=args.summary)
        self.readers.refuse_plugin_alias_reader(reader)
        for pattern in (args.pattern or "", reader.progress_pattern, reader.finished_pattern, reader.failed_pattern, reader.summary_pattern):
            re.compile(pattern)
        if args.script:
            self.readers.add_script(reader.revised(pattern=""), args.script.read_text())
        else:
            revised = reader.revised(pattern=args.pattern)
            self.tried(revised)
            self.readers.add(revised)
            self.backfill.queue_trial(revised, QUICK_RUNS, self.scope.id)
        self.announcer.announce(ReaderAdded(reader=args.name))
        print(f"reader {args.name} added: journal output read N --reader {args.name}")
        kept = self.kept_options(prior, args) if prior is not None else []
        if kept:
            print(f"kept from the reader before, as you did not give them: {', '.join(kept)}; give one as '' to drop it, such as --progress ''")
        return 0

    def tried(self, reader: Reader) -> None:
        self.probed(reader)
        for run in [run for run in self.judge.stored_runs(reader) if run.ended][:QUICK_RUNS]:
            misses = self.judge.misses(reader, self.judge.read_lines(reader, OutputFiles(Path(run.folder))))
            if misses:
                raise Rejection(f"reader {reader.name} is refused, tried on output {run.id}: {'; '.join(misses)}")

    @staticmethod
    def probed(reader: Reader) -> None:
        unfiltered = ReaderProbes.unfiltered_patterns(reader)
        if unfiltered:
            raise Rejection(f"reader {reader.name} is refused: its {' and '.join(unfiltered)} selects every line of any run, so it filters nothing and its card shows the raw output; give it a pattern for the few lines a person reads, such as the failures, the progress and the summary")
        misses = ReaderProbes.test_run_misses(reader)
        if misses:
            raise Rejection(f"reader {reader.name} is refused: {'; '.join(misses)}")

    def report(self, args: Namespace, caller: Caller) -> int:
        report = self.reports.save(self.reports.find(args.n).opened(datetime.fromtimestamp(self.clock.time(), timezone.utc)), caller.actor)
        print(report.full_text())
        return 0

    def dismiss(self, args: Namespace, caller: Caller) -> int:
        target_report = self.reports.find(args.n)
        findings = self.judge.run_findings(target_report)
        if findings:
            raise Rejection(f"reader report {target_report.id} is borne out by the run's own output and cannot be dismissed: write the reader anew with journal reader add {target_report.reader} ...: {'; '.join(findings)}")
        repeated_report = self.judge.unjudged_dismissal(target_report, datetime.fromtimestamp(self.clock.time(), timezone.utc))
        if repeated_report is not None:
            raise Rejection(f"reader report {target_report.id} is refused a dismissal: report {repeated_report.id} found the same for {CommandShape.command_name(repeated_report.command)} and was dismissed, and its verifier has not judged that dismissal sound, so the cause is still there: fix it, in the reader with journal reader add {target_report.reader} ..., in the command, or in the reader chosen for it")
        report = self.reports.save(target_report.dismissed(args.why), caller.actor)
        print(f"reader report {report.id} dismissed: {args.why}")
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        unfinished = [output.id for output in self.history.reader_unended(args.name)]
        self.readers.removed(args.name)
        aliases = self.aliases.reader_rows(args.name)
        for alias in aliases:
            self.aliases.save(alias.with_(reader=""), caller.actor)
        print(f"reader {args.name} removed" + (f"; journal {', journal '.join(alias.name for alias in aliases)} now run with no reader" if aliases else "") + (f"; outputs {', '.join(map(str, unfinished))} were read through it and now show their last lines" if unfinished else ""))
        return 0

    def default(self, args: Namespace, caller: Caller) -> int:
        replaced_readers = self.readers.default_choice(args.name)
        print(f"reader {args.name} reads its commands" + (f", over {', '.join(replaced_readers)}" if replaced_readers else ""))
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        readers = self.readers.all()
        if not readers:
            print("no reader is kept: journal reader add <name> keeps one")
        defaults = self.readers.default_names()
        for reader in readers:
            print(f"{reader.name}: {reader.subject}" + (" (locked)" if self.readers.is_locked(reader.name) else "") + (" (the default for its commands)" if reader.name in defaults else ""))
        return 0
