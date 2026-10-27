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
from journal.references import events


ENTRIES = Query.build(Entry)
DISPATCHES = ENTRIES.filter_alternatives(
    ENTRIES.filter_listed("entry_type", (events.SUBAGENT_STARTED, events.SUBAGENT_ENDED, events.STOP, events.SESSION_STARTED, events.SESSION_ENDED, events.TURN_FAILED)),
    ENTRIES.filter_listed("entry_type", (events.TOOL_STARTING, events.TOOL_FINISHED, events.TOOL_FAILED)).filter_listed("data->call->operation->kind", (SubagentDispatch.operation_type, AgentMessage.operation_type)),
    ENTRIES.filter(entry_type=events.PROMPT_SUBMITTED).filter_prefix("data->prompt", "<task-notification>"),
).inlined()
NUDGE = "nudge"
CUT_KEY = "cut_from"
# the entry a row's deletion is recorded as
DELETED_ENTRY = "deleted"
# the keys of an entry's data that hold what a tool was given and gave back, what a command printed and the agent's last words, which a read of what the agent did leaves out
PAYLOAD_KEYS = ("tool_input", "tool_response", "transcript_path", "output", "last_assistant_message")


# the events of an agent's turn that end a run of held stops, the stop among them
TURN_EVENTS = (events.STOP, events.TOOL_STARTING, events.PROMPT_SUBMITTED)


