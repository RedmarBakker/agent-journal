from journal.engine.delivery import Delivery
from journal.engine.support.decision_returns import DecisionReturns
from journal.engine.state_machine import StateMachine
from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent


class RowEventDelivery(Listener[RowEvent]):
    """Every row event, named for its moment, is asked of the top of each live agent's stack in the row's environment, and what each answers is delivered: typed into a main agent's terminal, stored on a worker's row for its next hook; a model's Updated reaches no state."""

    def __init__(self, machine: StateMachine, delivery: Delivery, returns: DecisionReturns) -> None:
        self.machine, self.delivery, self.returns = machine, delivery, returns

    def handle(self, event: RowEvent) -> None:
        for reply in self.machine.row_replies(event):
            self.delivered(reply)

    def delivered(self, reply) -> None:
        self.delivery.applied(reply, 0.0)
        if reply.decision.context:
            self.returns.chosen(reply.bottom_state).row_lines(reply)
