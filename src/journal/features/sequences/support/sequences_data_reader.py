from datetime import datetime, timezone

from journal.features.sequences.support.sequences_data import SequencesData
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.repositories.questions import Questions
from journal.repositories.workers import Workers
from journal.features.sequences.support.stacked_runs import StackedRuns
from journal.support.time_source import TimeSource

STEP_KEYS = ("sequences.step_to_follow", "sequences.sequence_paused", "sequences.following_the_step")
DISTANT_SECONDS = 10.0 ** 9


class SequencesDataReader:
    """Reads the sequences feature's part of the feature data for an agent, from the sequence state on its stack and the record: the step lines typed and the tool uses."""

    def __init__(self, entries: Entries, questions: Questions, workers: Workers, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.entries, self.questions, self.workers = entries, questions, workers

    def read(self, agent: Agent) -> SequencesData:
        run = StackedRuns.current(agent)
        if run is None:
            return SequencesData.empty(DISTANT_SECONDS)
        uses = self.entries.tool_starts(agent.session, last=1)
        last_line = self.entries.last_line_entry(agent.session, STEP_KEYS)
        started = datetime.fromisoformat(run.started_at).timestamp() if run.started_at else 0.0
        keyed_at = last_line.creation_time.timestamp() if last_line and last_line.creation_time.timestamp() >= started else 0.0
        line_time = max(keyed_at, datetime.fromisoformat(run.announced_at).timestamp() if run.announced_at else 0.0)
        return SequencesData(
            sequence_id=run.sequence_id, step=run.step + 1, step_text=run.text, pause_reason=run.pause_reason, is_adopted=bool(run.adopted_at),
            step_repeated=line_time > (uses[0].creation_time.timestamp() if uses else 0.0),
            step_silence_seconds=self.time_source.moment().timestamp() - line_time if line_time else DISTANT_SECONDS,
            is_typable=not any(agent.session in (w.session, w.resume) for w in self.workers.global_matching(environment_id=agent.environment_id)),
            question_open=bool(self.questions.open()),
            obligations_due=not agent.is_overview_read or bool(agent.threshold_due) or bool(agent.skills_due))
