from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.session_agents import SessionAgents
from journal.models.report import Report
from journal.repositories.entries import Entries
from journal.repositories.reports import Reports
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.caller import Caller
from journal.version import VERSION

# the newest refused stops a report quotes
REFUSAL_COUNT = 10


class PanicReport:
    """What refused an agent's stops, written as a report in the journal: the lines that refused its newest stops, its state stack from the bottom, each unclosed task's number and state, never its title, and the journal's version."""

    def __init__(self, sessions: SessionAgents, states: StatesCatalogue, entries: Entries, tasks: Tasks, reports: Reports, scope: Scope) -> None:
        self.sessions, self.states, self.entries, self.tasks, self.reports, self.scope = sessions, states, entries, tasks, reports, scope

    def report(self, caller: Caller) -> Report:
        agent = self.sessions.agent(caller.agent_session, self.scope.id)
        stack_text = ", ".join(state.state_text() for state in self.states.stack(agent).states)
        refusal_text = "\n".join(f"- {' '.join(line.split())}" for line in self.entries.refused_stops(agent.session, REFUSAL_COUNT)) or "- none recorded"
        task_text = "\n".join(f"- task {task.id}: {task.state}" for task in self.tasks.unclosed_tasks()) or "- none"
        body = f"## What held the stops\n\n{refusal_text}\n\n## The state stack, bottom to top\n\n{stack_text}\n\n## Unclosed tasks\n\n{task_text}\n\n## Version\n\n{VERSION}\n"
        return self.reports.save(Report(title=f"Stops held in a loop on {VERSION}", abstract="the lines that held the agent's stops, its state stack and its tasks' states", body=body), caller.actor)