class Entries(ScopedRepository[Entry]):
    model = Entry

    def trim(self, newest: int, stored: int) -> None:
        self._purged(self.query().filter_less_equal("id", newest - stored).filter_unequal("entry_type", NUDGE))

    def trim_lines(self, stored: int) -> None:
        for boundary in self.selected_globally(self.query().filter(entry_type=NUDGE).order_descending("id").limit(1).offset(stored)):
            self._purged(self.query().filter(entry_type=NUDGE).filter_less_equal("id", boundary.row_id))

    def keyed(self, key: str) -> list[Entry]:
        return self.selected(self.query().filter(idempotency=key).limit(1)) if key else []

    def recorded(self, entry: Entry, actor: Actor) -> Entry:
        with self.writing():
            prior = self.keyed(entry.idempotency)
            return prior[0] if prior else self.save(entry, actor)

    def last_prompt(self, session: str) -> datetime | None:
        rows = self.selected(self.query().filter(entry_type=events.PROMPT_SUBMITTED, actor=Actor.agent(session)).order_descending("id").limit(1))
        return rows[0].created_at if rows else None

    def deletions(self, table: str, id: int) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=DELETED_ENTRY).filter_json("data->table", table).filter_json("data->id", id).order_descending("id").limit(1))

    def agent_lines(self, session: str) -> int:
        return self.counted(self.lines(session))

    def last_line_moment(self, session: str, key: str, line: str) -> Moment | None:
        return self.line_moment(self.lines(session).filter_json("data->key", key).filter_json("data->line", line))

    def last_key_moment(self, session: str, key: str) -> Moment | None:
        return self.line_moment(self.lines(session).filter_json("data->key", key))

    def last_keys_moment(self, session: str, keys: tuple[str, ...]) -> Moment | None:
        return self.line_moment(self.lines(session).filter_listed("data->key", keys))

    def line_moment(self, query: Query) -> Moment | None:
        newest = self.selected(query.with_columns("data").without_keys("data", "line").order_descending("id").limit(1))
        return Moment(seconds=newest[0].data.get("time", 0.0), tool_uses=newest[0].data.get("tool_use", 0)) if newest else None

    def last_lines(self, session: str, key: str) -> float:
        return float(self.maximum(self.lines(session).filter_json("data->key", key), "data->time", 0))

    def tool_starts(self, session: str, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def last_command_lines(self, session: str, count: int) -> list[str]:
        starts = self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).filter_present("data->call->command").filter_unequal("data->call->command", "")
        return [entry.data["call"]["command"] for entry in reversed(self.selected(starts.order_descending("id").limit(count)))]

    def recent_commands(self, session: str, window: int, count: int) -> list[str]:
        starts = self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session))
        oldest = self.selected_ids(starts.order_descending("id").limit(1).offset(window - 1))
        window_starts = starts.filter_greater_equal("id", oldest[0]) if oldest else starts
        commands = window_starts.filter_present("data->call->command").filter_unequal("data->call->command", "")
        first = self.selected_ids(commands.order_descending("id").limit(1).offset(count - 1))
        newest = commands.filter_greater_equal("id", first[0]) if first else commands
        highest, lowest = self.maximum(newest, "data->call->command", ""), self.minimum(newest, "data->call->command", "")
        return [highest] * self.counted(newest) if highest == lowest else [highest, lowest]

    def output_tool_starts(self, session: str, last: int = 500) -> list[Entry]:
        mentions = self.query().filter_alternatives(self.query().filter_containing("data", "outputs/"), self.query().filter_containing("data", "journal output read "))
        return self.selected(mentions.filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def output_reads(self, session: str, output: int, flag: str) -> int:
        reads = self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).filter_containing("data", f"journal output read {output} ").filter_containing("data", flag)
        return self.counted(reads)

    def shape_commands(self, session: str, shape: str, last: int = 200) -> set[str]:
        rows = self.selected(self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).filter_json("data->call->shape", shape).order_descending("id").limit(last))
        return {row.recorded_call().command for row in rows}

    def shape_count(self, session: str, shape: str, last: int = 200) -> int:
        return min(self.counted(self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).filter_json("data->call->shape", shape)), last)

    def newer_shell_starts(self, session: str, earliest: datetime, last: int = 500) -> list[Entry]:
        shell = self.query().filter(entry_type=events.TOOL_STARTING, actor=Actor.agent(session)).filter_present("data->call->command").filter_unequal("data->call->command", "")
        return self.selected(shell.filter_greater("created_at", earliest).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def newer_tool_ends(self, session: str, earliest: datetime, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter_listed("entry_type", (events.TOOL_FINISHED, events.TOOL_FAILED)).filter(actor=Actor.agent(session)).filter_greater("created_at", earliest).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def newer_kind_entries(self, type_name: str, earliest: datetime, last: int = 50) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=type_name).filter_greater("created_at", earliest).order_descending("id").limit(last))

    def newer_session_entries(self, type_name: str, session: str, earliest: datetime, last: int = 50) -> list[Entry]:
        return [entry for entry in self.newer_kind_entries(type_name, earliest, last) if entry.is_session(session)]

    def open_moves(self, moved: str, ended: str) -> list[Entry]:
        chains = list(self.grouped_counts(self.query().filter(entry_type=moved), "data->chain"))
        closed = self.grouped_counts(self.query().filter(entry_type=ended).filter_listed("data->chain", chains), "data->chain") if chains else {}
        open_chains = [chain for chain in chains if chain not in closed]
        return self.selected(self.query().filter(entry_type=moved).filter_listed("data->chain", open_chains).order("id")) if open_chains else []

    def session_activity(self, session: str, part_kinds: tuple[str, ...], tool_kinds: tuple[str, ...], last: int) -> list[Entry]:
        tools = self.query().filter_listed("entry_type", tool_kinds).filter_alternatives(self.query().filter_null("data->call->command"), self.query().filter_json("data->call->command", ""))
        shown = self.query().filter(actor=Actor.agent(session)).filter_alternatives(self.query().filter_listed("entry_type", part_kinds), tools)
        return list(reversed(self.selected(shown.without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))))

    def session_kind_entries(self, type_name: str, session: str) -> list[Entry]:
        return [entry for entry in self.kind_entries(type_name) if entry.is_session(session)]

    def line_entries(self, session: str, line: str) -> list[Entry]:
        return self.selected(self.lines(session).filter_json("data->line", line).order("id"))

    def session_moves(self, kinds: tuple[str, ...], session: str, last: int = 200) -> list[Entry]:
        return [entry for entry in self.kind_entries_scoped(last) if entry.entry_type in kinds and entry.actor and entry.actor.id == session]

    def tool_ends(self, session: str, last: int = 500) -> list[Entry]:
        return self.selected(self.query().filter_listed("entry_type", (events.TOOL_FINISHED, events.TOOL_FAILED)).filter(actor=Actor.agent(session)).order_descending("id").limit(last))

    def last_line_entry(self, session: str, keys: tuple[str, ...]) -> Entry | None:
        rows = self.selected(self.lines(session).filter_listed("data->key", keys).with_columns("data", "created_at").without_keys("data", "line").order_descending("id").limit(1))
        return rows[0] if rows else None

    def refused_stops(self, session: str, count: int) -> list[str]:
        return [entry.data["refused"] for entry in self.selected(self.query().filter(actor=Actor.agent(session), entry_type=events.STOP).filter_present("data->refused").order_descending("id").limit(count))]

    def turn_events(self, session: str, count: int) -> list[Entry]:
        return self.selected(self.turn_query(session).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(count))

    def refusal_run_count(self, session: str, upper_id: int, count_cap: int) -> int:
        turn_entries = self.turn_query(session).filter_less("id", upper_id) if upper_id else self.turn_query(session)
        unrefused = turn_entries.filter_alternatives(self.query().filter_unequal("entry_type", events.STOP), self.query().filter_null("data->refused"))
        run_start = self.selected_ids(unrefused.order_descending("id").limit(1))
        refused = turn_entries.filter(entry_type=events.STOP).filter_present("data->refused")
        return min(self.counted(refused.filter_greater("id", run_start[0]) if run_start else refused), count_cap)

    def turn_query(self, session: str) -> Query:
        return self.query().filter(actor=Actor.agent(session)).filter_listed("entry_type", TURN_EVENTS)

    def line_entries(self, session: str, keys: tuple[str, ...], last: int = 100) -> list[Entry]:
        return self.selected(self.lines(session).filter_listed("data->key", keys).order_descending("id").limit(last))

    def recent_lines(self, session: str, key: str, entry_id: int) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_json("data->key", key).filter_greater("id", entry_id).order("id"))]

    def environment_values(self, key: str, name: str) -> list[str]:
        return [entry.data["values"][name] for entry in self.selected(self.query().filter(entry_type=NUDGE).filter_json("data->key", key).filter_present("data->values").order("id"))]

    def project_values(self, key: str, name: str) -> dict[str, float]:
        return {entry.data["values"][name]: entry.data["time"] for entry in self.selected_globally(self.query().filter(entry_type=NUDGE).filter_json("data->key", key).filter_present("data->values").order("id"))}

    def keyed_lines(self, session: str, keys: tuple[str, ...]) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_listed("data->key", keys).order("id"))]

    def use_lines(self, session: str, key: str, tool_use: int) -> list[str]:
        return [e.data["line"] for e in self.selected(self.lines(session).filter_json("data->key", key).filter_greater("data->tool_use", tool_use).order("id"))]

    def nudge_count(self, session: str, keys: tuple[str, ...], tool_use: int) -> int:
        return self.counted(self.lines(session).filter_listed("data->key", keys).filter_greater_equal("data->tool_use", tool_use))

    def last_kind_id(self, session: str, type_name: str) -> int:
        return self.maximum(self.query().filter(entry_type=type_name, actor=Actor.agent(session)), "id", 0)

    def recent_line_entries(self, session: str, key: str) -> int:
        newest = self.maximum(self.lines(session).filter_json("data->key", key), "id", 0)
        return self.counted(self.lines(session).filter_greater("id", newest))

    def nudge_tallies(self, cutoff: datetime) -> list[NudgeTally]:
        query = self.query().filter(entry_type=NUDGE).filter_greater("created_at", cutoff)
        return [NudgeTally(row["value0"], row["value1"], row["total"], row["latest"]) for row in self.tallied_globally(query, ("data->session", "data->key"), "data->time")]

    def kind_entries(self, type_name: str, last: int = 50) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=type_name).order_descending("id").limit(last))

    def undelivered_lines(self, type_name: str, session: str) -> list[Entry]:
        return [entry for entry in self.selected(self.query().filter(entry_type=type_name).filter_json("data->session", session).order_descending("id").limit(200)) if not entry.data.get("delivered")]

    def agent_kinds_newest(self, session: str, kinds: Sequence[str], last: int) -> list[Entry]:
        return self.selected(self.query().filter(actor=Actor.agent(session)).filter_listed("entry_type", list(kinds)).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def session_kind_newest(self, session: str, type_name: str, last: int) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=type_name).filter_json("data->session", session).without_keys("data", *PAYLOAD_KEYS).order_descending("id").limit(last))

    def kind_entries_scoped(self, last: int = 400) -> list[Entry]:
        return self.selected(self.query().order_descending("id").limit(last))

    def actor_entries(self, stamp: str, last: int = 200) -> list[Entry]:
        return self.selected_globally(self.query().filter(actor=stamp).order_descending("id").limit(last))

    def last_session_entry(self, session: str) -> Entry | None:
        rows = self.selected(self.query().filter(actor=Actor.agent(session)).filter_unequal("entry_type", NUDGE).order_descending("id").limit(1))
        return rows[0] if rows else None

    def final_message(self, session: str) -> str:
        stops = self.selected(self.query().filter(entry_type=events.STOP, actor=Actor.agent(session)).order_descending("id").limit(1))
        return stops[0].data.get("last_assistant_message", "") if stops else ""

    def last_id(self) -> int:
        return self.maximum(self.query(), "id", 0)

    def global_last_id(self) -> int:
        return self.maximum_globally(self.query(), "id", 0)

    def dispatches(self, session: str) -> list[Entry]:
        return self.selected(DISPATCHES.filter_json("data->session_id", session).order("id"))

    def subagent_ends(self, session: str, subagent: str) -> list[Entry]:
        return self.selected(ENTRIES.filter(entry_type=events.SUBAGENT_ENDED).filter_json("data->session_id", session).filter_json("data->agent_id", subagent).order("id"))

    def global_dispatches(self) -> list[Entry]:
        return self.selected_globally(DISPATCHES.order("id"))

    def agent_calls(self, last: int = 500) -> list[Entry]:
        return self.selected(DISPATCHES.filter(entry_type=events.TOOL_STARTING).order_descending("id").limit(last))

    def recent_shown(self, id: int, kinds: Sequence[str]) -> list[Entry]:
        return self.with_project(self.shown_query(kinds).filter_greater("id", id).order("id"))

    def shown_recent(self, last: int, kinds: Sequence[str]) -> list[Entry]:
        return self.with_project(self.shown_query(kinds).order_descending("id").limit(last))

    def shown_query(self, kinds: Sequence[str]) -> Query:
        return self.query().filter_listed("entry_type", sorted(kinds)).without_keys("data", *PAYLOAD_KEYS)

    def recent(self, id: int) -> list[Entry]:
        return self.selected(self.query().filter_greater("id", id).order("id"))

    def newer_tool_starts(self, id: int) -> list[Entry]:
        return self.selected(self.query().filter_greater("id", id).filter(entry_type=events.TOOL_STARTING).order("id"))

    def key_lines(self, key: str) -> list[str]:
        return [str(entry.data["line"]) for entry in self.selected(self.query().filter(entry_type=NUDGE).filter_json("data->key", key))]

    def cut_lines(self) -> list[Entry]:
        return self.selected(self.query().filter(entry_type=NUDGE).filter_present(f"data->{CUT_KEY}").order("id"))

    def lines(self, session: str) -> Query:
        return self.query().filter(entry_type=NUDGE).filter_json("data->session", session)

    def _placed(self, row: Entry) -> Entry:
        return row

    def clear(self) -> None:
        self._purged(self.query())
