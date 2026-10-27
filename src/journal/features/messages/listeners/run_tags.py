from journal.features.messages.messages_nudges import MessagesNudges
from journal.engine.support.session_agents import SessionAgents
from journal.engine.nudger import Nudger
from journal.console.console import Console
from journal.support.caller import Caller
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.events.agent_listener import AgentListener
from journal.features.messages.support.tags import Tags
from journal.repositories.environments import Environments
from journal.supervisor_link import SupervisorLink

RUNS = {
    "todo": ("task", "create", "{name}", "--brief", "{text}"),
    "log": ("task", "log", "{n}", "{text}"),
    "end": ("task", "complete", "{n}", "--how", "{text}"),
    "memory": ("memory", "add", "{name}"),
    "rule": ("rule", "create", "{name}", "--reason", "{text}"),
    "reminder": ("reminder", "create", "{name}", "--reason", "{text}"),
}


class RunTags(AgentListener[TurnDisplayed]):
    """A tag opening a line of the turn runs the command it stands for, with the turn's text as its text: [!todo="the title"] files a task with the turn as its brief, [!log:N] makes the turn the log line, [!end:N] the outcome, [!memory="what to keep in mind"] the fact's reason. A refusal is typed back; the reply tag belongs to the recorder."""

    def __init__(self, console: Console, environments: Environments, supervisor: SupervisorLink, nudger: Nudger, sessions: SessionAgents) -> None:
        self.nudger, self.sessions = nudger, sessions
        self.console, self.environments, self.supervisor = console, environments, supervisor

    def handle(self, event: TurnDisplayed) -> None:
        if not event.final:
            return
        text = Tags.visible(event.text)
        caller = Caller.agent(self.environments.find(event.environment_id).name, event.session, event.provider)
        for name, numbers, argument in Tags.tags(event.text):
            if name not in RUNS:
                continue
            argv = [word.format(name=argument, n=numbers, text=text) for word in RUNS[name]]
            outcome = self.console.run(argv, caller)
            if outcome.code:
                line = self.nudger.deliver(self.sessions.agent(event.session, event.environment_id), MessagesNudges.TAG_FAILURE.create(name=name, reason=(outcome.error or outcome.text).strip().splitlines()[-1]))
                if line:
                    self.supervisor.type(event.environment_id, line)
