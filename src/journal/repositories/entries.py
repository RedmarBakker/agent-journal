from collections.abc import Sequence
from datetime import datetime

from journal.support.moment import Moment
from journal.db.query import Query
from journal.models.entry import Entry
from journal.models.support.nudge_tally import NudgeTally
from journal.support.actor import Actor
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.agent_message import AgentMessage
from journal.support.subagent_dispatch import SubagentDispatch


ENTRIES = Query.build(Entry)
DISPATCHES = ENTRIES.filter_alternatives(
    ENTRIES.filter_listed("kind", ("SubagentStarted", "SubagentEnded", "Stop", "SessionStarted", "SessionEnded", "TurnFailed")),
    ENTRIES.filter_listed("kind", ("ToolStarting", "ToolFinished", "ToolFailed")).filter_listed("data->call->operation->kind", (SubagentDispatch.operation_type, AgentMessage.operation_type)),
    ENTRIES.filter(kind="PromptSubmitted").filter_prefix("data->prompt", "<task-notification>"),
).inlined()
NUDGE = "nudge"
# the keys of an entry's data that hold what a tool was given and gave back, what a command printed and the agent's last words, which a read of what the agent did leaves out
PAYLOAD_KEYS = ("tool_input", "tool_response", "transcript_path", "output", "last_assistant_message")


# the events of an agent's turn that end a run of held stops, the stop among them
TURN_EVENTS = ("Stop", "ToolStarting", "PromptSubmitted")


