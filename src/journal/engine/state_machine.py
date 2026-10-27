from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.support.agent_role import AgentRole
from journal.engine.states.compacting import Compacting
from journal.engine.support.typist import Typist
from journal.engine.delivery import Delivery
from journal.engine.nudger import Nudger
from journal.engine.support.settings import Settings
from journal.repositories.setting_rows import SettingRows
from journal.engine.support.feature_registry import FeatureRegistry
from journal.engine.states.ended import Ended
from journal.engine.support.machine_answer import MachineAnswer
from journal.engine.support.machine_reply import MachineReply
from journal.engine.support.assigner_resolution import AssignerResolution
from journal.engine.support.block import Block
from journal.engine.support.stack import Stack
from journal.engine.support.data_readers import DataReaders
from journal.events.feature_data import FeatureData
from journal.events.event import Event
from journal.events.rows.row_event import RowEvent
from journal.repositories.scope import Scope
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.engine.demand_tracker import DemandTracker
from journal.support.moment import Moment
from journal.events.bus import Bus
from journal.support.decision import Decision
from journal.support.actor import Actor
from journal.engine.nudge import Nudge
from journal.models.agent import Agent
from journal.support.rejection import Rejection
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.engine.support.stack_history import StackHistory
from journal.engine.listener_index import ListenerIndex
from journal.engine.support.session_agents import SessionAgents


TOOL_ANSWER_LINE_COUNT = 3
JOURNAL_START = "the journal started, so no compaction is still running"

