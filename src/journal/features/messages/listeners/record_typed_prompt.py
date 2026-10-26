from datetime import datetime, timezone

from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.message import TERMINAL_LINE, Message
from journal.repositories.messages import Messages
from journal.repositories.scheduled_jobs import ScheduledJobs
from journal.support.typed_lines import TypedLines
from journal.sync.team_account import TeamAccount
from journal.support.time_source import TimeSource

# the least time between two arrivals of the same words for them to be a schedule's, not the user typing them again
SCHEDULE_SECONDS = 60


class RecordTypedPrompt(AgentListener[PromptSubmitted]):
    """What the user types in the agent's terminal reaches the chat as their message, already read by the agent it was typed to; the journal's own lines stay out, and a prompt the session's own scheduler sent, the prompt of one of its running jobs, or words that repeat an earlier prompt exactly at least a minute later, is the system's scheduled prompt, never a user message waiting on an answer; the earlier arrivals of those words become scheduled prompts too."""

    def __init__(self, messages: Messages, lines: TypedLines, account: TeamAccount, jobs: ScheduledJobs, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.account, self.jobs = account, jobs
        self.messages, self.lines = messages, lines

    def handle(self, event: PromptSubmitted) -> None:
        if not event.is_users or not event.prompt.strip() or self.lines.contains(event.environment_id, event.prompt):
            return
        text, now = event.prompt.strip(), self.time_source.moment()
        earlier = self.messages.prompt_repeats(text)
        if self.is_scheduled(event.session, text, now.timestamp()) or any(now.timestamp() - message.creation_time.timestamp() >= SCHEDULE_SECONDS for message in earlier):
            for message in earlier:
                if not message.is_scheduled_prompt:
                    self.messages.save(message.scheduled(), Actor.system())
            self.messages.save(Message(text=text, read_at=now).scheduled(), Actor.system())
            return
        self.messages.save(Message(author=Author.USER, text=text, read_at=now, data={"kind": TERMINAL_LINE}), Actor.user(self.account.user_number()))

    def is_scheduled(self, session: str, text: str, moment: float) -> bool:
        return any(job.prompt.strip() == text and job.is_running(moment) for job in self.jobs.session_jobs(session))
