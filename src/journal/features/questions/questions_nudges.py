from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class QuestionsNudges:
    """The nudges of the questions feature."""

    QUESTION_ANSWERED = Nudge("questions", "question_answered", "question {{n}} is answered", "read it with `journal question show {{n}}` and act on it", repeat=Timeout.seconds(0))
    QUESTION_CLOSED = Nudge("questions", "question_closed", "the user closed question {{n}} unanswered", "go on without it", repeat=Timeout.seconds(0))
    JOURNAL_QUESTION_TOOL = Nudge("questions", "ask_through_the_journal", "ask with `journal question ask \"<one line>\" --options \"a\" \"b\"`, not your own question tool", "", repeat=Timeout.seconds(0))
