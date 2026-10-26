from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.features.suggestions.support.suggester import Suggester
from journal.models.message import Message
from journal.models.suggestion import Suggestion
from journal.support.actor import Actor
from journal.support.card_type import CardType


class SuggestionProcessCard(ProcessCard):
    """The process card of a suggestion the journal makes, open with its accept button until it is answered and then showing the answer."""

    name = "suggestion"

    @staticmethod
    def key(suggestion: Suggestion) -> str:
        return f"suggestion:{suggestion.id}"

    def card_contents(self, suggestion: Suggestion, suggester: Suggester, environment_id: int) -> ProcessCardContents:
        data = {"kind": "suggestion", "row": f"suggestions:{suggestion.id}", "accept": suggester.accept_label, "answer": suggestion.answer or "", "description": suggester.detail()}
        return ProcessCardContents(self.name, environment_id, self.key(suggestion), suggestion.title, data, Actor.system(), CardType.SUGGESTIONS, False)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