class Entries(ScopedRepository[Entry]):
    model = Entry

    def trim(self, newest: int, stored: int) -> None:
        self._purged(self.query().filter_less_equal("id", newest - stored).filter_unequal("kind", NUDGE))

    def trim_lines(self, stored: int) -> None:
        for boundary in self.selected_globally(self.query().filter(kind=NUDGE).order_descending("id").limit(1).offset(stored)):
            self._purged(self.query().filter(kind=NUDGE).filter_less_equal("id", boundary.row_id))

    def keyed(self, key: str) -> list[Entry]:
        return self.selected(self.query().filter(idempotency=key).limit(1)) if key else []

    def recorded(self, entry: Entry, actor: Actor) -> Entry:
        with self.writing():
            prior = self.keyed(entry.idempotency)
            return prior[0] if prior else self.save(entry, actor)

    def last_prompt(self, session: str) -> datetime | None:
        rows = self.selected(self.query().filter(kind="PromptSubmitted", actor=Actor.agent(session)).order_descending("id").limit(1))
        return rows[0].created_at if rows else None

    def agent_lines(self, session: str) -> int:
        return self.counted(self.lines(session))

    def last_line_moment(self, session: str, key: str, line: str) -> Moment | None:
        return self.line_moment(self.lines(session).filter_json("data->key", key).filter_json("data->line", line))

    def last_key_moment(self, session: str, key: str) -> Moment | None:
        return self.line_moment(self.lines(session).filter_json("data->key", key))

    def line_moment(self, query: Query) -> Moment | None:
        newest = self.selected(query.with_columns("data").without_keys("data", "line").order_descending("id").limit(1))
        return Moment(seconds=newest[0].data.get("time", 0.0), tool_uses=newest[0].data.get("tool_use", 0)) if newest else None

    def last_lines(self, session: str, key: str) -> float:
        return float(self.maximum(self.lines(session).filter_json("data->key", key), "data->time", 0))

    def tool_starts(self, session: str, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter(kind="ToolStarting", actor=Actor.agent(session)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def recent_commands(self, session: str, window: int, count: int) -> list[str]:
        starts = self.query().filter(kind="ToolStarting", actor=Actor.agent(session))
        oldest = self.selected_ids(starts.order_descending("id").limit(1).offset(window - 1))
        window_starts = starts.filter_greater_equal("id", oldest[0]) if oldest else starts
        commands = window_starts.filter_present("data->call->command").filter_unequal("data->call->command", "")
        first = self.selected_ids(commands.order_descending("id").limit(1).offset(count - 1))
        newest = commands.filter_greater_equal("id", first[0]) if first else commands
        highest, lowest = self.maximum(newest, "data->call->command", ""), self.minimum(newest, "data->call->command", "")
        return [highest] * self.counted(newest) if highest == lowest else [highest, lowest]

    def output_tool_starts(self, session: str, last: int = 500) -> list[Entry]:
        mentions = self.query().filter_alternatives(self.query().filter_containing("data", "outputs/"), self.query().filter_containing("data", "journal output read "))
        return self.selected(mentions.filter(kind="ToolStarting", actor=Actor.agent(session)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def output_reads(self, session: str, output: int, flag: str) -> int:
        reads = self.query().filter(kind="ToolStarting", actor=Actor.agent(session)).filter_containing("data", f"journal output read {output} ").filter_containing("data", flag)
        return self.counted(reads)

    def shape_commands(self, session: str, shape: str, last: int = 200) -> set[str]:
        rows = self.selected(self.query().filter(kind="ToolStarting", actor=Actor.agent(session)).filter_json("data->call->shape", shape).order_descending("id").limit(last))
        return {row.recorded_call().command for row in rows}

    def shape_count(self, session: str, shape: str, last: int = 200) -> int:
        return min(self.counted(self.query().filter(kind="ToolStarting", actor=Actor.agent(session)).filter_json("data->call->shape", shape)), last)

    def newer_shell_starts(self, session: str, earliest: datetime, last: int = 500) -> list[Entry]:
        shell = self.query().filter(kind="ToolStarting", actor=Actor.agent(session)).filter_present("data->call->command").filter_unequal("data->call->command", "")
        return self.selected(shell.filter_greater("created_at", earliest).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def newer_tool_ends(self, session: str, earliest: datetime, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter_listed("kind", ("ToolFinished", "ToolFailed")).filter(actor=Actor.agent(session)).filter_greater("created_at", earliest).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def newer_kind_entries(self, kind: str, earliest: datetime, last: int = 50) -> list[Entry]:
        return self.selected(self.query().filter(kind=kind).filter_greater("created_at", earliest).order_descending("id").limit(last))

    def newer_session_entries(self, kind: str, session: str, earliest: datetime, last: int = 50) -> list[Entry]:
        return [entry for entry in self.newer_kind_entries(kind, earliest, last) if entry.is_session(session)]

    def open_moves(self, moved: str, ended: str) -> list[Entry]:
        chains = list(self.grouped_counts(self.query().filter(kind=moved), "data->chain"))
        closed = self.grouped_counts(self.query().filter(kind=ended).filter_listed("data->chain", chains), "data->chain") if chains else {}
        open_chains = [chain for chain in chains if chain not in closed]
        return self.selected(self.query().filter(kind=moved).filter_listed("data->chain", open_chains).order("id")) if open_chains else []

    def session_activity(self, session: str, part_kinds: tuple[str, ...], tool_kinds: tuple[str, ...], last: int) -> list[Entry]:
        tools = self.query().filter_listed("kind", tool_kinds).filter_alternatives(self.query().filter_null("data->call->command"), self.query().filter_json("data->call->command", ""))
        shown = self.query().filter(actor=Actor.agent(session)).filter_alternatives(self.query().filter_listed("kind", part_kinds), tools)
        return list(reversed(self.selected(shown.without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))))

    def session_kind_entries(self, kind: str, session: str) -> list[Entry]:
        return [entry for entry in self.kind_entries(kind) if entry.is_session(session)]

    def line_entries(self, session: str, line: str) -> list[Entry]:
        return self.selected(self.lines(session).filter_json("data->line", line).order("id"))

    def session_moves(self, kinds: tuple[str, ...], session: str, last: int = 200) -> list[Entry]:
        return [entry for entry in self.kind_entries_scoped(last) if entry.kind in kinds and entry.actor and entry.actor.id == session]

    def tool_ends(self, session: str, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter_listed("kind", ("ToolFinished", "ToolFailed")).filter(actor=Actor.agent(session)).order_descending("id").limit(last))

    def last_line_entry(self, session: str, keys: tuple[str, ...]) -> Entry | None:
        rows = self.selected(self.lines(session).filter_listed("data->key", keys).with_columns("data", "created_at").without_keys("data", "line").order_descending("id").limit(1))
        return rows[0] if rows else None

    def refused_stops(self, session: str, count: int) -> list[str]:
        return [entry.data["refused"] for entry in self.selected(self.query().filter(actor=Actor.agent(session), kind="Stop").filter_present("data->refused").order_descending("id").limit(count))]

    def turn_events(self, session: str, count: int) -> list[Entry]:
        return self.selected(self.turn_query(session).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(count))

    def refusal_run_count(self, session: str, upper_id: int, count_cap: int) -> int:
        events = self.turn_query(session).filter_less("id", upper_id) if upper_id else self.turn_query(session)
        unrefused = events.filter_alternatives(self.query().filter_unequal("kind", "Stop"), self.query().filter_null("data->refused"))
        run_start = self.selected_ids(unrefused.order_descending("id").limit(1))
        refused = events.filter(kind="Stop").filter_present("data->refused")
        return min(self.counted(refused.filter_greater("id", run_start[0]) if run_start else refused), count_cap)

    def turn_query(self, session: str) -> Query:
        return self.query().filter(actor=Actor.agent(session)).filter_listed("kind", TURN_EVENTS)

    def line_entries(self, session: str, keys: tuple[str, ...], last: int = 100) -> list[Entry]:
        return self.selected(self.lines(session).filter_listed("data->key", keys).order_descending("id").limit(last))

    def recent_lines(self, session: str, key: str, entry_id: int) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_json("data->key", key).filter_greater("id", entry_id).order("id"))]

    def environment_values(self, key: str, name: str) -> list[str]:
        return [entry.data["values"][name] for entry in self.selected(self.query().filter(kind=NUDGE).filter_json("data->key", key).order("id"))]

    def project_values(self, key: str, name: str) -> dict[str, float]:
        return {entry.data["values"][name]: entry.data["time"] for entry in self.selected_globally(self.query().filter(kind=NUDGE).filter_json("data->key", key).order("id"))}

    def keyed_lines(self, session: str, keys: tuple[str, ...]) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_listed("data->key", keys).order("id"))]

    def use_lines(self, session: str, key: str, tool_use: int) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_json("data->key", key).filter_greater("data->tool_use", tool_use).order("id"))]

    def nudge_count(self, session: str, keys: tuple[str, ...], tool_use: int) -> int:
        return self.counted(self.lines(session).filter_listed("data->key", keys).filter_greater_equal("data->tool_use", tool_use))

    def last_kind_id(self, session: str, kind: str) -> int:
        return self.maximum(self.query().filter(kind=kind, actor=Actor.agent(session)), "id", 0)

    def recent_line_entries(self, session: str, key: str) -> int:
        newest = self.maximum(self.lines(session).filter_json("data->key", key), "id", 0)
        return self.counted(self.lines(session).filter_greater("id", newest))

    def nudge_tallies(self, cutoff: datetime) -> list[NudgeTally]:
        query = self.query().filter(kind=NUDGE).filter_greater("created_at", cutoff)
        return [NudgeTally(row["value0"], row["value1"], row["total"], row["latest"]) for row in self.tallied_globally(query, ("data->session", "data->key"), "data->time")]

    def kind_entries(self, kind: str, last: int = 50) -> list[Entry]:
        return self.selected(self.query().filter(kind=kind).order_descending("id").limit(last))

    def undelivered_lines(self, kind: str, session: str) -> list[Entry]:
        return [entry for entry in self.selected(self.query().filter(kind=kind).filter_json("data->session", session).order_descending("id").limit(200)) if not entry.data.get("delivered")]

    def agent_kinds_newest(self, session: str, kinds: Sequence[str], last: int) -> list[Entry]:
        return self.selected(self.query().filter(actor=Actor.agent(session)).filter_listed("kind", list(kinds)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def session_kind_newest(self, session: str, kind: str, last: int) -> list[Entry]:
        return self.selected(self.query().filter(kind=kind).filter_json("data->session", session).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def kind_entries_scoped(self, last: int = 400) -> list[Entry]:
        return self.selected(self.query().order_descending("id").limit(last))

    def actor_entries(self, stamp: str, last: int = 200) -> list[Entry]:
        return self.selected_globally(self.query().filter(actor=stamp).order_descending("id").limit(last))

    def last_session_entry(self, session: str) -> Entry | None:
        rows = self.selected(self.query().filter(actor=Actor.agent(session)).filter_unequal("kind", NUDGE).order_descending("id").limit(1))
        return rows[0] if rows else None

    def final_message(self, session: str) -> str:
        stops = self.selected(self.query().filter(kind="Stop", actor=Actor.agent(session)).order_descending("id").limit(1))
        return stops[0].data.get("last_assistant_message", "") if stops else ""

    def last_id(self) -> int:
        return self.maximum(self.query(), "id", 0)

    def global_last_id(self) -> int:
        return self.maximum_globally(self.query(), "id", 0)

    def dispatches(self, session: str) -> list[Entry]:
        return self.selected(DISPATCHES.filter_json("data->session_id", session).order("id"))

    def subagent_ends(self, session: str, subagent: str) -> list[Entry]:
        return self.selected(ENTRIES.filter(kind="SubagentEnded").filter_json("data->session_id", session).filter_json("data->agent_id", subagent).order("id"))

    def global_dispatches(self) -> list[Entry]:
        return self.selected_globally(DISPATCHES.order("id"))

    def agent_calls(self, last: int = 500) -> list[Entry]:
        return self.selected(DISPATCHES.filter(kind="ToolStarting").order_descending("id").limit(last))

    def recent_shown(self, id: int, kinds: Sequence[str]) -> list[Entry]:
        return self.with_project(self.shown_query(kinds).filter_greater("id", id).order("id"))

    def shown_recent(self, last: int, kinds: Sequence[str]) -> list[Entry]:
        return self.with_project(self.shown_query(kinds).order_descending("id").limit(last))

    def shown_query(self, kinds: Sequence[str]) -> Query:
        return self.query().filter_listed("kind", sorted(kinds)).without_keys("data", *PAYLOAD_KEYS)

    def recent(self, id: int) -> list[Entry]:
        return self.selected(self.query().filter_greater("id", id).order("id"))

    def key_lines(self, key: str) -> list[str]:
        return [str(entry.data["line"]) for entry in self.selected(self.query().filter(kind=NUDGE).filter_json("data->key", key))]

    def lines(self, session: str) -> Query:
        return self.query().filter(kind=NUDGE).filter_json("data->session", session)

    def _placed(self, row: Entry) -> Entry:
        return row

    def clear(self) -> None:
        self._purged(self.query())
