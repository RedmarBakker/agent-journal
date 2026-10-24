from journal.engine.demand import Demand
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.messages.messages_part import MessagesPart
from journal.features.messages.support.message_requirement import MessageRequirement
from journal.support.timeout import Timeout


def unanswered(data: FeatureData) -> MessageRequirement | None:
    messages = data.part(MessagesPart)
    return MessageRequirement(messages.unanswered, messages.unanswered_files) if messages.unanswered else None


def unread(data: FeatureData) -> MessageRequirement | None:
    messages = data.part(MessagesPart)
    return MessageRequirement(messages.unread) if messages.unread else None


def answer_exemption(event: ToolStarting, requirement: MessageRequirement) -> bool:
    return event.call.is_journal or any(path.startswith(folder) for path in event.call.read_paths for folder in requirement.folders)


class MessagesDemands:
    """What the messages feature demands of the agent: a message read is answered before its span runs out, every tool but journal commands and reads of the message's files then refused; an unread message is read before its span runs out, its writes then refused."""

    REPLY = Demand(
        key="messages.reply",
        requirement=unanswered,
        line=lambda requirement, balance: MessagesNudges.unanswered_countdown(requirement.numbers, balance),
        refusal=lambda requirement: MessagesNudges.UNANSWERED_TOOL_BLOCK.create(messages=requirement.listing()),
        exemption=answer_exemption,
        span=lambda settings: Timeout.tool_uses(settings.integer(MessagesOptions.TOOL_BLOCK_LIMIT)),
        block_scope=lambda event: True,
        silence=lambda settings: Timeout.tool_uses(settings.integer(MessagesOptions.ANSWER_REQUEST_LIMIT)),
    )
    READ = Demand(
        key="messages.read",
        requirement=unread,
        line=lambda requirement, balance: MessagesNudges.inbox_countdown(requirement.numbers, balance),
        refusal=lambda requirement: MessagesNudges.INBOX_EDIT_BLOCK.create(count=len(requirement.numbers)),
        exemption=lambda event, requirement: event.call.is_journal,
        span=lambda settings: Timeout.tool_uses(settings.integer(MessagesOptions.EDIT_BLOCK_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
    )
