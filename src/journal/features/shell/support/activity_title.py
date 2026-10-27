from journal.support.rejection import Rejection

ACTIVITY_SUFFIX = "ing"
# the one rule a card's title follows, said wherever a title is asked for
TITLE_RULE = "a short, whole phrase in plain words in the user's own language that says what the run is doing, such as Running tests or Building the application"
# the connectives a phrase never stops on, which leave it half a sentence
CONNECTIVES = frozenset({"of", "the", "a", "an", "to", "for", "with", "and", "or", "in", "on", "at", "by", "from", "into", "over"})


class ActivityTitle:
    """A card's title says what the run is doing, Running tests or Building the application, as a whole phrase that starts with a word of activity, never a bare name such as Tests nor a half sentence such as Running the tests of."""

    @staticmethod
    def is_one_word(text: str) -> bool:
        return len(text.split(":")[0].split()) < 2

    @staticmethod
    def checked(text: str) -> str:
        title_parts = text.split()
        if text and ActivityTitle.is_one_word(text):
            raise Rejection(f"a card's title is {TITLE_RULE}, not the single word {text!r}: say what runs, and name it with --topic")
        if title_parts and not title_parts[0].lower().endswith(ACTIVITY_SUFFIX):
            raise Rejection(f"a card's title is {TITLE_RULE}, not {text!r}: open it on what it does")
        if title_parts and title_parts[-1].lower() in CONNECTIVES:
            raise Rejection(f"a card's title is {TITLE_RULE}, not {text!r}, which stops on {title_parts[-1]!r}: write the phrase whole")
        return text
