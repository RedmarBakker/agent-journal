from journal.engine.nudge import Nudge


class QuestionsNudges:
    """The nudges of the questions feature."""

    QUESTION_ANSWERED = Nudge("questions", "question_answered", "question {{n}} is answered", "`journal question show {{n}}`, then act on it", repeat_interval=0)
    JOURNAL_QUESTION_TOOL = Nudge("questions", "ask_through_the_journal", "ask through the journal, not your own question tool", "`journal question ask \"<one line>\" --options \"a\" \"b\"`", repeat_interval=0)
