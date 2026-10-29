from journal.events.agent.agent_event_type import AgentEventType
from journal.support.hook_type import HookType

# the one place the names of hooks and agent events are written: code reads hooks.PRE_TOOL_USE or events.TOOL_STARTING, never the name as a string
hooks = HookType
events = AgentEventType
