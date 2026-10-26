from typing import Callable

from journal.engine.nudger import Nudger
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.session_agents import SessionAgents
from journal.engine.nudge import Nudge
from journal.features.sequences.support.stacked_runs import FOLLOWING_SEQUENCE, StackedRuns
from journal.features.skills.support.requirements import Requirements
from journal.support.actor import Actor
from journal.models.agent import Agent
from journal.models.sequence import Sequence
from journal.models.support.ref import Ref
from journal.support.sequence_run import SequenceRun
from journal.support.rejection import Rejection
from journal.repositories.agents import Agents
from journal.repositories.rows import Rows
from journal.repositories.workers import Workers
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.support.time_source import TimeSource


class RunTracker:
    """The one way a sequence run is started and moved: each start and move is an event on the agent's row, which the sequence state on its stack answers; the runs themselves are read from those states, the bottom one first and the one in hand last."""

    def __init__(self, sessions: SessionAgents, agents: Agents, requirements: Requirements, workers: Workers, rows: Rows, nudger: Nudger, time_source: TimeSource, states: StatesCatalogue) -> None:
        self.time_source, self.states = time_source, states
        self.sessions, self.agents, self.requiring, self.workers, self.rows, self.nudger = sessions, agents, requirements, workers, rows, nudger

    @staticmethod
    def runs(agent: Agent) -> list[SequenceRun]:
        return StackedRuns.runs(agent)

    def current(self, session: str, environment_id: int) -> SequenceRun | None:
        return StackedRuns.current(self.sessions.agent(session, environment_id))

    def start(self, sequence: Sequence, session: str, environment_id: int, topic: str = "") -> str:
        agent = self.sessions.agent(session, environment_id)
        if any(run.sequence_id == sequence.id for run in self.runs(agent)) or not sequence.steps or not self.states.stack(agent).top().takes_pushes():
            return ""
        run = SequenceRun(sequence.row_id, sequence.title, tuple(sequence.steps), subject=topic, started_at=self.timestamp(), announced_at=self.timestamp(), end_condition=tuple(sequence.end_condition))
        liabilities = self.requiring.require(agent, self.requiring.obligations(agent, self.requiring.lookup("sequences")))
        self.moved(agent, lambda current: current.sequence_started(run, self.time_source.seconds()))
        return "\n".join([*liabilities, self.line(agent, self.step(run))])

    def follow(self, session: str, environment_id: int) -> SequenceRun:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.moved(agent, lambda current: current.sequence_step_adopted(self.time_source.seconds()))
        return run.adopted(self.timestamp()).paused("")

    def next(self, session: str, environment_id: int) -> str:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.refuse_open_end(run)
        self.moved(agent, lambda current: current.sequence_step_finished(run, self.time_source.seconds()))
        if run.last:
            return self.line(agent, SequencesNudges.SEQUENCE_ENDED.create(n=run.sequence_id))
        return self.line(agent, self.step(run.advanced()))

    def skip(self, session: str, environment_id: int) -> None:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.moved(agent, lambda current: current.sequence_step_skipped(run, self.time_source.seconds()))

    def end(self, session: str, environment_id: int) -> None:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.moved(agent, lambda current: current.sequence_cancelled(run, self.time_source.seconds()))

    def refuse_open_end(self, run: SequenceRun) -> None:
        state = self.rows.row_state(Ref.parse(run.subject)) if run.last and run.subject and run.end_condition else ""
        if state and state not in run.end_condition:
            raise Rejection(f"sequence {run.sequence_id} ends when {run.subject} is {' or '.join(run.end_condition)}; it is {state}. finish it first, or `journal sequence abandon --why \"<why>\"`")

    def abandon(self, session: str, environment_id: int, reason: str) -> tuple[SequenceRun, str]:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.moved(agent, lambda current: current.sequence_abandoned(reason, self.time_source.seconds()))
        return run, self.line(agent, SequencesNudges.SEQUENCE_ABANDONED.create(n=run.sequence_id))

    def pause(self, session: str, environment_id: int, reason: str) -> SequenceRun:
        agent = self.sessions.agent(session, environment_id)
        run = StackedRuns.current(agent)
        self.moved(agent, lambda current: current.sequence_paused(reason, self.time_source.seconds()))
        return run.paused(reason)

    def finish_matching(self, environment_id: int, missing, reason: str) -> None:
        for agent in self.agents.stacked_main_agents(FOLLOWING_SEQUENCE):
            for run in [run for run in self.runs(agent) if agent.environment_id == environment_id and missing(run)]:
                self.moved(agent, self.unfinishable(run, reason))

    def environments_running(self, sequence_id: int) -> set[int]:
        return {agent.environment_id for agent in self.agents.stacked_main_agents(FOLLOWING_SEQUENCE) for run in self.runs(agent) if run.sequence_id == sequence_id}

    def transfer(self, session: str, environment_id: int) -> None:
        agent = self.sessions.agent(session, environment_id)
        ended = self.agents.ended_stacked_agent(environment_id, session, FOLLOWING_SEQUENCE)
        if self.runs(agent) or ended is None:
            return
        for run in self.runs(ended):
            self.moved(agent, self.transferred(run))

    def unfinishable(self, run: SequenceRun, reason: str) -> Callable[[Agent], Agent]:
        return lambda current: current.sequence_cannot_finish(run.sequence_id, reason, self.time_source.seconds())

    def transferred(self, run: SequenceRun) -> Callable[[Agent], Agent]:
        return lambda current: current.sequence_transferred(run, self.time_source.seconds())

    def moved(self, agent: Agent, change: Callable[[Agent], Agent]) -> None:
        self.agents.rewritten(agent, Actor.system(), change)

    def typed_agent(self, session: str, environment_id: int) -> bool:
        return not any(session in (w.session, w.resume) for w in self.workers.global_matching(environment_id=environment_id))

    @staticmethod
    def step(run: SequenceRun) -> Nudge:
        return SequencesNudges.PENDING_STEP.create(n=run.sequence_id, step=run.step + 1, text=run.text)

    def line(self, agent: Agent, nudge: Nudge) -> str:
        return self.nudger.answer(agent, nudge) or ""

    def timestamp(self) -> str:
        return self.time_source.moment().isoformat()
