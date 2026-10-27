from dataclasses import dataclass


@dataclass(frozen=True)
class BriefingData:
    """The briefing feature's reading: whether the agent has run journal environment overview since its session started or its context was compacted, and what the start block names: the environment, when another session worked here lately, the rules, facts and reminders numbered, and what waits, the Team chat's latest messages, the background runs the journal's last restart cut off, and the folder the environment's agent was launched in and whether it is gone."""

    is_overview_read: bool
    environment: str
    peer_session_active_at: str
    rules: str
    rules_count: int
    memories: str
    reminders: str
    waiting: str
    team_history: str
    interrupted_runs: str = ""
    launch_folder: str = ""
    is_launch_folder_missing: bool = False
