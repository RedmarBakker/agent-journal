from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import JOURNAL
from journal.support.card_type import CardType
from journal.features.delivery.listeners.confirm_typed import ConfirmTyped
from journal.features.delivery.listeners.line_batch_release import LineBatchRelease
from journal.features.delivery.listeners.line_retyping import LineRetyping
from journal.features.delivery.listeners.menu_answer_card import MenuAnswerCard
from journal.features.feature import Feature


class Delivery(Feature):
    name = "delivery"
    card_families = (CardFamily("menus", "Menus", "bolt", JOURNAL),)
    card_types = (CardTypeEntry(CardType.MENUS, "Menus the journal answered", "menus"),)
    title = "Delivery"
    help = "The journal's lines ride the answers of the agent's hooks. An agent that has stopped is woken by one line typed into its terminal, always the same, whose prompt carries what waits; it is confirmed by that prompt, and one that has not come back while the agent sits between turns is typed again, six times at most, and the chat says so."
    listeners = (ConfirmTyped, LineRetyping, LineBatchRelease, MenuAnswerCard)
