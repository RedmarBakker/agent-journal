from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.subagent_chat import SubagentChat
from journal.repositories.subagents import Subagents
from journal.support.actor import Actor
from journal.support.agent_message import AgentMessage
from journal.support.voice_key import VoiceKey


class SubagentMessageRecord(AgentListener[ToolStarting]):
    """A message an agent sends one of its subagents after it started is a message to it in its chat."""


    def __init__(self, chat: SubagentChat, subagents: Subagents) -> None:
        self.chat, self.subagents = chat, subagents

    def handle(self, event: ToolStarting) -> None:
        operation = event.call.operation
        if not isinstance(operation, AgentMessage):
            return
        for subagent in self.subagents.session_subagent(event.session, operation.receiver):
            self.chat.instruction(subagent, operation.text, VoiceKey.hooked("instruction", event.hook_key), Actor.agent(event.session))
