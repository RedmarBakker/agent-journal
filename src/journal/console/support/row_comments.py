from journal.features.messages.support.passage_place import PassagePlace
from journal.models.all_models import AllModels
from journal.models.message import Message
from journal.models.support.commentable import Commentable
from journal.models.support.ref import Ref
from journal.repositories.messages import Messages

COMMENTS_VERB = "comments"


class RowComments:
    """The comments verb every Commentable model's noun has: journal doc comments 12 lists the comments written under that row, each with who wrote it, when, whether it is answered, and where its passage sits now."""

    def __init__(self, messages: Messages, passages: PassagePlace) -> None:
        self.messages, self.passages = messages, passages
        self.tables = {model.noun(): model.table() for model in AllModels.MODELS if issubclass(model, Commentable)}

    def nouns(self) -> tuple[str, ...]:
        return tuple(self.tables)

    def listed(self, noun: str, number: int) -> int:
        ref = Ref(self.tables[noun], number)
        comments = self.messages.row_comments(ref)
        if not comments:
            print(f"no comments on {noun} {number}")
        for comment in comments:
            print(self.heading(comment))
            for line in comment.quote.split("\n") if comment.is_passage_comment else ():
                print(f"  > {line}")
            if comment.is_passage_comment:
                print(self.passages.line(ref, comment.quote))
        return 0

    def heading(self, comment: Message) -> str:
        answered = "answered" if self.messages.answered(comment) else "not answered"
        return f"message {comment.id} from {comment.sender}, {comment.created_at:%Y-%m-%d %H:%M}, {answered}: {comment.text_body}"
