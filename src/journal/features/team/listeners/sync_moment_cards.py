from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.edit_dropped import EditDropped
from journal.events.moments.edit_overridden import EditOverridden
from journal.events.moments.sync_moment import SyncMoment
from journal.events.moments.team_chat_claimed import TeamChatClaimed
from journal.events.moments.team_chat_files_diverged import TeamChatFilesDiverged
from journal.support.actor import Actor
from journal.support.card_kind import CardKind

DETAIL_CHARACTERS = 120


class SyncMomentCards(Listener[SyncMoment]):
    """What the team sync did or found that the user should see is one mark in the chat: the Team chat claimed while its holder was offline, its files on this machine kept apart, an edit kept over this machine's, a row deleted by a colleague."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SyncMoment) -> None:
        if isinstance(event, TeamChatClaimed):
            self.cards.show(event.environment_id, None, f"{event.holder} claimed the Team chat while {event.former} was offline: what {event.former} had not pushed stayed on their machine", "warn", actor=Actor.system(), shows=CardKind.WORKTREES)
        if isinstance(event, TeamChatFilesDiverged):
            label = f"The Team chat's files on {event.device} have changes of their own, so they stay at {event.local[:8]} and not at the holder's {event.tip[:8]}"
            self.cards.show(event.environment_id, None, label, "warn", key=f"team-chat-files:{event.device}", actor=Actor.system(), shows=CardKind.WORKTREES)
        if isinstance(event, EditOverridden):
            self.cards.show(event.environment_id, None, f"{event.writer}'s edit of {event.noun} {event.row_id}'s {event.field} was kept over yours", "warn", detail=f"kept: {event.field_value[:DETAIL_CHARACTERS]}", row=event.ref, shows=CardKind.CONFLICTS)
        if isinstance(event, EditDropped):
            self.cards.show(event.environment_id, None, f"{event.noun.capitalize()} {event.row_id} was deleted by a colleague, so your edit of it was dropped", "warn", shows=CardKind.CONFLICTS)
