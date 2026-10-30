from tests.stories.builder.story_agent import StoryAgent
import json
from datetime import datetime

from journal.engine.clock import Clock
from journal.support.time_source import TimeSource
from journal.features.shell.jobs.watch_refresh import WatchRefresh
from journal.providers.codex import Codex
from tests.agent_hooks import pass_time, silent_tick
from tests.stories.builder.step_result import StepResult

# the context window a Codex session's rollout reports in a story
STORY_CONTEXT_TOKENS = 200000


class TimeSteps:
    """Time and the context window in a story: the agent quiet for a while, as the clock's tick finds it, the context reaching a share of its window, as the statusline writes it, and a compaction, as the provider's hooks bring it."""

    def agent_is_quiet_for(self, agent: StoryAgent, minutes: float) -> StepResult:
        silent_tick(self.app, minutes * 60)
        return self.observed(f"agent is quiet for {minutes} minutes", None, None)

    def agent_is_quiet_past(self, agent: StoryAgent, seconds: float) -> StepResult:
        return self.silence_tick(str(agent.role), seconds)

    def agent_is_quiet_just_under(self, agent: StoryAgent, seconds: float) -> StepResult:
        silent_tick(self.app, seconds - 1)
        return self.observed(f"agent is quiet just under {seconds} seconds", None, None)

    def silence_tick(self, agent_kind: str, seconds: float) -> StepResult:
        silent_tick(self.app, seconds + 1)
        return self.observed(f"{agent_kind} is quiet past {seconds} seconds", None, None)

    def time_travel(self, seconds: float = 0, minutes: float = 0) -> StepResult:
        pass_time(self.app, seconds + minutes * 60)
        return self.observed(f"the clock moves on {seconds + minutes * 60} seconds", None, None)

    def local_time_after(self, minutes: float) -> str:
        return datetime.fromtimestamp(self.app.container.get(TimeSource).seconds() + minutes * 60).strftime("%Y-%m-%d %H:%M")

    def clock_ticks(self, seconds: float) -> StepResult:
        pass_time(self.app, seconds)
        self.app.runtime().deferred.drain()
        self.app.container.get(Clock).tick(self.app.container.get(Clock).held_at)
        self.app.runtime().deferred.drain()
        return self.observed(f"the clock ticks {seconds} seconds later", None, None)

    def running_commands_are_read_again(self, seconds: float) -> StepResult:
        pass_time(self.app, seconds)
        self.app.container.get(WatchRefresh).tick(self.app.container.get(Clock).held_at)
        self.app.runtime().deferred.drain()
        return self.observed(f"the running commands are read again {seconds} seconds later", None, None)

    def context_reaches(self, percent: int) -> StepResult:
        if self.provider == Codex.name:
            self.rollout_reports_context(self.scoped_session(), percent)
        else:
            self.app.config.status_home.mkdir(parents=True, exist_ok=True)
            (self.app.config.status_home / f"{self.scoped_session()}.json").write_text(json.dumps({"context_window": {"used_percentage": percent}}))
        return self.observed(f"context reaches {percent}%", None, None)

    @staticmethod
    def rollout_reports_context(session: str, percent: int) -> None:
        rollout = Codex.config_folder() / "sessions" / f"rollout-story-{session}.jsonl"
        rollout.parent.mkdir(parents=True, exist_ok=True)
        usage = {"model_context_window": STORY_CONTEXT_TOKENS, "last_token_usage": {"total_tokens": STORY_CONTEXT_TOKENS * percent // 100}}
        with rollout.open("a") as records:
            records.write(json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": usage}}) + "\n")

    def local_moment(self, minutes: float) -> str:
        return datetime.fromtimestamp(self.app.container.get(Clock).held_at + minutes * 60).strftime("%Y-%m-%d %H:%M")

    def main_context_reaches(self, percent: int) -> StepResult:
        self.app.config.status_home.mkdir(parents=True, exist_ok=True)
        (self.app.config.status_home / f"{self.main_session()}.json").write_text(json.dumps({"context_window": {"used_percentage": percent}}))
        return self.observed(f"the main agent's context reaches {percent}%", None, None)

    def agent_consumes_context(self, agent: StoryAgent, percent: int) -> StepResult:
        self.context_reaches(percent)
        return self.agent_reads(agent)

    def subagent_compaction_begins(self, subagent: str) -> StepResult:
        return self.hooked(self.agents.subject, "a subagent's compaction begins", "PreCompact", trigger="auto", agent_id=subagent)

    def compaction_begins(self) -> StepResult:
        return self.hooked(self.agents.subject, "a compaction begins", "PreCompact")

    def compacted_session_starts(self) -> StepResult:
        return self.hooked(self.agents.subject, "context is compacted", "SessionStart", source="compact")

    def context_is_compacted(self) -> StepResult:
        self.compaction_begins()
        return self.compacted_session_starts()