class StateMachine:
    """Holds and moves each agent's stack: tracks the agent's demands at each of its tool uses, loads the agent's state, asks the task assigner in force before the stack answers a hook event, so a stop meets the task it starts, and, through RowAssignment, after every listener of a row event has heard it, so a closed task is let go and marked first, asks the state the event, saves the new state, and answers with a reply, the decision and the lines, remarks and terminal moves its states asked for, a tool use's answer taking at most three lines and queuing the rest for the next hook, which the delivery carries out; it reaches no terminal itself."""

    def __init__(self, agents: Agents, states: StatesCatalogue, nudger: Nudger, bus: Bus, settings: SettingRows, features: FeatureRegistry, scope: Scope, entries: Entries, readers: DataReaders, sessions: SessionAgents, tracker: DemandTracker, assigners: AssignerResolution, delivery: Delivery) -> None:
        self.agents, self.states, self.nudger, self.bus, self.tracker, self.assigners, self.delivery = agents, states, nudger, bus, tracker, assigners, delivery
        self.listener_index = ListenerIndex({})
        self.settings, self.features, self.scope, self.entries, self.readers, self.sessions = settings, features, scope, entries, readers, sessions

    def worker_decision(self, agent_id: int, decision: Decision, event: AgentEvent) -> Decision:
        agent = self.agents.find(agent_id)
        if event.has_hook_lines():
            self.agents.save(agent.with_(queued_lines=()), Actor.system())
            return Decision.allowed_with("\n".join(agent.queued_lines)).merged(decision)
        if decision.context:
            self.agents.save(agent.queued(decision.context), Actor.system())
        return Decision(decision.allowed, decision.reason)

    def index_listeners(self) -> None:
        conduct_sets = [self.agent_conducts(role, lowest_state) for role in self.features.roles() for lowest_state in (BaseState, *self.features.mode_states())]
        self.listener_index = ListenerIndex.built(list(self.states.classes()), list(dict.fromkeys(conduct_sets)), self.event_kinds(Event))

    def agent_conducts(self, role: AgentRole, lowest_state: type[BaseState]) -> tuple[type[Conduct], ...]:
        return (*self.features.conducts(role), *self.features.mode_conducts(role, lowest_state))

    @classmethod
    def event_kinds(cls, type_name: type) -> list[type]:
        return [type_name, *(descendant for subclass in type_name.__subclasses__() for descendant in cls.event_kinds(subclass))]

    @staticmethod
    def is_queued_remark(agent: Agent, nudge: Nudge, event: AgentEvent | RowEvent) -> bool:
        return nudge.is_remark and not event.has_hook_lines() and not agent.role.is_helper()

    @staticmethod
    def answer_lines(lines: list[str], event: AgentEvent) -> list[str]:
        return lines[:TOOL_ANSWER_LINE_COUNT] if isinstance(event, (ToolStarting, ToolFinished)) else lines

    @staticmethod
    def overflow_lines(lines: list[str], event: AgentEvent) -> list[str]:
        return lines[TOOL_ANSWER_LINE_COUNT:] if isinstance(event, (ToolStarting, ToolFinished)) else []

    def row_replies(self, event: RowEvent) -> list[MachineReply]:
        replies = []
        for agent in self.audience(event):
            with self.scope.environment(agent.environment_id):
                replies.append(self.reply(agent, event.reaching(agent.session)))
        return replies

    def audience(self, event: RowEvent) -> list[Agent]:
        unended = [agent for environment_id in event.environment_ids() for agent in self.agents.unended_scoped(environment_id)] if event.environment_id else self.agents.unended()
        return [agent for agent in unended if self.features.receives_row_event(type(event).feature_name, agent.role)]

    def queue_lines(self, agent: Agent, lines: str) -> None:
        self.agents.save(self.agents.find(agent.row_id).queued(lines), Actor.system())

    def mode_change(self, stored_stack: Stack, stack: Stack) -> tuple[Nudge, ...]:
        bottom, previous_bottom = stack.states[0], stored_stack.states[0]
        return bottom.mode_lines() if type(bottom) is not type(previous_bottom) and self.states.is_mode_floor(previous_bottom) else ()

    def row_assignments(self, event: RowEvent) -> None:
        for agent in self.audience(event):
            with self.scope.environment(agent.environment_id):
                self.assigners.resolved(agent).next_task(agent, event.reaching(agent.session))

    def assigned(self, agent: Agent, event: AgentEvent) -> Agent:
        if not self.assigners.resolved(agent).next_task(agent, event).has_task():
            return agent
        return self.agents.find(agent.row_id)

    def reply(self, agent: Agent, event: AgentEvent | RowEvent) -> MachineReply:
        return self.stack_reply(agent if isinstance(event, RowEvent) else self.assigned(agent, event), event)

    def stack_reply(self, agent: Agent, event: AgentEvent | RowEvent) -> MachineReply:
        settings = self.top_state()
        stored_stack = self.states.stack(agent)
        stack = self.states.floor(stored_stack, settings, agent.role)
        mode_change = self.mode_change(stored_stack, stack)
        event = event.with_data(self.readers.agent_data(agent))
        if isinstance(event, ToolStarting):
            self.tracker.count(agent.session, self.features.demands(agent.role), event.data, Moment(seconds=event.time, tool_uses=event.tool_use))
        transition = stack.top().answered(event, settings, self.listener_index.state_listeners(type(stack.top()), self.agent_conducts(agent.role, type(stack.states[0])), type(event)))
        machine_answer = self.answer_moves(stack, transition, agent.role, settings, event.data)
        if transition.dropped:
            self.entries.save(StackHistory.entry(agent, list(agent.stack), event.key, Actor.system(), dropped=list(transition.dropped)), Actor.system())
        agent = self._store(agent, machine_answer, event.key, Actor.system())
        nudge_lines = [(nudge, line) for nudge in (*mode_change, *transition.nudges, *machine_answer.nudges) if (line := self.nudger.deliver(agent, nudge))]
        queued = tuple(line for nudge, line in nudge_lines if self.is_queued_remark(agent, nudge, event))
        lines = [line for _, line in nudge_lines if line not in queued]
        lines, remarks = self.answer_lines(lines, event), (*queued, *self.overflow_lines(lines, event))
        keystrokes = tuple(line for nudge in transition.terminal_lines if (line := self.nudger.deliver(agent, nudge)))
        reasons = [line for refusal in (transition.refusal, *transition.extra_refusals) if refusal and (line := self.nudger.refuse_with(agent, refusal))]
        if reasons:
            return MachineReply(agent, Decision.refuse("\n".join([*reasons, *lines])), keystrokes, remarks)
        if machine_answer.refusal and (line := self.nudger.refuse_with(agent, machine_answer.refusal.nudge)):
            return MachineReply(agent, Decision.refuse(line), keystrokes, remarks)
        answered = MachineReply(agent, Decision.allowed_with("\n".join(lines)), keystrokes, remarks)
        return answered.merged(self.stack_reply(agent, event)) if transition.handed_down and machine_answer.stack == stack.popped() else answered

    def push(self, session: str, environment_id: int, destination: BaseState, actor: Actor, text: str) -> MachineReply:
        agent = self.sessions.agent(session, environment_id)
        return self.manual(agent, self.states.stack(agent).pushed(destination), actor, text)

    def pop(self, session: str, environment_id: int, actor: Actor, text: str) -> MachineReply:
        agent = self.sessions.agent(session, environment_id)
        return self.manual(agent, self.states.stack(agent).popped(), actor, text)

    def reset(self, session: str, environment_id: int, actor: Actor, text: str) -> MachineReply:
        agent = self.sessions.agent(session, environment_id)
        return self.manual(agent, self.states.reset_stack(self.states.stack(agent), agent.role), actor, text)

    def compactions_ended(self) -> list[MachineReply]:
        return [self.manual(agent, self.states.stack(agent).popped(), Actor.system(), JOURNAL_START) for agent in self.agents.global_state(Compacting.name)]

    def manual(self, agent: Agent, following: Stack, actor: Actor, text: str) -> MachineReply:
        machine_answer = self.hook_machine(self.states.stack(agent), following, self.top_state(), self.readers.agent_data(agent))
        resolved = self._store(agent, machine_answer, text, actor)
        if machine_answer.refusal:
            raise Rejection(machine_answer.refusal.nudge.rendered())
        keystrokes = tuple(line for nudge in machine_answer.nudges if (line := self.nudger.deliver(resolved, nudge)))
        return MachineReply(resolved, Decision(), keystrokes)

    def top_state(self) -> Settings:
        return Settings.applied(self.settings, self.features.options())

    def answer_moves(self, stack: Stack, transition: Transition, role: AgentRole, settings: Settings, data: FeatureData) -> MachineAnswer:
        placed = self.placed(stack, transition.target, role)
        return self.hook_machine(placed, self.moved(placed, transition), settings, data)

    def hook_machine(self, previous: Stack, following: Stack, settings: Settings, data: FeatureData) -> MachineAnswer:
        if following.states[:-1] == previous.states and len(following.states) == len(previous.states) + 1:
            return self.pushed_down(previous, following, settings)
        if following == previous.popped() and len(previous.states) > 1:
            return self.forwarded(previous, following, settings, data)
        return MachineAnswer(following)

    def pushed_down(self, previous: Stack, following: Stack, settings: Settings) -> MachineAnswer:
        paused = previous.top().on_pause(settings)
        pushed = following.top().on_push(settings)
        if isinstance(pushed, Block):
            return MachineAnswer(previous, refusal=pushed, refused=following.top().name)
        return MachineAnswer(following, (*paused, *pushed))

    def forwarded(self, previous: Stack, following: Stack, settings: Settings, data: FeatureData) -> MachineAnswer:
        popped = previous.top().on_pop(settings)
        resumed = following.top().on_resume(data, settings)
        if not isinstance(resumed, Transition):
            return MachineAnswer(following, (*popped, *resumed))
        if resumed.popped and len(following.states) > 1:
            lower = self.forwarded(following, following.popped(), settings, data)
            return MachineAnswer(lower.stack, (*popped, *resumed.nudges, *lower.nudges))
        return MachineAnswer(following.with_top(resumed.target), (*popped, *resumed.nudges))

    def moved(self, stack: Stack, transition: Transition) -> Stack:
        if transition.pushed:
            return stack.pushed(transition.pushed)
        if transition.popped:
            return stack.popped()
        return stack

    def placed(self, stack: Stack, destination: BaseState, role: AgentRole) -> Stack:
        if type(destination) is type(stack.top()):
            return stack.with_top(destination)
        return self.states.stack_base(destination, role)

    def _store(self, agent: Agent, machine_answer: MachineAnswer, cause: str, actor: Actor) -> Agent:
        stack, destination = machine_answer.stack, machine_answer.stack.top()
        if machine_answer.refusal:
            self.entries.save(StackHistory.entry(agent, list(agent.stack), cause, actor, refused=machine_answer.refused, line=machine_answer.refusal.nudge.rendered()), actor)
        if self.is_unchanged(agent, destination, stack):
            return agent
        typist = Typist()
        stack.replace(self.states.stack(agent), typist)
        resolved = self.agents.save(agent.with_(state=destination.name, data=destination.serialized(), stack=tuple(stack.serialized())), actor)
        self.delivery.moved(agent.environment_id, typist.moves)
        if self.is_moved(agent, stack):
            self.entries.save(StackHistory.entry(agent, stack.serialized(), cause, actor), actor)
        return resolved

    @staticmethod
    def is_unchanged(agent: Agent, destination: BaseState, stack: Stack) -> bool:
        return destination.name == agent.state and destination.serialized() == agent.data and stack.serialized() == list(agent.stack)

    @staticmethod
    def is_moved(agent: Agent, stack: Stack) -> bool:
        return [state.name for state in stack.states] != [row["state"] for row in agent.stack]
