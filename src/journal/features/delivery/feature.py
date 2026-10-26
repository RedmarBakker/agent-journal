from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.mark_kinds import JOURNAL
from journal.support.card_type import CardType
from journal.features.delivery.listeners.confirm_read import ConfirmRead
from journal.features.delivery.listeners.confirm_typed import ConfirmTyped
from journal.features.delivery.listeners.line_batch_release import LineBatchRelease
from journal.features.delivery.listeners.line_retyping import LineRetyping
from journal.features.delivery.listeners.menu_answer_card import MenuAnswerCard
from journal.features.feature import Feature
from journal.support.typed_lines import BATCH_OPTION


class Delivery(Feature):
    name = "delivery"
    card_families = (CardFamily("menus", "Menus", "bolt", JOURNAL),)
    card_kinds = (CardTypeEntry(CardType.MENUS, "Menus the journal answered", "menus"),)
    title = "Delivery"
    help = "A line the journal types is confirmed by the prompt that brings it back; one that has not come back while the agent sits between turns is typed again, six times at most, and the chat says so. Lines go at most once a window, the rest held and typed as one."
    BATCH_SECONDS = BATCH_OPTION
    options = (BATCH_SECONDS,)
    listeners = (ConfirmTyped, ConfirmRead, LineRetyping, LineBatchRelease, MenuAnswerCard)
