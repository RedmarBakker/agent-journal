from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.assigner_index import AssignerIndex
from journal.engine.task_assigner import TaskAssigner
from journal.models.agent import Agent


class AssignerResolution:
    """The task assigner in force for an agent: the one named by the state closest to the top of its stack that names one; the floor of every role names one."""

    def __init__(self, states: StatesCatalogue, index: AssignerIndex) -> None:
        self.states, self.index = states, index

    def resolved(self, agent: Agent) -> TaskAssigner:
        for state in reversed(self.states.stack(agent).states):
            if state.assigner is not None:
                return self.index.instance(state.assigner)
        return self.index.instance(NoTaskAssigner)
