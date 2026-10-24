from dataclasses import dataclass
from typing import Callable

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.support.timeout import Timeout


@dataclass(frozen=True)
class Demand:
    """Something the agent must do for the journal, declared once by its feature: its requirement read from the feature data, none once it is met; the line said at each tool use with the balance of uses left; the span from its start before the agent is put into a DemandBlock, whose refusal stops every tool in its block scope; the tools exempt from it; and the span of silence before its line is first said."""

    key: str
    requirement: Callable[[FeatureData], object | None]
    line: Callable[[object, int], Nudge]
    refusal: Callable[[object], Nudge]
    exemption: Callable[[ToolStarting, object], bool]
    span: Callable[[Settings], Timeout]
    block_scope: Callable[[ToolStarting], bool]
    silence: Callable[[Settings], Timeout] | None = None
