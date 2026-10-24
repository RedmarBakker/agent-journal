from journal.engine.demand import Demand
from journal.events.feature_data import FeatureData
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.shell_part import ShellPart
from journal.support.timeout import Timeout


def unwatched(data: FeatureData) -> tuple[str, ...] | None:
    return data.part(ShellPart).unwatched_commands or None


class ShellDemands:
    """What the shell feature demands of the agent: a command run in the background that no reader reads is given a reader, with a label that names what it does, before its span runs out; its writes are then refused."""

    READER = Demand(
        key="shell.reader",
        requirement=unwatched,
        line=lambda commands, balance: ShellNudges.reader_countdown(commands, balance),
        refusal=lambda commands: ShellNudges.READER_REFUSAL.create(commands=", ".join(commands)),
        exemption=lambda event, commands: False,
        span=lambda settings: Timeout.tool_uses(settings.integer(ShellOptions.READER_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
    )
