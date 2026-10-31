from journal.features.voices.support.voices_data import VoicesData
from journal.models.agent import Agent
from journal.features.voices.support.voice_choice import VoiceChoice
from journal.features.voices.voices_nudges import VoicesNudges
from journal.repositories.entries import Entries


class VoicesDataReader:
    """Reads the voices feature's part of the feature data for an agent."""

    def __init__(self, selection: VoiceChoice, entries: Entries) -> None:
        self.chosen, self.entries = selection, entries

    def read(self, agent: Agent) -> VoicesData:
        introduced = self.entries.last_key_moment(agent.session, VoicesNudges.INTRODUCE_YOURSELF.key) is not None
        return VoicesData(instruction=self.chosen.instruction(), introduction_sent=introduced)
