from journal.engine.clock import Clock
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.compacting import Compacting
from journal.events.agent.journal_returned import JournalReturned
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.subagent_ended import SubagentEnded
from journal.events.agent.subagent_started import SubagentStarted
from journal.events.agent.tool_failed import ToolFailed
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.events.agent.turn_failed import TurnFailed
from journal.config import Config
from journal.support.hook import Hook
from journal.hooks.support.tool_calls import ToolCalls
from journal.hooks.support.turn_gatherer import TurnGatherer
from journal.hooks.tool_uses import ToolUses
from journal.support.hook_type import HookType
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.events.moments.hook_unbound import HookUnbound
from journal.events.moments.session_unbound import SessionUnbound
from journal.providers.providers import Providers
from journal.repositories.entries import Entries


class Translation:
    """Each hook kind to the agent event it means; one table, so no kind is ever read twice in two places."""

    EVENTS = {
        HookType.SESSION_START: lambda hook, calls, agent: SessionStarted(source=hook.source, folder=hook.folder, agent=agent),
        HookType.USER_PROMPT: lambda hook, calls, agent: PromptSubmitted(prompt=hook.text, agent=agent),
        HookType.PRE_TOOL_USE: lambda hook, calls, agent: ToolStarting(call=calls.build(hook), folder=hook.folder, agent=agent),
        HookType.POST_TOOL_USE: lambda hook, calls, agent: ToolFinished(call=calls.build(hook), output=hook.output, response=hook.response, agent=agent),
        HookType.POST_TOOL_USE_FAILURE: lambda hook, calls, agent: ToolFailed(call=calls.build(hook), error=hook.error, agent=agent),
        HookType.PRE_COMPACT: lambda hook, calls, agent: Compacting(agent=agent),
        HookType.STOP: lambda hook, calls, agent: Stop(prior_refusal=hook.stop_refused_earlier, agent=agent),
        HookType.STOP_FAILURE: lambda hook, calls, agent: TurnFailed(error=hook.error, message=hook.assistant_message, agent=agent),
        HookType.SUBAGENT_START: lambda hook, calls, agent: SubagentStarted(subagent=hook.subagent, agent=agent),
        HookType.SUBAGENT_STOP: lambda hook, calls, agent: SubagentEnded(subagent=hook.subagent, report=hook.subagent_report, agent=agent),
        HookType.MESSAGE_DISPLAY: lambda hook, calls, agent: TurnDisplayed(text=hook.text, delta=hook.text, turn_id=hook.turn_id, index=hook.index, final=hook.final, agent=agent),
        HookType.SESSION_END: lambda hook, calls, agent: SessionEnded(agent=agent),
    }

    UNBOUND = {
        HookType.SESSION_START: SessionUnbound,
    }

    def __init__(self, config: Config, providers: Providers, turns: TurnGatherer, entries: Entries, clock: Clock, uses: ToolUses, calls: ToolCalls) -> None:
        self.config, self.providers, self.turns = config, providers, turns
        self.entries, self.clock, self.uses, self.calls = entries, clock, uses, calls

    def event(self, hook: Hook, agent: Agent) -> AgentEvent:
        placed = self.placed(self.EVENTS[hook.hook_type](hook, self.calls, agent), hook, agent)
        return self.turns.fold(self.uses.counted(placed.boot_delayed(hook.boot_wait_seconds).hooked(hook.key())))

    def unbound(self, hook: Hook, environment: Environment) -> HookUnbound:
        return self.UNBOUND.get(hook.hook_type, HookUnbound)(environment_id=environment.row_id, session=hook.session, environment=environment.name)

    def events(self, hook: Hook, agent: Agent) -> tuple[AgentEvent, ...]:
        return (self.returned(hook, agent), self.event(hook, agent)) if hook.silence_start else (self.event(hook, agent),)

    def returned(self, hook: Hook, agent: Agent) -> JournalReturned:
        return self.placed(JournalReturned(silence_start=float(hook.silence_start), agent=agent), hook, agent)

    def placed(self, bare: AgentEvent, hook: Hook, agent: Agent) -> AgentEvent:
        provider = self.providers.lookup(hook.provider)
        return bare.placed(agent, provider.status(hook.session, self.config.status_home).context, self.clock.time(), hook.subagent)
