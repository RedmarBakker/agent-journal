import re
from datetime import datetime, timezone

from journal.engine.nudger import Nudger
from journal.engine.support.session_agents import SessionAgents
from journal.engine.nudge import Nudge
from journal.support.command_part import CommandPart
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

COMMAND_PATTERN = re.compile(r"`([^`<]+)")


class RunTracker:
    """The sequences an agent works through, stored on its row as a stack: one started inside another is the current one, and when it ends the other becomes current again. Every start goes through here."""

    def __init__(self, sessions: SessionAgents, agents: Agents, requirements: Requirements, workers: Workers, rows: Rows, nudger: Nudger) -> None:
        self.sessions, self.agents, self.requiring, self.workers, self.rows, self.nudger = sessions, agents, requirements, workers, rows, nudger

    def runs(self, agent: Agent) -> list[SequenceRun]:
        return [SequenceRun.build(raw) for raw in agent.sequence_runs or ()]

    def current(self, session: str, environment_id: int) -> SequenceRun | None:
        runs = self.runs(self.sessions.agent(session, environment_id))
        return runs[-1] if runs else None

    def start(self, sequence: Sequence, session: str, environment_id: int, topic: str = "") -> str:
        started = self.new_run(sequence, session, environment_id, topic)
        if started is None:
            return ""
        run, liabilities = started
        return "\n".join([*liabilities, self.line(self.sessions.agent(session, environment_id), self.step(run))])

    def new_run(self, sequence: Sequence, session: str, environment_id: int, topic: str = "") -> tuple[SequenceRun, list[str]] | None:
        agent = self.sessions.agent(session, environment_id)
        runs = self.runs(agent)
        if any(run.sequence_id == sequence.id for run in runs) or not sequence.steps:
            return None
        run = SequenceRun(sequence.row_id, sequence.title, tuple(sequence.steps), subject=topic, started_at=self.timestamp(), announced_at=self.timestamp(), end_condition=tuple(sequence.end_condition))
        self.rewritten(agent, lambda time: [*time, run])
        return run, self.requiring.require(agent, self.requiring.obligations(agent, self.requiring.lookup("sequences")))

    def next(self, session: str, environment_id: int) -> str:
        agent = self.sessions.agent(session, environment_id)
        runs = self.runs(agent)
        run = runs[-1]
        self.refuse_open_end(run)
        if not run.last:
            return self.line(agent, self.step(self.changed(session, environment_id, lambda time: time.advanced().announced(self.timestamp()))))
        return self.ended(agent, runs, self.line(agent, SequencesNudges.SEQUENCE_ENDED.create(n=run.sequence_id)))

    def ended(self, agent: Agent, runs: list[SequenceRun], ended: str) -> str:
        if len(runs) == 1:
            self.stored(agent, [])
            return ended
        outer = self.rewritten(agent, lambda time: [*time[:-2], time[-2].announced(self.timestamp())])[-1]
        return f"{ended}\n{self.line(agent, self.step(outer))}"

    def skip(self, session: str, environment_id: int) -> str:
        agent = self.sessions.agent(session, environment_id)
        runs = self.runs(agent)
        run = runs[-1]
        skipped = self.line(agent, SequencesNudges.STEP_OMISSION.create(n=run.sequence_id, step=run.step + 1))
        if run.last:
            return self.ended(agent, runs, f"{skipped}\n{self.line(agent, SequencesNudges.SEQUENCE_ENDED.create(n=run.sequence_id))}")
        moved = self.changed(session, environment_id, lambda time: time.advanced().announced(self.timestamp()))
        return f"{skipped}\n{self.line(agent, self.step(moved))}"

    def end(self, session: str, environment_id: int) -> str:
        agent = self.sessions.agent(session, environment_id)
        runs = self.runs(agent)
        return self.ended(agent, runs, self.line(agent, SequencesNudges.SEQUENCE_CANCELLED.create(n=runs[-1].sequence_id)))

    def refuse_open_end(self, run: SequenceRun) -> None:
        state = self.rows.row_state(Ref.parse(run.subject)) if run.last and run.subject and run.end_condition else ""
        if state and state not in run.end_condition:
            raise Rejection(f"sequence {run.sequence_id} ends when {run.subject} is {' or '.join(run.end_condition)}; it is {state}. finish it first, or `journal sequence abandon --why \"<why>\"`")

    def abandon(self, session: str, environment_id: int) -> tuple[SequenceRun, str]:
        agent = self.sessions.agent(session, environment_id)
        runs = self.runs(agent)
        return runs[-1], self.ended(agent, runs, self.line(agent, SequencesNudges.SEQUENCE_ABANDONED.create(n=runs[-1].sequence_id)))

    def finish_matching(self, environment_id: int, missing, reason: str) -> list[tuple[Agent, str]]:
        notified = []
        for agent in self.agents.sequence_agents(environment_id):
            runs = self.runs(agent)
            retained = [run for run in runs if not missing(run)]
            if len(retained) < len(runs):
                self.stored(agent, retained)
                notified.append((agent, "\n".join(self.line(agent, SequencesNudges.SEQUENCE_CANNOT_FINISH.create(n=run.sequence_id, why=reason)) for run in runs if missing(run))))
        return notified

    def environments_running(self, sequence_id: int) -> set[int]:
        return {agent.environment_id for agent in self.agents.main_agents() for run in self.runs(agent) if run.sequence_id == sequence_id}

    def follow(self, session: str, environment_id: int) -> SequenceRun:
        return self.changed(session, environment_id, lambda run: run.adopted(self.timestamp()).announced(self.timestamp()).paused(""))

    def pause(self, session: str, environment_id: int, reason: str) -> SequenceRun:
        return self.changed(session, environment_id, lambda run: run.paused(reason))

    def announce(self, session: str, environment_id: int) -> SequenceRun:
        return self.changed(session, environment_id, lambda run: run.announced(self.timestamp()))

    def changed(self, session: str, environment_id: int, change) -> SequenceRun:
        return self.rewritten(self.sessions.agent(session, environment_id), lambda time: [*time[:-1], change(time[-1])])[-1]

    def rewritten(self, agent: Agent, change) -> list[SequenceRun]:
        recent = self.agents.touched(agent, Actor.system(), lambda time: {"sequence_runs": tuple(run.as_dict() for run in change(self.runs(time)))})
        return self.runs(recent)

    def transfer(self, session: str, environment_id: int) -> None:
        agent = self.sessions.agent(session, environment_id)
        ended = self.agents.ended_sequence_agents(session)
        if agent.sequence_runs or not ended:
            return
        self.stored(agent, self.runs(ended[-1]))
        self.stored(ended[-1], [])

    def stored(self, agent: Agent, runs: list[SequenceRun]) -> None:
        self.agents.touch(agent, Actor.system(), sequence_runs=tuple(run.as_dict() for run in runs))

    @staticmethod
    def names(step_text: str, parts: tuple[CommandPart, ...]) -> bool:
        step_commands = [command.strip() for command in COMMAND_PATTERN.findall(step_text) if command.strip()]
        return any(part.text.strip().startswith(command) for part in parts for command in step_commands)

    def typed_agent(self, session: str, environment_id: int) -> bool:
        return not any(session in (w.session, w.resume) for w in self.workers.global_matching(environment_id=environment_id))

    @classmethod
    def reminder(cls, run: SequenceRun) -> Nudge:
        return SequencesNudges.SEQUENCE_PAUSED.create(n=run.sequence_id, step=run.step + 1, why=run.pause_reason) if run.pause_reason else cls.step(run)

    @staticmethod
    def step(run: SequenceRun) -> Nudge:
        return SequencesNudges.PENDING_STEP.create(n=run.sequence_id, step=run.step + 1, text=run.text)

    def line(self, agent: Agent, nudge: Nudge) -> str:
        return self.nudger.answer(agent, nudge) or ""

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
