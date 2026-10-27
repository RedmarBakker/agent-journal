from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.edit_dropped import EditDropped
from journal.events.moments.edit_overridden import EditOverridden
from journal.events.moments.sync_moment import SyncMoment
from journal.events.moments.team_chat_claimed import TeamChatClaimed
from journal.events.moments.team_chat_files_diverged import TeamChatFilesDiverged
from journal.support.actor import Actor
from journal.support.card_type import CardType

DETAIL_CHARACTERS = 120


class SyncMomentCards(Listener[SyncMoment]):
    """What the team sync did or found that the user should see is one mark in the chat: the Team chat claimed while its holder was offline, its files on this machine kept apart, an edit kept over this machine's, a row deleted by a colleague."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SyncMoment) -> None:
        if isinstance(event, TeamChatClaimed):
            self.cards.show(event.environment_id, None, f"{event.holder} took over the Team chat while {event.former} was offline; {event.former}'s unsent changes stayed on their machine", actor=Actor.system(), shows=CardType.WORKTREES, outcome=CardOutcome.WARNED)
        if isinstance(event, TeamChatFilesDiverged):
            label = f"Team chat changes made on {event.device} were kept there and not replaced"
            self.cards.show(event.environment_id, None, label, key=f"team-chat-files:{event.device}", actor=Actor.system(), shows=CardType.WORKTREES, outcome=CardOutcome.WARNED)
        if isinstance(event, EditOverridden):
            self.cards.show(event.environment_id, None, f"{event.writer}'s change to this {event.noun} was kept instead of yours", detail=f"kept: {event.field_value[:DETAIL_CHARACTERS]}", row=event.ref, shows=CardType.CONFLICTS, outcome=CardOutcome.WARNED)
        if isinstance(event, EditDropped):
            self.cards.show(event.environment_id, None, f"A colleague deleted this {event.noun}, so your change to it was dropped", shows=CardType.CONFLICTS, outcome=CardOutcome.WARNED)
