from functools import partial

from journal.events.listener import Listener
from journal.events.stack_moved import StackMoved
from journal.repositories.state_transitions import StateTransitions
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue


class TransitionCounts(Listener[StackMoved]):
    """Each move of a stack adds one to the count of its kind, on the deferred worker after the hook has answered."""

    def __init__(self, deferred: ListenerQueue, transitions: StateTransitions) -> None:
        self.deferred, self.transitions = deferred, transitions

    def handle(self, event: StackMoved) -> None:
        self.deferred.add(partial(self.counted, event))

    def counted(self, event: StackMoved) -> None:
        self.transitions.counted(event.before_state, event.after_state, event.cause, event.at, Actor.system())
