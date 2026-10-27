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
from journal.models.environment import Environment
from journal.providers.providers import Providers
from journal.repositories.entries import Entries


class Translation:
    """Each hook kind to the agent event it means; one table, so no kind is ever read twice in two places."""

    EVENTS = {
        HookType.SESSION_START: lambda hook, calls: SessionStarted(source=hook.source, folder=hook.folder),
        HookType.USER_PROMPT: lambda hook, calls: PromptSubmitted(prompt=hook.text),
        HookType.PRE_TOOL_USE: lambda hook, calls: ToolStarting(call=calls.build(hook), folder=hook.folder),
        HookType.POST_TOOL_USE: lambda hook, calls: ToolFinished(call=calls.build(hook), output=hook.output, response=hook.response),
        HookType.POST_TOOL_USE_FAILURE: lambda hook, calls: ToolFailed(call=calls.build(hook), error=hook.error),
        HookType.PRE_COMPACT: lambda hook, calls: Compacting(),
        HookType.STOP: lambda hook, calls: Stop(prior_refusal=hook.stop_refused_earlier),
        HookType.STOP_FAILURE: lambda hook, calls: TurnFailed(error=hook.error, message=hook.assistant_message),
        HookType.SUBAGENT_START: lambda hook, calls: SubagentStarted(subagent=hook.subagent),
        HookType.SUBAGENT_STOP: lambda hook, calls: SubagentEnded(subagent=hook.subagent, report=hook.subagent_report),
        HookType.MESSAGE_DISPLAY: lambda hook, calls: TurnDisplayed(text=hook.text, delta=hook.text, turn_id=hook.turn_id, index=hook.index, final=hook.final),
        HookType.SESSION_END: lambda hook, calls: SessionEnded(),
    }

    def __init__(self, config: Config, providers: Providers, turns: TurnGatherer, entries: Entries, clock: Clock, uses: ToolUses, calls: ToolCalls) -> None:
        self.config, self.providers, self.turns = config, providers, turns
        self.entries, self.clock, self.uses, self.calls = entries, clock, uses, calls

    def event(self, hook: Hook, environment: Environment) -> AgentEvent:
        placed = self.placed(self.EVENTS[hook.kind](hook, self.calls), hook, environment)
        return self.turns.fold(self.uses.counted(placed.boot_delayed(hook.boot_wait_seconds).hooked(hook.key())))

    def returned(self, hook: Hook, environment: Environment) -> JournalReturned:
        return self.placed(JournalReturned(silence_start=hook.silence_start), hook, environment)

    def placed(self, bare: AgentEvent, hook: Hook, environment: Environment) -> AgentEvent:
        provider = self.providers.lookup(hook.provider)
        return bare.placed(hook.session, environment.row_id, hook.provider, provider.status(hook.session, self.config.status_home).context, self.clock.time(), hook.subagent)
