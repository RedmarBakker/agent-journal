import json
from dataclasses import asdict, fields
from datetime import datetime, timezone

from journal.events.agent.agent_event import AgentEvent
from journal.events.event import Event
from journal.support.tool_call import ToolCall
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.features.plugins.support.plugin_fault import PluginFault
from journal.features.plugins.support.plugin_answer import PluginAnswer
from journal.features.plugins.support.plugin_card import PluginCard
from journal.support.time_source import TimeSource

ANSWERS = ("allow", "refuse", "tell")
ANSWER_COMMANDS = 20
PLACED = ("session", "environment_id", "bound_environment_ids", "provider", "context", "subagent", "time", "data", "propagation")
EVENT_NAMES = {"stop": "idle", "edit_overridden": "edit_kept", "plugin_recovered": "plugin_answering", "plugin_card_requested": "plugin_card_asked", "plugin_upgrade_failed": "plugin_not_upgraded",
               "plugin_disabled": "plugin_switched_off", "search_completed": "search_made", "shared_comment_posted": "shared_comment_left"}
ANSWER_FIELDS = {"tell": "message"}
FIELD_NAMES = {"prior_refusal": "held_before", "silence_seconds": "quiet_for", "edited_paths": "written_paths", "field_value": "kept", "menu_choice": "done", "explanation": "why"}


class Protocol:
    """The one line the journal sends a plugin for an event, and the one line it reads back: JSON both ways, versioned. An event and its fields go by their names, or by the published names plugins already read where the journal renamed them."""

    VERSION = 1

    def __init__(self, time_source: TimeSource) -> None:
        self.time_source = time_source

    @staticmethod
    def published_name(event: Event) -> str:
        return EVENT_NAMES.get(event.key, event.key)

    def event_line(self, event: Event, environment: str, state: str = "") -> str:
        line = {"v": self.VERSION, "event": self.published_name(event), "at": self.time_source.moment().isoformat(), "environment": environment, "state": state, "data": self.event_data(event)}
        if isinstance(event, AgentEvent):
            line |= {"session": event.session, "provider": event.provider, "subagent": event.subagent}
        return json.dumps(line, default=str)

    @staticmethod
    def event_data(event: Event) -> dict:
        if isinstance(event, ModelEvent):
            row = {"table": event.model.table(), "id": event.model.id, "by": event.actor.stamp}
            return row | {"changed": list(event.changed())} if isinstance(event, Updated) else row
        data: dict[str, object] = {}
        for name, value in ((f.name, getattr(event, f.name)) for f in fields(event) if f.name not in PLACED):
            data |= {**asdict(value), "operation": value.operation.as_data()} if isinstance(value, ToolCall) else {name: value}
        return {FIELD_NAMES.get(name, name): value for name, value in data.items()}

    @staticmethod
    def line_status(text: str) -> str:
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            return ""
        return str(raw.get("status", "")).strip() if isinstance(raw, dict) else ""

    def parsed_answer(self, text: str) -> PluginAnswer:
        if not text.strip():
            return PluginAnswer()
        try:
            raw = json.loads(text.strip().splitlines()[-1])
        except json.JSONDecodeError as broken:
            raise PluginFault(f"its answer is not JSON: {broken}") from broken
        if not isinstance(raw, dict):
            raise PluginFault("its answer is not a JSON object")
        raw = {ANSWER_FIELDS.get(key, key): value for key, value in raw.items()}
        answer_fields = {f.name for f in fields(PluginAnswer)} - {"ignored"}
        answer = PluginAnswer(**{**{key: value for key, value in raw.items() if key in answer_fields}, "ignored": tuple(sorted(set(raw) - answer_fields)), "cards": tuple(PluginCard.parsed(card) for card in raw.get("cards", ())), "commands": tuple(raw.get("commands", ()))})
        if answer.answer not in ANSWERS:
            raise PluginFault(f"it answered {answer.answer!r}; an answer is allow, refuse or tell")
        if answer.v != self.VERSION:
            raise PluginFault(f"it answered in protocol {answer.v}; this journal speaks {self.VERSION}")
        if len(answer.commands) > ANSWER_COMMANDS:
            raise PluginFault(f"it asked for {len(answer.commands)} commands; one answer runs at most {ANSWER_COMMANDS}")
        return answer
