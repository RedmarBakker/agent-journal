from typing import TypedDict


class TerminalLine(TypedDict):
    """One part of a shell command the agent ran, as the terminal pane shows it, with the journal's reason when it refused the command before it ran."""

    agent_id: int
    time: float
    tool: str
    command: str
    output: str
    seconds: float
    status: int
    stepped: bool
    level: str
    refused: str
