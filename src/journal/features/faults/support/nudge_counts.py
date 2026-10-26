from datetime import datetime, timezone

from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.support.time_source import TimeSource


class NudgeCounts:
    """What the Developer tab shows of the nudges that fired: per agent, each nudge with how often it fired and when it last did, since the counts were last reset."""

    def __init__(self, entries: Entries, agents: Agents, time_source: TimeSource) -> None:
        self.entries, self.agents, self.time_source = entries, agents, time_source
        self.reset_at = datetime.fromtimestamp(0, timezone.utc)

    def rows(self) -> list[dict]:
        sessions: dict[str, list[dict]] = {}
        for tally in sorted(self.entries.nudge_tallies(self.reset_at), key=lambda tally: -tally.count):
            sessions.setdefault(tally.session, []).append({"key": tally.key, "count": tally.count, "last_at": tally.last_at})
        return [{"session": session, "agent": self.agent_name(session), "nudges": nudges} for session, nudges in sessions.items()]

    def agent_name(self, session: str) -> str:
        agents = self.agents.global_matching(session=session)
        return f"{agents[0].role} agent {agents[0].id}" if agents else f"session {session[:8]}"

    def reset(self) -> None:
        self.reset_at = self.time_source.moment()
