from journal.features.etiquette.support.etiquette_data import EtiquetteData
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.features.etiquette.etiquette_nudges import EtiquetteNudges


class EtiquetteDataReader:
    """Reads the etiquette feature's part of the feature data for an agent."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def read(self, agent: Agent) -> EtiquetteData:
        return EtiquetteData(reminder_gap=self.entries.recent_line_entries(agent.session, EtiquetteNudges.JOURNAL_LINE_RULE.key), code_edits=agent.code_edits)
