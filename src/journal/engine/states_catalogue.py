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
from journal.support.agent_role import AgentRole


class StatesCatalogue:
    """Every state by name: the engine's own and those of every feature, with a name two features add belonging to the one that extends the other. A row's state column becomes the class that holds its behaviour; a name no feature has any more resolves to the first state, Idle; and the bottom of a main agent's stack is the state of the work mode a feature's setting picks, Idle when none does, while every helper's is Void, with the state its role works in from its start pushed over it when it has one."""

    ENGINE_STATES: tuple[type[BaseState], ...] = (Compacting, Ended, Void, DemandBlock, Panicking, LockedOut)

    def __init__(self, features: FeatureRegistry) -> None:
        self._states: dict[str, type[BaseState]] = {}
        for state in [*features.states(), *self.ENGINE_STATES]:
            self._states[state.name] = self.derived(self._states.get(state.name, state), state)
        self.modes, self.role_floors = features.modes(), features.floors()

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

    def restored(self, name: str, data: dict) -> BaseState:
        state = self._states.get(name) or self._states["idle"]
        return state.restored(data or {})

    def first(self) -> BaseState:
        return self.restored("idle", {})

    def sent_first(self, role: AgentRole) -> BaseState:
        return self.role_floors.get(role, Void)()

    def mode_state(self, settings: Settings) -> type[BaseState]:
        picks = [modes.states.get(str(settings.value(modes.option))) for modes in self.modes]
        return next((state for state in picks if state), type(self.first()))

    def is_mode_floor(self, state: BaseState) -> bool:
        return any(type(state) in modes.states.values() for modes in self.modes)

    def floor(self, stack: Stack, settings: Settings, role: AgentRole) -> Stack:
        return self.apply_mode(stack, settings) if role == AgentRole.MAIN else self.helper_floor(stack)

    def helper_floor(self, stack: Stack) -> Stack:
        bottom = stack.states[0]
        if isinstance(bottom, Void):
            return stack
        return Stack((Void(), *(stack.states[1:] if self.is_bottom(bottom) else stack.states)))

    def apply_mode(self, stack: Stack, settings: Settings) -> Stack:
        state = self.mode_state(settings)
        if type(stack.states[0]) is state:
            return stack
        return Stack((state.restored(stack.states[0].serialized()), *stack.states[1:]))

    def is_bottom(self, state: BaseState) -> bool:
        return isinstance(state, (self.bottom_root(), Void))

    def bottom_root(self) -> type[BaseState]:
        return [base for base in type(self.first()).__mro__ if getattr(base, "name", "") == "idle"][-1]

    def stack(self, agent: Agent) -> Stack:
        stored = Stack(tuple(self.restored(row["state"], row["data"]) for row in agent.stack)) if agent.stack else self.stack_base(self.restored(agent.state, agent.data), agent.role)
        return self.helper_floor(stored) if agent.role.is_helper() else stored

    def stack_base(self, state: BaseState, role: AgentRole) -> Stack:
        layers = Stack((state,)) if self.is_bottom(state) else Stack((self.first(), state))
        return self.helper_floor(layers) if role.is_helper() else layers

    def reset_stack(self, stack: Stack, role: AgentRole) -> Stack:
        return Stack(self.helper_floor(stack).states[:2]) if role.is_helper() else Stack((self.first(),))
