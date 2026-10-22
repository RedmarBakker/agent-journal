from journal.events.agent.session_started import SessionStarted
from journal.features.messages.listeners.inbox_notice import InboxNotice


class StartInboxDelivery(InboxNotice[SessionStarted]):
    """A session that starts is given the messages still unread, by number: delivery, since the agent may have missed the line typed when the message arrived."""
