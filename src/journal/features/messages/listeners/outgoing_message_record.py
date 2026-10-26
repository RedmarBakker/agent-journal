from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.models.message import Message
from journal.repositories.messages import Messages
from journal.repositories.subagents import Subagents
from journal.support.peer_name import PeerName
from journal.features.workers.support.subagent_entries import SubagentEntries
from journal.support.agent_message import AgentMessage
from journal.support.voice_key import VoiceKey


class OutgoingMessageRecord(AgentListener[ToolFinished]):
    """A message the agent sent to another agent with Claude Code's own tool reaches the chat, named as sent to that agent, by its job when it is a subagent of the sender, by its project's name when its address is a socket, or as failed with the tool's reason when the send did not arrive; one that only asks to be notified when the other is idle shows nothing and is left out; its hook's key keeps a hook sent again from recording it twice."""

    def __init__(self, messages: Messages, names: PeerName, subagents: Subagents) -> None:
        self.messages, self.names, self.subagents = messages, names, subagents

    def handle(self, event: ToolFinished) -> None:
        message = event.call.operation
        if not isinstance(message, AgentMessage) or not message.text.strip():
            return
        receiver, text, key = message.receiver, message.text.strip(), VoiceKey.hooked("sent", event.hook_key)
        answer = SubagentEntries.answered(event.response or event.output)
        if answer.get("success") is False:
            self.messages.recorded(Message.send_failed(self.receiver_name(event.session, receiver), text, event.session, receiver, str(answer.get("message", "the send failed"))).with_(idempotency=key), Actor.agent(event.session))
            return
        self.messages.recorded(Message.outgoing(self.receiver_name(event.session, receiver), text, event.session, receiver).with_(idempotency=key), Actor.agent(event.session))

    def receiver_name(self, session: str, receiver: str) -> str:
        subagent = self.subagents.session_subagent(session, receiver)
        return subagent[0].task if subagent and subagent[0].task else self.names.resolve(receiver)
