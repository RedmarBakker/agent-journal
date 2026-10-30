from journal.engine.delivery import Delivery
from journal.engine.support.decision_returns import DecisionReturns
from journal.engine.state_machine import StateMachine
from journal.repositories.agents import Agents
from journal.repositories.origin import Origin
from journal.repositories.scope import Scope
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.support.decision import Decision


class HookAnswer(AgentListener[AgentEvent]):
    """The first listener on every agent event before the hook answers: asks the state machine for its reply, has the delivery carry out what the reply asks of the terminal, and answers the hook with its decision; a worker's lines wait on its row for its next hook."""


    def __init__(self, machine: StateMachine, delivery: Delivery, agents: Agents, returns: DecisionReturns, scope: Scope) -> None:
        self.machine, self.delivery, self.agents, self.returns, self.scope = machine, delivery, agents, returns, scope

    def handle(self, event: AgentEvent) -> Decision:
        with self.scope.entered(Origin.agent_origin(event.agent, self.scope.actor)):
            if isinstance(event, ToolStarting) and event.call.is_panic_line():
                return Decision()
            agent = self.agents.newest_row(event.agent)
            self.delivery.silence(event)
            reply = self.machine.reply(agent, event)
            self.delivery.applied(reply, event.typing_delay)
            return self.returns.chosen(reply.bottom_state).hook_decision(reply, event)
