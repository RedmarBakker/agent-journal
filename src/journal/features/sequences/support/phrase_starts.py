from journal.features.sequences.support.announced_starts import AnnouncedStarts
from journal.repositories.sequences import Sequences


class PhraseStarts:
    """The sequences whose phrase is the user's request itself, started for the agent the words were written to."""

    def __init__(self, sequences: Sequences, starts: AnnouncedStarts) -> None:
        self.sequences, self.starts = sequences, starts

    def start(self, text: str, session: str, environment_id: int) -> None:
        for sequence in self.sequences.requested_sequences(text):
            self.starts.start(sequence, session, environment_id)
