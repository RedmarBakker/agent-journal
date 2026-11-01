from journal.engine.base_state import BaseState
from journal.engine.support.stack import Stack
from journal.models.agent import Agent
from journal.engine.states.panicking import Panicking
from journal.engine.states.wait import Wait
from journal.engine.states.compacting import Compacting
from journal.engine.states.locked_out import LockedOut
from journal.engine.states.void import Void
from journal.engine.states.ended import Ended
from journal.engine.states.demand_block import DemandBlock
from journal.engine.support.feature_registry import FeatureRegistry
from journal.engine.support.settings import Settings
from journal.support.option import Option
from journal.support.agent_role import AgentRole


class StatesCatalogue:
    """Every state by name: the engine's own and those of every feature, with a name two features add belonging to the one that extends the other. A row's state column becomes the class that holds its behaviour; a name no feature has any more resolves to the first state, Idle; and the bottom of a main agent's stack is the state picked by the first feature, in the registry's order, whose setting picks one, Idle when none does, while every helper's is Void, with the state its role works in from its start pushed over it when it has one."""

    ENGINE_STATES: tuple[type[BaseState], ...] = (Compacting, Ended, Void, DemandBlock, Panicking, LockedOut)

    def __init__(self, features: FeatureRegistry) -> None:
        self._states: dict[str, type[BaseState]] = {}
        for state in [*features.states(), *self.ENGINE_STATES]:
            self._states[state.name] = self.derived(self._states.get(state.name, state), state)
        self.state_floors, self.role_floors = features.state_floors(), features.floors()

    @staticmethod
    def derived(registered: type[BaseState], state: type[BaseState]) -> type[BaseState]:
        if issubclass(state, registered):
            return state
        if issubclass(registered, state):
            return registered
        raise ValueError(f"two unrelated states are both named {state.name}: {registered.__name__} and {state.__name__}")

    def classes(self) -> list[type[BaseState]]:
        return list(self._states.values())

    def known(self, name: str) -> bool:
        return name in self._states

    def names(self) -> list[str]:
        return sorted(self._states)

    def waits(self) -> list[str]:
        return sorted(name for name, state in self._states.items() if issubclass(state, Wait))

    def title(self, name: str) -> str:
        return self._states[name].title if name in self._states else name

    def parent(self, name: str) -> str:
        state = self._states.get(name)
        return next((registered.name for base in state.__mro__[1:] for registered in self._states.values() if registered is base), "") if state else ""

    def listed(self) -> list[dict]:
        names = ["idle"] + [name for name in self._states if name != "idle"]
        return [{"key": name, "title": self.title(name), "parent": self.parent(name)} for name in names]

    def label(self, name: str, data: dict) -> str:
        state = self._states.get(name)
        return state.restored(data or {}).trail_label() if state else name

    def restored(self, name: str, data: dict) -> BaseState:
        state = self._states.get(name) or self._states["idle"]
        return state.restored(data or {})

    def top(self, agent: Agent) -> BaseState:
        return self.restored(agent.state, agent.data)

    def has_ended(self, agent: Agent) -> bool:
        return self.top(agent).final

    def first(self) -> BaseState:
        return self.restored("idle", {})

    def sent_first(self, role: AgentRole) -> BaseState:
        return self.role_floors.get(role, Void)()

    def selected_floor(self, settings: Settings) -> type[BaseState]:
        picks = [floor.states.get(settings.value(floor.option)) for floor in self.state_floors]
        return next((state for state in picks if state), type(self.first()))

    def floor_options(self) -> list[Option]:
        return [floor.option for floor in self.state_floors]

    def is_selected_floor(self, state: BaseState) -> bool:
        return any(type(state) in floor.states.values() for floor in self.state_floors)

    def floor(self, stack: Stack, settings: Settings, role: AgentRole) -> Stack:
        return self.apply_floor(stack, settings) if role == AgentRole.MAIN else self.helper_floor(stack)

    @staticmethod
    def helper_floor(stack: Stack) -> Stack:
        return Stack((stack.bottom().floored(Void), *stack.states[1:]))

    def apply_floor(self, stack: Stack, settings: Settings) -> Stack:
        state = self.selected_floor(settings)
        if type(stack.states[0]) is state or stack.states[0].keeps_floor():
            return stack
        return Stack((state.restored(stack.states[0].serialized()), *stack.states[1:]))

    @staticmethod
    def helper_layers(first_state: BaseState) -> Stack:
        return Stack((first_state,)) if isinstance(first_state, Void) else Stack((Void(), first_state))

    def is_bottom(self, state: BaseState) -> bool:
        return isinstance(state, (self.bottom_root(), Void))

    def bottom_root(self) -> type[BaseState]:
        return [base for base in type(self.first()).__mro__ if getattr(base, "name", "") == "idle"][-1]

    def stack(self, agent: Agent) -> Stack:
        return Stack(tuple(self.restored(row["state"], row["data"]) for row in agent.stack)) if agent.stack else self.stack_base(self.top(agent))

    def stack_base(self, state: BaseState) -> Stack:
        return Stack((state,)) if self.is_bottom(state) else Stack((self.first(), state))

    def reset_stack(self, stack: Stack) -> Stack:
        bottom = stack.bottom()
        return Stack((bottom,)) if bottom.keeps_floor() else Stack(bottom.reset_states(stack.states))
