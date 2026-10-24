from journal.engine.demand import Demand
from journal.events.feature_data import FeatureData
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.shell_part import ShellPart
from journal.models.reader_report import ReaderReport
from journal.support.timeout import Timeout


def unwatched(data: FeatureData) -> tuple[str, ...] | None:
    return data.part(ShellPart).unwatched_commands or None


def unread_reports(data: FeatureData) -> tuple[int, ...] | None:
    return data.part(ShellPart).unread_reports or None


def unfixed_reports(data: FeatureData) -> tuple[int, ...] | None:
    return data.part(ShellPart).unfixed_reports or None


def refuted_reports(data: FeatureData) -> tuple[ReaderReport, ...] | None:
    return data.part(ShellPart).refuted_reports or None


class ShellDemands:
    """What the shell feature demands of the agent: a command run in the background that no reader reads is given a reader, with a label that names what it does; a reader report is read; a report read is acted on, the reader written anew or the report dismissed; each before its span runs out, its writes then refused; and a report whose dismissal the verifier refuted holds every write at once, with the verdict, until its reader is written anew."""

    REPORT_REFUTED = Demand(
        key="shell.reader_report_refuted",
        requirement=refuted_reports,
        line=lambda reports, balance: ShellNudges.REPORT_REFUTED.create(verdicts=ShellNudges.report_refutations(reports)),
        refusal=lambda reports: ShellNudges.REPORT_REFUTED_REFUSAL.create(verdicts=ShellNudges.report_refutations(reports)),
        exemption=lambda event, reports: False,
        span=lambda settings: Timeout.tool_uses(0),
        block_scope=lambda event: bool(event.call.writes),
    )

    READER = Demand(
        key="shell.reader",
        requirement=unwatched,
        line=lambda commands, balance: ShellNudges.reader_countdown(commands, balance),
        refusal=lambda commands: ShellNudges.READER_REFUSAL.create(commands=", ".join(commands)),
        exemption=lambda event, commands: False,
        span=lambda settings: Timeout.tool_uses(settings.integer(ShellOptions.READER_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
    )
    REPORT_READ = Demand(
        key="shell.reader_report_read",
        requirement=unread_reports,
        line=lambda reports, balance: ShellNudges.report_read_countdown(reports, balance),
        refusal=lambda reports: ShellNudges.REPORT_READ_REFUSAL.create(reports=", ".join(map(str, reports))),
        exemption=lambda event, reports: False,
        span=lambda settings: Timeout.tool_uses(settings.integer(ShellOptions.REPORT_READ_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
    )
    REPORT_FIX = Demand(
        key="shell.reader_report_fix",
        requirement=unfixed_reports,
        line=lambda reports, balance: ShellNudges.report_fix_countdown(reports, balance),
        refusal=lambda reports: ShellNudges.REPORT_FIX_REFUSAL.create(reports=", ".join(map(str, reports))),
        exemption=lambda event, reports: False,
        span=lambda settings: Timeout.tool_uses(settings.integer(ShellOptions.REPORT_FIX_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
    )
