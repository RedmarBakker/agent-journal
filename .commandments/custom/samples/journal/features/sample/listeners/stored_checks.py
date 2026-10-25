from journal.events.agent.peer_message import PeerMessage
from journal.events.agent_listener import AgentListener
from journal.models.link import Link
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.support.voice_key import VoiceKey


# @sin StoredCheckOutsideFunnelDetector
def thoughts_by_seen_texts(messages, thoughts: list[str], actor) -> None:
    stored = {m.text for m in messages.thoughts("s1")}
    for thought in thoughts:
        if thought not in stored:
            messages.save(Message(text=thought), actor)


# @sin StoredCheckOutsideFunnelDetector
def reply_by_text_comparison(messages, n: int, text: str, actor) -> None:
    if any(m.text == text for m in messages.replies(n)):
        return
    messages.save(Message(text=text, reply_target=n), actor)


# @sin StoredCheckOutsideFunnelDetector
def peer_by_field_filter(messages, sender: str, text: str, actor) -> None:
    if [m for m in messages.recent(30) if m.data.get("sender") == sender and m.text == text]:
        return
    messages.save(Message.outgoing(sender, text, "s1"), actor)


# @righteous StoredCheckOutsideFunnelDetector
def thought_by_key(messages, thought: str, key: str, actor) -> None:
    messages.recorded(Message(text=thought, idempotency=key), actor)


# @righteous StoredCheckOutsideFunnelDetector
def turn_by_key(messages, text: str, key: str, actor) -> None:
    if messages.sent_with(key):
        return
    messages.save(Message(text=text, idempotency=key), actor)


# @righteous StoredCheckOutsideFunnelDetector
def answers_in_order(messages, answered: list[int], text: str, actor) -> None:
    for n in answered:
        if n in answered[1:]:
            messages.read(n, actor)


# @sin StoredCheckOutsideFunnelDetector
def subject_link_by_seen_targets(links, message, task, actor) -> None:
    if Ref.build(task) not in links.targets(message, "subject"):
        links.save(Link(source=Ref.build(message), target=Ref.build(task), kind="subject"), actor)


# @righteous StoredCheckOutsideFunnelDetector
def subject_link_through_funnel(links, message, task, actor) -> None:
    links.linked(Ref.build(message), Ref.build(task), "subject", actor)


# @righteous StoredCheckOutsideFunnelDetector
def question_by_its_words(messages, text: str, key: str, actor) -> None:
    asks = "?" not in text
    messages.recorded(Message(text=text, idempotency=key, data={"asks": asks}), actor)


class PeerRecord(AgentListener[PeerMessage]):
    def handle(self, event: PeerMessage) -> None:
        self.unkeyed(event)
        self.keyed(event)

    # @sin StoredCheckOutsideFunnelDetector
    def unkeyed(self, event: PeerMessage) -> None:
        self.messages.save(Message.agent_message(event.sender, event.text, event.session, event.time, False), event.actor)

    # @righteous StoredCheckOutsideFunnelDetector
    def keyed(self, event: PeerMessage) -> None:
        self.messages.recorded(Message.agent_message(event.sender, event.text, event.session, event.time, False).with_(idempotency=VoiceKey.hooked("peer", event.hook_key)), event.actor)
