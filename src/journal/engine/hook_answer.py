from journal.engine.delivery import Delivery
from journal.engine.state_machine import StateMachine
from journal.repositories.agents import Agents
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.support.decision import Decision


class HookAnswer(AgentListener[AgentEvent]):
    """The first listener on every agent event before the hook answers: asks the state machine for its reply, has the delivery carry out what the reply asks of the terminal, and answers the hook with its decision; a worker's lines wait on its row for its next hook."""


    def __init__(self, machine: StateMachine, delivery: Delivery, agents: Agents) -> None:
        self.machine, self.delivery, self.agents = machine, delivery, agents

    def handle(self, event: AgentEvent) -> Decision:
        if isinstance(event, ToolStarting) and event.call.is_panic_line():
            return Decision()
        agent = self.agents.newest_row(event.agent)
        self.delivery.silence(event)
        reply = self.machine.reply(agent, event)
        self.delivery.applied(reply, event.typing_delay)
        if agent.role.is_helper():
            return self.machine.worker_decision(agent.row_id, reply.decision, event)
        return self.delivery.hook_decision(event, reply.decision)
