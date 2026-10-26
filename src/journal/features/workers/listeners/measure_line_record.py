from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.measure_lines import MeasureLines
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class MeasureLineRecord(AgentListener[LineDelivered]):
    """When a measure's line was sent is kept on its state on the agent's row, for the page to show."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: LineDelivered) -> None:
        key, rows = MeasureLines.measure_key(event.nudge), self.agents.session_rows(event.session)
        if key and rows:
            self.agents.rewritten(rows[0], Actor.system(), lambda current: current.measure_line_sent(key, event.time))
