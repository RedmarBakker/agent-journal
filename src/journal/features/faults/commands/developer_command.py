import sys
from argparse import Namespace
from datetime import datetime

from journal.console.command import Command
from journal.features.client_errors.support.client_error_store import ClientErrorStore
from journal.features.faults.support.developer_numbers import DeveloperNumbers
from journal.features.faults.support.scenario_transitions import ScenarioTransitions
from journal.features.faults.support.thread_sampler import ThreadSampler
from journal.http.journal.answer_time import AnswerTime
from journal.models.timing import Timing
from journal.repositories.query_plans import QueryPlans
from journal.support.caller import Caller
from journal.support.large_reads import LargeReads
from journal.support.query_times import QueryTimes

TOP = 10
PROFILE_SECONDS = 20.0
PROFILE_LIMIT_SECONDS = 25.0
PROFILE_LINES = 30


class DeveloperCommand(Command):
    """journal developer: how fast the journal answers and what each request reads, from the same numbers the Developer tab shows."""

    noun = "developer"

    def __init__(self, numbers: DeveloperNumbers, sampler: ThreadSampler, queries: QueryTimes, plans: QueryPlans, large_reads: LargeReads, client_errors: ClientErrorStore, transitions: ScenarioTransitions) -> None:
        self.viewer_errors, self.transition_kinds = client_errors, transitions
        self.numbers, self.sampler, self.statements, self.plans, self.large_reads = numbers, sampler, queries, plans, large_reads

    def arguments(self, verbs) -> None:
        slowest = self.verb(verbs, "slowest", "the routes of the rolling log grouped, the slowest group first, a page at a time: each with its worst and typical time and how many were logged")
        slowest.add_argument("--page", type=int, default=1, help="which page of groups, from 1")
        inspect = self.verb(verbs, "inspect", "one group of journal developer slowest: its logged requests, the slowest first, with when, how long and what each read")
        inspect.add_argument("group", help="the group as slowest names it, such as 'GET /journal/messages'")
        inspect.add_argument("--page", type=int, default=1, help="which page of its requests, from 1")
        self.verb(verbs, "loads", "the newest requests with the records each read, by kind, while load counting is on")
        self.verb(verbs, "models", "the records read per kind since the last reset")
        self.verb(verbs, "averages", "the average and slowest time of hooks, requests, each kind of hook and, while stage timing is on, each stage of a hook")
        queries = self.verb(verbs, "queries", "the SQL statements that took the most time since the last reset, each with its runs and times and the steps of its query plan that read a whole table or sort")
        queries.add_argument("--count", type=int, default=TOP, help="how many statements")
        reads = self.verb(verbs, "reads", "the reads of more rows than a page since the last reset, the largest first, each with the code that asked: a page read asking more was cut to a page")
        reads.add_argument("--count", type=int, default=TOP, help="how many reads")
        errors = self.verb(verbs, "client-errors", "the console errors the viewer posted, each with its stack and how many times it came, until they are cleared")
        errors.set_defaults(verb="client_errors")
        errors.add_argument("--clear", action="store_true", help="empty the list, which ends the reminders")
        transitions = self.verb(verbs, "transitions", "each kind of change of an agent's stack counted here, the top state before, the top state after and its cause, the rarest first, marked when no scenario story walks it")
        transitions.add_argument("--hours", type=float, default=0.0, help="only the kinds seen in the last this many hours; 0 for every kind")
        self.verb(verbs, "reset", "clear the times, the rolling log and the counts")
        profile = self.verb(verbs, "profile", "watch every thread of the server for a while and print where its time goes, the busiest functions first")
        profile.add_argument("seconds", type=float, nargs="?", default=PROFILE_SECONDS, help=f"how long to watch, at most {PROFILE_LIMIT_SECONDS:.0f} seconds")

    def slowest(self, args: Namespace, caller: Caller) -> int:
        groups = self.numbers.groups()
        self.print_lines([group.line() for group in self.paged(groups, args.page)], "nothing logged yet")
        self.print_lines([self.pages_line(len(groups), args.page, "journal developer slowest", "journal developer inspect '<group>' for one group's requests")], "")
        return 0

    def inspect(self, args: Namespace, caller: Caller) -> int:
        group = next((candidate for candidate in self.numbers.groups() if candidate.name == args.group), None)
        if group is None:
            print(f"no group {args.group} in the rolling log: journal developer slowest names them", file=sys.stderr)
            return 1
        self.print_lines([f"{self.clock(t)}  {t.ms:>6} ms  {t.route}  {t.loads.line()}" for t in self.paged(list(group.timings), args.page)], "")
        self.print_lines([self.pages_line(len(group.timings), args.page, f"journal developer inspect '{args.group}'", group.line())], "")
        return 0

    @staticmethod
    def paged(items: list, page: int) -> list:
        return items[(page - 1) * TOP : page * TOP]

    @staticmethod
    def pages_line(count: int, page: int, command: str, footer: str) -> str:
        pages = max(1, -(-count // TOP))
        next_page = f"; {command} --page {page + 1} for the next" if page < pages else ""
        return f"page {page} of {pages}{next_page}. {footer}"

    def loads(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([f"{self.clock(t)}  {t.load_line()}" for t in self.numbers.loaded()], "nothing counted: turn on faults.count_loads in the Developer tab")
        return 0

    def models(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([f"{total.rows:>8}  {total.model}" for total in self.numbers.model_totals()], "nothing counted yet")
        return 0

    def averages(self, args: Namespace, caller: Caller) -> int:
        rows = {"hooks": self.numbers.hook_time(), "requests": self.numbers.request_time(), **{f"hook {type_name}": time for type_name, time in self.numbers.hook_averages().items()}, **{f"stage {stage}": time for stage, time in self.numbers.stage_averages().items()}}
        self.print_lines([self.average_line(name, time) for name, time in rows.items() if time.count], "nothing measured yet")
        return 0

    def profile(self, args: Namespace, caller: Caller) -> int:
        sample = self.sampler.sampled(min(args.seconds, PROFILE_LIMIT_SECONDS))
        print(f"{sample.sample_count} looks at every thread, and the share of them each place was seen working.")
        print("\nWhere each working thread was:")
        self.print_lines(self.shares(sample.busy_functions, sample.sample_count), "every thread was waiting")
        print("\nOn a working stack, with what it calls:")
        self.print_lines(self.shares(sample.stack_functions, sample.sample_count), "every thread was waiting")
        return 0

    @staticmethod
    def shares(places, sample_count: int) -> list[str]:
        return [f"{100 * count / sample_count:5.1f}%  {place}" for place, count in places.most_common(PROFILE_LINES)]

    def queries(self, args: Namespace, caller: Caller) -> int:
        for query in self.statements.slowest(args.count):
            print(query.line())
            for step in QueryPlans.slow_steps(self.plans.steps(query)):
                print(f"    {step}")
        return 0

    def reads(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([read.line() for read in self.large_reads.largest(args.count)], "no read of more rows than a page since the last reset")
        return 0

    def client_errors(self, args: Namespace, caller: Caller) -> int:
        if args.clear:
            self.viewer_errors.clear()
            print("the viewer's console errors are cleared")
            return 0
        self.print_lines([error.line() for error in self.viewer_errors.all()], "the viewer logged no console errors")
        return 0

    def transitions(self, args: Namespace, caller: Caller) -> int:
        self.print_lines(self.transition_kinds.lines(args.hours), "no stack change counted yet")
        self.print_lines([self.transition_kinds.footer()], "")
        return 0

    def reset(self, args: Namespace, caller: Caller) -> int:
        self.numbers.reset()
        self.statements.clear()
        self.large_reads.clear()
        print("the times, the rolling log and the counts are cleared")
        return 0

    @staticmethod
    def average_line(name: str, time: AnswerTime) -> str:
        return f"{name:<44} {time.count:>6} measured  {time.average_ms():>5} ms average  {time.slowest_ms:>5} ms slowest"

    @staticmethod
    def clock(timing: Timing) -> str:
        return datetime.fromtimestamp(timing.time).strftime("%H:%M:%S")

    @staticmethod
    def print_lines(lines: list[str], empty: str) -> None:
        print("\n".join(lines) if lines else empty)
