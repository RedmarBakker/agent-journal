from argparse import Namespace
from datetime import datetime

from journal.console.command import Command
from journal.features.faults.support.developer_numbers import DeveloperNumbers
from journal.features.faults.support.thread_sampler import ThreadSampler
from journal.http.journal.answer_time import AnswerTime
from journal.models.timing import Timing
from journal.support.caller import Caller

TOP = 10
PROFILE_SECONDS = 20.0
PROFILE_LIMIT_SECONDS = 25.0
PROFILE_LINES = 30


class DeveloperCommand(Command):
    """journal developer: how fast the journal answers and what each request reads, from the same numbers the Developer tab shows."""

    noun = "developer"

    def __init__(self, numbers: DeveloperNumbers, sampler: ThreadSampler) -> None:
        self.numbers, self.sampler = numbers, sampler

    def arguments(self, verbs) -> None:
        slowest = self.verb(verbs, "slowest", "the slowest requests and hooks of the rolling log, with their path, kind and milliseconds")
        kinds = slowest.add_mutually_exclusive_group()
        kinds.add_argument("--hooks", action="store_true", help="hooks only")
        kinds.add_argument("--requests", action="store_true", help="requests only")
        slowest.add_argument("--top", type=int, default=TOP, help="how many, the slowest first")
        self.verb(verbs, "loads", "the newest requests with the records each read, by kind, while load counting is on")
        self.verb(verbs, "models", "the records read per kind since the last reset")
        self.verb(verbs, "averages", "the average and slowest time of hooks, requests and each kind of hook")
        self.verb(verbs, "reset", "clear the times, the rolling log and the counts")
        profile = self.verb(verbs, "profile", "watch every thread of the server for a while and print where its time goes, the busiest functions first")
        profile.add_argument("seconds", type=float, nargs="?", default=PROFILE_SECONDS, help=f"how long to watch, at most {PROFILE_LIMIT_SECONDS:.0f} seconds")

    def slowest(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([f"{t.ms:>6} ms  {t.method:<5} {t.route}" for t in self.slowest_kind(args)], "nothing logged yet")
        return 0

    def slowest_kind(self, args: Namespace) -> list[Timing]:
        if args.hooks:
            return self.numbers.slowest_hooks(args.top)
        if args.requests:
            return self.numbers.slowest_requests(args.top)
        return self.numbers.slowest(args.top)

    def loads(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([f"{self.clock(t)}  {t.load_line()}" for t in self.numbers.loaded()], "nothing counted: turn on faults.count_loads in the Developer tab")
        return 0

    def models(self, args: Namespace, caller: Caller) -> int:
        self.print_lines([f"{total.rows:>8}  {total.model}" for total in self.numbers.model_totals()], "nothing counted yet")
        return 0

    def averages(self, args: Namespace, caller: Caller) -> int:
        rows = {"hooks": self.numbers.hook_time(), "requests": self.numbers.request_time(), **{f"hook {kind}": time for kind, time in self.numbers.hook_averages().items()}}
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

    def reset(self, args: Namespace, caller: Caller) -> int:
        self.numbers.reset(caller.actor)
        print("the times, the rolling log and the counts are cleared")
        return 0

    @staticmethod
    def average_line(name: str, time: AnswerTime) -> str:
        return f"{name:<28} {time.count:>6} measured  {time.average_ms():>5} ms average  {time.slowest_ms:>5} ms slowest"

    @staticmethod
    def clock(timing: Timing) -> str:
        return datetime.fromtimestamp(timing.time).strftime("%H:%M:%S")

    @staticmethod
    def print_lines(lines: list[str], empty: str) -> None:
        print("\n".join(lines) if lines else empty)
