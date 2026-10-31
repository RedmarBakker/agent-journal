from journal.support.large_reads import LargeReads
from journal.support.query_times import QueryTimes
from journal.support.stage_times import StageTimes
from datetime import datetime, timezone
from journal.events.announcer import Announcer
from journal.config import Config
from journal.support.masks import Masks
from journal.support.secret_values import SecretValues
"""Phase one: a task is created, linked, updated and deleted in a real database, and every model event is heard with its actor."""

import json
import threading

import pytest

from journal.db.query import Query
from tests.old_columns import kind_columns
from journal.db.unknown_column import UnknownColumn
from journal.events.models.created import Created
from journal.events.models.creating import Creating
from journal.events.models.deleted import Deleted
from journal.events.models.model_event import ModelEvent
from journal.events.models.saved import Saved
from journal.events.models.saving import Saving
from journal.events.models.updated import Updated
from journal.events.models.updating import Updating
from journal.events.listener import Listener
from journal.features.listeners.unlink_deleted import UnlinkDeleted
from journal.support.rejection import Rejection
from journal.support.actor import Actor
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.links import Links
from journal.repositories.agents import Agents
from journal.repositories.users import Users
from journal.support.missing_row import MissingRow
from journal.repositories.checks import Checks
from journal.repositories.questions import Questions
from journal.repositories.tasks import Tasks
from journal.repositories.phases import Phases
from journal.repositories.plans import Plans
from journal.repositories.rows import Rows
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.support.scope_missing import ScopeMissing
from journal.features.voices.voices_options import VoicesOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.support.time_source import TimeSource

USER = Actor.user(1)
AGENT = Actor.agent("abc")


class Heard(Listener[ModelEvent]):
    def __init__(self):
        self.events = []

    def handle(self, event):
        self.events.append(event)


def tasks_of(connection, bus, scope) -> Tasks:
    time_source = TimeSource()
    return Tasks(connection, bus, scope, Links(connection, bus, time_source), Questions(connection, bus, scope, time_source), Checks(connection, bus, time_source), time_source, Rows(connection), Agents(connection, bus, scope, time_source), SettingRows(connection, bus, scope, time_source))


class SayNo(Listener[Creating]):
    def handle(self, event):
        raise Rejection("not today")


def test_a_saved_task_gets_an_id_and_the_actor_stamp(connection, bus, scope):
    tasks = tasks_of(connection, bus, scope)
    with scope.environment(1):
        task = tasks.save(Task(environment_id=1, title="write the release notes"), actor=USER)
        assert task.id == 1
        assert task.creator == USER and task.updater == USER
        assert task.created_at is not None
        assert tasks.find(1) == task


def test_a_read_asking_more_than_a_page_is_cut_to_a_page_and_a_whole_read_past_a_page_is_recorded(connection, bus, scope):
    tasks = tasks_of(connection, bus, scope)
    for n in range(150):
        tasks.save(Task(environment_id=1, title=f"task {n}"), actor=USER)
    reads = connection.large_reads
    with scope.environment(1):
        assert len(tasks.selected(tasks.query().order("id").limit(50))) == 50 and reads.largest(10) == [], "a read of a page or less is not recorded"
        assert len(tasks.selected(tasks.query().order("id").limit(500))) == 100, "a read asking 500 rows reads a page of 100"
        assert len(tasks.rows()) == 150, "a whole-table read reads every row"
    recorded = reads.largest(10)
    assert [(read.largest_rows, read.table) for read in recorded] == [(500, "tasks"), (150, "tasks")], recorded
    assert all(read.caller.startswith("test_data.py:") for read in recorded), "each names the code that asked, outside the repositories"


def test_every_model_event_is_heard_in_order_with_its_actor(connection, bus, scope):
    heard = Heard()
    bus.listen(ModelEvent, heard)
    tasks = tasks_of(connection, bus, scope)
    with scope.environment(1):
        task = tasks.save(Task(environment_id=1, title="t"), actor=USER)
        tasks.save(task.with_(state=TaskState.STARTED), actor=AGENT)
        tasks.delete(task, actor=USER)
    kinds = [type(e).__name__ for e in heard.events]
    assert kinds == ["Saving", "Creating", "Created", "Saved", "Saving", "Updating", "Updated", "Saved", "Deleting", "Deleted"]
    assert heard.events[5].actor == AGENT and heard.events[5].model.state == TaskState.STARTED
    with scope.environment(1), pytest.raises(MissingRow):
        tasks.find(task.id)


def test_a_refusing_listener_stops_the_write(connection, bus, scope):
    bus.listen(Creating, SayNo())
    tasks = tasks_of(connection, bus, scope)
    with pytest.raises(Rejection):
        tasks.save(Task(environment_id=1, title="t"), actor=USER)
    with scope.environment(1):
        assert tasks.all() == []


def test_links_join_any_two_rows_and_leave_with_a_deleted_row(connection, bus, scope):
    tasks, links = tasks_of(connection, bus, scope), Links(connection, bus, TimeSource())
    bus.listen(Deleted, UnlinkDeleted(links))
    item = tasks.save(Task(environment_id=1, title="a"), actor=USER)
    b = tasks.save(Task(environment_id=1, title="b"), actor=USER)
    links.save(Link(source=Ref.build(item), target=Ref.build(b), link_type="blocks"), actor=AGENT)
    assert links.targets(item, "blocks") == [Ref.build(b)]
    assert links.all_sources(b) == [Ref.build(item)]
    assert len(links.connecting(item, b)) == 1
    tasks.delete(b, actor=USER)
    assert links.link_rows(item) == []


def test_where_reads_typed_values_back(connection, bus, scope):
    tasks = tasks_of(connection, bus, scope)
    tasks.save(Task(environment_id=1, title="open"), actor=USER)
    started = tasks.save(Task(environment_id=1, title="started", state=TaskState.STARTED), actor=USER)
    with scope.environment(1):
        assert tasks.with_state(TaskState.STARTED) == [started]
    with scope.environment(2):
        assert tasks.scoped() == [] and tasks.matching(title="open") == [] and tasks.search(["open"]) == [] and tasks.count() == 0, "every read is the scope's, whatever it asks"
    with pytest.raises(ScopeMissing):
        tasks.matching(title="open")
    assert [t.title for t in tasks.global_matching(title="open")] == ["open"], "a read across environments says so by its name"


def test_writes_from_many_threads_all_land(connection, bus, scope):
    tasks = tasks_of(connection, bus, scope)

    def write(n):
        tasks.save(Task(environment_id=1, title=f"t{n}"), actor=USER)

    threads = [threading.Thread(target=write, args=(n,)) for n in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with scope.environment(1):
        assert len(tasks.all()) == 20


def test_a_column_a_model_gained_is_added_to_a_table_made_before_it(tmp_path):
    from journal.db.connection import Connection
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    old = Connection(tmp_path / "old.db", Masks(SecretValues(Config(tmp_path))), StageTimes(), QueryTimes(), LargeReads())
    with old.transaction() as db:
        db.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, environment_id INTEGER)")
    Schema(old, AllModels.MODELS).create()
    names = {row["name"] for row in old.execute("PRAGMA table_info(messages)").fetchall()}
    assert "idempotency" in names and "text" in names


def test_a_thread_returns_its_connection_to_the_pool(connection):
    import threading
    def work():
        connection.all("SELECT 1")
        connection.release()
    for _ in range(30):
        t = threading.Thread(target=work)
        t.start()
        t.join()
    assert len(connection._open) <= 2


def test_a_row_older_than_a_column_loads_with_the_fields_default(tmp_path):
    from journal.db.connection import Connection
    from journal.db.schema import Schema
    from journal.events.bus import Bus
    from journal.models.all_models import AllModels
    from journal.repositories.messages import Messages
    from journal.repositories.reactions import Reactions
    from journal.repositories.links import Links
    from journal.repositories.environments import Environments
    from journal.repositories.scope import Scope
    old = Connection(tmp_path / "old.db", Masks(SecretValues(Config(tmp_path))), StageTimes(), QueryTimes(), LargeReads())
    with old.transaction() as db:
        db.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, environment_id INTEGER, author TEXT, text TEXT, created_at TEXT, updated_at TEXT, creator TEXT, updater TEXT)")
        db.execute("INSERT INTO messages (environment_id, author, text, created_at, updated_at, creator, updater) VALUES (1, 'user', 'old', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', 'user:1', 'user:1')")
    Schema(old, AllModels.MODELS).create()
    bus = Bus()
    links = Links(old, bus, TimeSource())
    scope = Scope(Environments(old, bus, TimeSource()), links)
    with scope.environment(1):
        message = Messages(old, bus, scope, Reactions(old, bus, scope, links, TimeSource()), links, TimeSource()).find(1)
    assert message.files == () and message.acknowledgement is False and message.idempotency == "" and message.read_at is None


def test_a_title_is_one_line_of_eighty_characters_without_a_colon_and_an_old_one_is_left_alone(connection, bus, scope):
    from journal.support.actor import Actor
    from journal.models.task import Task
    from journal.support.rejection import Rejection
    tasks = tasks_of(connection, bus, scope)
    with scope.environment(1):
        with pytest.raises(Rejection, match="at most 80 characters"):
            tasks.save(Task(environment_id=1, title="x" * 81), Actor.system())
        with pytest.raises(Rejection, match="no colon"):
            tasks.save(Task(environment_id=1, title="Titles: the rule"), Actor.system())
        short = tasks.save(Task(environment_id=1, title="The title rule", brief="x" * 500), Actor.system())
        assert tasks.save(short.with_(brief="changed"), Actor.system()).brief == "changed", "a row saved again with the title it had is left alone"


def test_a_row_answers_its_heading_its_summary_and_its_dock_card():
    from journal.models.doc import Doc
    from journal.models.memory import Memory
    from journal.models.plan import Plan
    from journal.models.report import Report
    from journal.models.support.dock_card import DockCard
    from journal.models.support.row_card import RowCard
    report = Report(id=33, title="What the dock showed", abstract="One line about it", body="## First\n\ntext")
    assert report.heading() == "Report 33: What the dock showed" and report.summary_line() == "One line about it"
    assert Doc(id=3, title="Notes", abstract="How the notes are kept", body="# Notes\n\nThe first line.\nThe second.").summary_line() == "How the notes are kept", "a document's summary is its abstract"
    task = Task(id=12, title="Write it", brief="First line of the brief\nmore")
    assert task.heading() == "Task 12: Write it" and task.summary_line() == "First line of the brief"
    assert Memory(id=2, text="Ports are fixed").heading() == "Memory 2" and Memory(id=2).summary_line() == ""
    assert task.docked() == DockCard.plain() and [b.label for b in DockCard.plain().buttons] == ["Open", "Close"]
    assert [(b.label, b.act) for b in Plan(id=1).docked().buttons] == [("Open plan", "open"), ("Approve", "approve"), ("Close", "close")]
    assert RowCard.build(report).as_data() == {"row": "reports:33", "heading": "Report 33: What the dock showed", "summary": "One line about it", "status": "Ready", "dock": {"buttons": [{"label": "Open", "act": "open"}, {"label": "Close", "act": "close"}], "folds": True}}, "a card carries no file: a document is downloaded from where it is read"


def legacy_workers(connection) -> None:
    """The workers table as journals kept it before workers and verifiers shared the table of sent agents, for the migrations that ran on it, with none of the Role columns a worker has had since."""
    from journal.db.schema import Schema
    from journal.models.worker import Worker
    columns = ", ".join(f"{column.name} {column.sql_type}" for column in Schema.columns(Worker) if column.name not in ("id", "helper_type", "role"))
    connection.execute(f"CREATE TABLE workers (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")


def test_the_time_keys_migration_renames_at_in_the_column_and_the_stored_json(connection):
    """Migration 20: the edits column at becomes time, and the at key inside an entry's data, a check's progress and a dump's question and answers becomes time; a record without them is left as it is."""
    from journal.db.migrations.time_keys import TimeKeys
    kind_columns(connection)
    connection.execute("ALTER TABLE edits RENAME COLUMN time TO at")
    for table, now, then in (("checks", "progress", "running"), ("dumps", "choice", "chosen"), ("dumps", "claimed", "taken")):
        connection.execute(f"ALTER TABLE {table} RENAME COLUMN {now} TO {then}")
    connection.execute("INSERT INTO entries (environment_id, kind, actor, data, created_at, creator) VALUES (1, 'nudge', 'system', ?, '2026-10-21', 'system')", (json.dumps({"key": "k", "at": 5.0}),))
    connection.execute("INSERT INTO entries (environment_id, kind, actor, data, created_at, creator) VALUES (1, 'ran', 'system', ?, '2026-10-21', 'system')", (json.dumps({"command": "ls"}),))
    connection.execute("INSERT INTO checks (title, running, created_at, creator) VALUES ('c', ?, '2026-10-21', 'system')", (json.dumps({"at": 7.0, "output": ""}),))
    connection.execute("INSERT INTO dumps (environment_id, question, answers, chosen, taken, created_at, creator) VALUES (1, ?, ?, '{}', '{}', '2026-10-21', 'system')", (json.dumps({"at": 1.0, "text": "q"}), json.dumps([{"question": "q", "answer": "a", "at": 2.0}])))
    TimeKeys().apply(connection)
    assert "time" in {row["name"] for row in connection.all("PRAGMA table_info(edits)")} and "at" not in {row["name"] for row in connection.all("PRAGMA table_info(edits)")}
    nudge, completed = [json.loads(row["data"]) for row in connection.all("SELECT data FROM entries ORDER BY id")]
    assert nudge == {"key": "k", "time": 5.0} and completed == {"command": "ls"}, "the key moves where it is, and a row without it is untouched"
    assert json.loads(connection.one("SELECT running FROM checks")["running"]) == {"time": 7.0, "output": ""}
    dump = connection.one("SELECT question, answers FROM dumps")
    assert json.loads(dump["question"]) == {"time": 1.0, "text": "q"} and json.loads(dump["answers"]) == [{"question": "q", "answer": "a", "time": 2.0}]
    connection.execute("ALTER TABLE edits ADD COLUMN at REAL DEFAULT 0")
    connection.execute("INSERT INTO edits (environment_id, session, path, at, time, created_at, creator) VALUES (1, 's', 'a.py', 9.0, 0, '2026-10-21', 'system')")
    TimeKeys().apply(connection)
    names = {row["name"] for row in connection.all("PRAGMA table_info(edits)")}
    assert "at" not in names and connection.one("SELECT time FROM edits")["time"] == 9.0, "where the schema already added the time column, the old at column's values move into it and the column goes"


def test_the_verifiers_once_kept_as_workers_go_with_their_links_their_role_column_and_their_chat_cards(connection):
    from journal.db.migrations.orphan_worker_cards import OrphanWorkerCards
    from journal.db.migrations.verifier_workers_drop import VerifierWorkersDrop
    legacy_workers(connection)
    kind_columns(connection)
    connection.execute("ALTER TABLE workers ADD COLUMN role TEXT DEFAULT 'worker'")
    for name, role in (("Ada", "worker"), ("Diogenes", "verifier")):
        connection.execute("INSERT INTO workers (environment_id, name, role, created_at, creator) VALUES (1, ?, ?, '2026-10-25', 'system')", (name, role))
    ada, diogenes = [row["id"] for row in connection.all("SELECT id FROM workers ORDER BY id")]
    connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES (?, 'reader_reports:1', 'verifies', '2026-10-25', 'system')", (f"workers:{diogenes}",))
    for data in ({"row": f"workers:{ada}"}, {"row": f"workers:{diogenes}"}, {"key": f"worker:{diogenes}:stopped:1"}, {"key": "verifier:1"}):
        connection.execute("INSERT INTO messages (environment_id, author, text, data, created_at, creator) VALUES (1, 'system', 'card', ?, '2026-10-25', 'system')", (json.dumps(data),))
    VerifierWorkersDrop().apply(connection)
    OrphanWorkerCards().apply(connection)
    assert [row["name"] for row in connection.all("SELECT name FROM workers")] == ["Ada"] and not connection.all("SELECT id FROM links WHERE kind = 'verifies'")
    assert "role" not in {row["name"] for row in connection.all("PRAGMA table_info(workers)")}, "the workers lose the column that told a verifier apart"
    assert [json.loads(row["data"]) for row in connection.all("SELECT data FROM messages ORDER BY id")] == [{"row": f"workers:{ada}"}, {"key": "verifier:1"}], "only the cards of the removed verifiers go"


def test_workers_and_verifiers_move_into_the_one_table_of_sent_agents_each_keeping_what_names_it(connection):
    from journal.db.migrations.helper_rows import HelperRows
    from journal.db.schema import Schema
    from journal.models.verifier import Verifier
    legacy_workers(connection)
    columns = ", ".join(f"{column.name} {column.sql_type}" for column in Schema.columns(Verifier) if column.name not in ("id", "helper_type"))
    connection.execute(f"CREATE TABLE verifiers (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")
    for name in ("Ada", "Grace"):
        connection.execute("INSERT INTO workers (environment_id, name, state, created_at, creator) VALUES (1, ?, 'dispatched', '2026-10-25', 'system')", (name,))
    connection.execute("INSERT INTO verifiers (environment_id, name, state, created_at, creator) VALUES (1, 'Diogenes', 'judged', '2026-10-25', 'system')")
    connection.execute("INSERT INTO links (source, target, link_type, created_at, creator) VALUES ('verifiers:1', 'reader_reports:4', 'verifies', '2026-10-25', 'system')")
    connection.execute("INSERT INTO messages (environment_id, author, text, data, created_at, creator) VALUES (1, 'system', 'card', ?, '2026-10-25', 'system')", (json.dumps({"key": "verifier:1"}),))
    HelperRows().apply(connection)
    rows = [(row["id"], row["name"], row["helper_type"]) for row in connection.all("SELECT id, name, helper_type FROM sent_agents ORDER BY id")]
    assert rows == [(1, "Ada", "worker"), (2, "Grace", "worker"), (3, "Diogenes", "verifier")], "each worker keeps its number, and a verifier takes one after the last so none meets a worker's"
    assert connection.one("SELECT source FROM links")["source"] == "verifiers:3" and json.loads(connection.one("SELECT data FROM messages")["data"]) == {"key": "verifier:3"}, "its link and its card follow its new number"
    tables = {row["name"] for row in connection.all("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "workers" not in tables and "verifiers" not in tables, "and the two old tables go"


def test_the_trigger_phrases_migration_renames_the_words_column(connection):
    """Migration 21: a trigger's words column becomes phrases, carried over when the schema already added phrases."""
    from journal.db.migrations.trigger_phrases import TriggerPhrases
    connection.execute("ALTER TABLE triggers ADD COLUMN words TEXT DEFAULT '[]'")
    connection.execute("INSERT INTO triggers (phrases, words, action, text, created_at, creator) VALUES ('[]', '[\"deploy\"]', 'deny', 'no', '2026-10-21', 'system')")
    TriggerPhrases().apply(connection)
    names = {row["name"] for row in connection.all("PRAGMA table_info(triggers)")}
    assert "words" not in names and connection.one("SELECT phrases FROM triggers")["phrases"] == '["deploy"]'
    connection.execute("ALTER TABLE triggers RENAME COLUMN phrases TO words")
    TriggerPhrases().apply(connection)
    assert "phrases" in {row["name"] for row in connection.all("PRAGMA table_info(triggers)")}, "a record from before, with words alone, has the column renamed"


def test_the_paused_tasks_migration_turns_a_parked_task_and_plan_into_paused_ones(connection):
    """Migration 42: a task or plan stored as parked is paused, and the task's suspension_reason column is its pause_reason."""
    from journal.db.migrations.paused_tasks import PausedTasks
    connection.execute("ALTER TABLE tasks ADD COLUMN suspension_reason TEXT DEFAULT ''")
    connection.execute("INSERT INTO tasks (environment_id, title, state, suspension_reason, created_at, creator) VALUES (1, 'the parser', 'parked', 'waits on the lexer', '2026-10-23', 'system')")
    connection.execute("INSERT INTO plans (environment_id, title, state, created_at, creator) VALUES (1, 'release', 'parked', '2026-10-23', 'system')")
    PausedTasks().apply(connection)
    task = connection.one("SELECT state, pause_reason FROM tasks")
    assert (task["state"], task["pause_reason"]) == ("paused", "waits on the lexer") and connection.one("SELECT state FROM plans")["state"] == "paused"


def test_the_paused_tasks_become_blocked_and_the_pause_leaves_the_columns_and_the_stacks(connection):
    """Migrations 85 and 86: a paused task is blocked with its pause reason, or a reason that says when it was paused, and the pause's columns and the choice of paused work on a stack are gone."""
    from journal.db.migrations.paused_tasks_blocked import PausedTasksBlocked
    from journal.db.migrations.pause_columns_drop import PauseColumnsDrop
    connection.execute("ALTER TABLE tasks ADD COLUMN pause_reason TEXT DEFAULT ''")
    connection.execute("ALTER TABLE tasks ADD COLUMN wait_ended_at REAL DEFAULT 0")
    connection.execute("ALTER TABLE agents ADD COLUMN paused_declined INTEGER DEFAULT 0")
    for title, state, reason in (("the parser", "paused", "waits on the lexer"), ("the lexer", "paused", ""), ("the printer", "open", "")):
        connection.execute("INSERT INTO tasks (environment_id, title, state, pause_reason, block_reason, created_at, creator) VALUES (1, ?, ?, ?, '', '2026-10-31', 'system')", (title, state, reason))
    stack = [{"state": "idle", "data": {}}, {"state": "choosing_paused_work", "data": {"refusals": 1}}]
    connection.execute("INSERT INTO agents (session, state, stack, created_at, creator) VALUES ('s1', 'choosing_paused_work', ?, '2026-10-31', 'system')", (json.dumps(stack),))
    PausedTasksBlocked().apply(connection)
    PauseColumnsDrop().apply(connection)
    tasks = [(row["title"], row["state"], row["block_reason"]) for row in connection.all("SELECT title, state, block_reason FROM tasks ORDER BY id")]
    assert tasks == [("the parser", "blocked", "waits on the lexer"), ("the lexer", "blocked", "paused before version 4.69.15"), ("the printer", "open", "")]
    assert not {"pause_reason", "wait_ended_at"} & {row["name"] for row in connection.all("PRAGMA table_info(tasks)")} and "paused_declined" not in {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
    agent = connection.one("SELECT state, stack FROM agents")
    assert (agent["state"], json.loads(agent["stack"])) == ("idle", [{"state": "idle", "data": {}}]), "the choice of paused work leaves the stack, and the state beneath it is the agent's state"


def test_the_load_keys_migration_lets_a_load_stored_with_the_dropped_minutes_read_again(connection):
    """Migration 64: the over_full_minutes and over_zero_minutes keys leave the stored queues and the loads by mode, and each reads as an AgentLoad."""
    import json
    from journal.db.migrations.load_keys_drop import LoadKeysDrop
    from journal.models.support.agent_load import AgentLoad
    stale = {"rho": 0.5, "over_full_minutes": 10.0, "over_zero_minutes": 60.0}
    connection.execute("INSERT INTO agents (environment_id, session, created_at, creator, work_queue, message_queue, mode_loads) VALUES (1, 's1', '2026-10-26', 'system', ?, ?, ?)", (json.dumps(stale), json.dumps(stale), json.dumps({"builder": stale})))
    LoadKeysDrop().apply(connection)
    row = connection.one("SELECT work_queue, message_queue, mode_loads FROM agents")
    loads = [json.loads(row["work_queue"]), json.loads(row["message_queue"]), json.loads(row["mode_loads"])["builder"]]
    assert [AgentLoad.parsed(load).rho for load in loads] == [0.5, 0.5, 0.5]


def test_no_dataclass_field_shadows_a_property_or_method_of_its_class_or_a_parent():
    """A frozen dataclass whose field is named like a property or a method on it, its own or inherited, cannot be built: the generated __init__ sets the field and the property has no setter. Every dataclass under the package is checked, so a rename can never leave such a pair behind."""
    import dataclasses
    import importlib
    import inspect
    import pkgutil
    import journal
    clashes = []
    for matched in pkgutil.walk_packages(journal.__path__, "journal."):
        module = importlib.import_module(matched.name)
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != matched.name or not dataclasses.is_dataclass(cls):
                continue
            for field in dataclasses.fields(cls):
                for owner in cls.__mro__:
                    attribute = owner.__dict__.get(field.name)
                    if isinstance(attribute, property) or inspect.isfunction(attribute):
                        clashes.append(f"{cls.__module__}.{cls.__name__}.{field.name} shadows {owner.__name__}.{field.name}")
    assert clashes == [], "\n".join(clashes)


def test_the_dashboard_sections_migration_renames_the_heading_column(connection):
    """Migration 22: a dashboard line's heading column becomes section, carried over when the schema already added section."""
    from journal.db.migrations.dashboard_sections import DashboardSections
    connection.execute("ALTER TABLE dashboard_rows ADD COLUMN heading TEXT DEFAULT ''")
    connection.execute("INSERT INTO dashboard_rows (plugin, key, label, heading, section, created_at, creator) VALUES ('p', 'k', 'l', 'Totals', '', '2026-10-21', 'system')")
    DashboardSections().apply(connection)
    names = {row["name"] for row in connection.all("PRAGMA table_info(dashboard_rows)")}
    assert "heading" not in names and connection.one("SELECT section FROM dashboard_rows")["section"] == "Totals"


def test_the_chart_drop_keeps_only_workflows_a_user_or_an_agent_wrote_as_documents(connection):
    from journal.db.migrations.chart_drop import ChartDrop
    kind_columns(connection)
    with connection.transaction() as db:
        db.execute("ALTER TABLE docs RENAME COLUMN creator TO created_by")
        db.execute("ALTER TABLE docs RENAME COLUMN updater TO updated_by")
        db.execute("CREATE TABLE charts (id INTEGER PRIMARY KEY, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT, title TEXT, revision INTEGER, shipped INTEGER, event TEXT, state TEXT, places TEXT, drawing TEXT, drawn_version INTEGER, locked INTEGER)")
        db.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, kind TEXT, key TEXT, text TEXT)")
        db.execute("CREATE TABLE counts (id INTEGER PRIMARY KEY)")
        db.execute("CREATE TABLE noted_times (id INTEGER PRIMARY KEY)")
        rows = [("Hold the stop while a task is paused", 5, 1, "system"), ("Remind to commit after twenty writes", 2, 1, "user:1"), ("Ask about an open question after ten quiet minutes", 0, 0, "agent:s1")]
        for title, revision, shipped, editor in rows:
            db.execute("INSERT INTO charts (created_at, created_by, updated_at, updated_by, title, revision, shipped, event, state, places, drawing, drawn_version, locked) VALUES ('t', 'system', 't', ?, ?, ?, ?, 'idle', 'idle', '', '', 30, 0)", (editor, title, revision, shipped))
    ChartDrop().apply(connection)
    titles = [row["title"] for row in connection.all("SELECT title FROM docs WHERE title LIKE 'Workflow: %' ORDER BY id")]
    assert titles == ["Workflow: Remind to commit after twenty writes", "Workflow: Ask about an open question after ten quiet minutes"], "a shipped workflow re-drawn by an upgrade is the journal's, however many revisions it counts; one a user or an agent last wrote is kept"
    assert connection.one("SELECT name FROM sqlite_master WHERE name = 'charts'") is None, "the chart's tables are gone"


def test_the_timestamp_renames_migration_moves_the_phone_codes_and_the_wait_times_to_their_at_names(connection):
    """Migration 26: the pairing codes table becomes phone_codes with expires_at, and a wait stored on an agent's row keeps its started and reminded times under their _at names."""
    from journal.db.migrations.timestamp_renames import TimestampRenames
    connection.execute("ALTER TABLE phone_codes RENAME COLUMN expires_at TO expiry_time")
    connection.execute("ALTER TABLE phone_codes RENAME TO pairing_codes")
    wait = {"state": "awaiting", "data": {"focus": "ci", "start_time": 5.0, "reminder_time": 9.0}}
    connection.execute("INSERT INTO agents (environment_id, session, state, data, stack, created_at, creator) VALUES (1, 's', 'awaiting', ?, ?, '2026-10-21', 'system')", (json.dumps(wait["data"]), json.dumps([{"state": "idle", "data": {}}, wait])))
    TimestampRenames().apply(connection)
    assert "expires_at" in {row["name"] for row in connection.all("PRAGMA table_info(phone_codes)")}
    row = connection.one("SELECT data, stack FROM agents WHERE session = 's'")
    assert json.loads(row["data"]) == {"focus": "ci", "started_at": 5.0, "reminded_at": 9.0} and json.loads(row["stack"])[-1]["data"]["started_at"] == 5.0


def test_the_worker_reuse_counts_migration_reads_each_reuse_from_the_reports_before_it(connection):
    """Migration 30: an old worker row's reuse count comes from its report links, the last report followed by a send when it is out again; the reason it was retired starts empty."""
    from journal.db.migrations.worker_reuse_counts import WorkerReuseCounts
    legacy_workers(connection)
    kind_columns(connection)
    for n, state in ((1, "reported"), (2, "dispatched"), (3, "dispatched")):
        connection.execute("INSERT INTO workers (environment_id, name, state, created_at, creator) VALUES (1, ?, ?, '2026-10-21', 'system')", (f"w{n}", state))
    for worker, reports in ((1, 3), (2, 2)):
        for message in range(reports):
            connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES (?, ?, 'reported', '2026-10-21', 'system')", (f"workers:{worker}", f"messages:{worker * 10 + message}"))
    connection.execute("UPDATE workers SET reuse_count = NULL, retire_reason = NULL")
    WorkerReuseCounts().apply(connection)
    counts = [(row["name"], row["reuse_count"]) for row in connection.all("SELECT name, reuse_count FROM workers ORDER BY id")]
    assert counts == [("w1", 2), ("w2", 2), ("w3", 0)], "three reports and back is two sends; two reports and out again is two; out on its first job is none"


def test_the_message_thread_migration_renames_the_column_and_a_side_thread_message_reads_back_by_its_thread(connection):
    """Migration 65: a database whose messages keep their chat in agent_role keeps every row, the people's side thread among them, under thread."""
    from journal.db.migrations.message_thread_column import MessageThreadColumn
    connection.execute("ALTER TABLE messages RENAME COLUMN thread TO agent_role")
    for role in ("main", "people", "worker"):
        connection.execute("INSERT INTO messages (environment_id, author, text, data, agent_role, created_at, creator) VALUES (1, 'user', ?, '{}', ?, '2026-10-26', 'user:1')", (f"in {role}", role))
    MessageThreadColumn().apply(connection)
    rows = [(row["text"], row["thread"]) for row in connection.all("SELECT text, thread FROM messages ORDER BY id")]
    assert rows == [("in main", "main"), ("in people", "people"), ("in worker", "worker")]


def test_the_message_agents_migration_moves_the_session_into_its_column_and_puts_every_message_in_the_main_chat(connection):
    """Migration 34: a peer message's session leaves its data for the session column, an agent's own message takes its writer's session, a user's has none, and all of them are the main agent's."""
    from journal.db.migrations.message_agents import MessageAgents
    for creator, data in (("system", {"kind": "peer", "session": "s1", "peer": "other"}), ("agent:s2", {}), ("user:1", {}), ("system", {"session": ""})):
        connection.execute("INSERT INTO messages (environment_id, author, text, data, created_at, creator) VALUES (1, 'agent', 'x', ?, '2026-10-22', ?)", (json.dumps(data), creator))
    connection.execute("ALTER TABLE messages RENAME COLUMN thread TO agent_role")
    connection.execute("UPDATE messages SET session = NULL, agent_role = NULL")
    MessageAgents().apply(connection)
    rows = [(row["session"], row["agent_role"], json.loads(row["data"])) for row in connection.all("SELECT session, agent_role, data FROM messages ORDER BY id")]
    assert rows == [("s1", "main", {"kind": "peer", "peer": "other"}), ("s2", "main", {}), (None, "main", {}), (None, "main", {})]


def test_a_query_renders_every_read_shape_with_its_values_bound():
    tasks, entries = Query.build(Task), Query.build(Entry)
    assert tasks.filter(state=TaskState.OPEN, creator=None).order_descending("id").limit(5).select() == ("SELECT * FROM tasks WHERE state = ? AND creator IS NULL ORDER BY id DESC LIMIT ? OFFSET ?", ("open", 5, 0)), "a value is turned by its column, and None reads as null"
    assert tasks.filter_listed("id", (1, 2)).filter_unlisted("state", (TaskState.COMPLETED,)).filter_present("block_reason").select() == ("SELECT * FROM tasks WHERE id IN (?, ?) AND state NOT IN (?) AND block_reason IS NOT NULL", (1, 2, TaskState.COMPLETED.value))
    assert tasks.filter_greater("id", 1).filter_less("id", 9).filter_greater_equal("id", 2).filter_less_equal("id", 8).filter_unequal("title", "x").select()[0] == "SELECT * FROM tasks WHERE id > ? AND id < ? AND id >= ? AND id <= ? AND title IS NOT ?"
    assert tasks.filter_prefix("title", "a").filter_missing_prefix("creator", "user:").select() == ("SELECT * FROM tasks WHERE title >= ? AND title < ? AND (creator IS NULL OR creator < ? OR creator >= ?)", ("a", "a\uffff", "user:", "user:\uffff"))
    assert tasks.filter_containing("title", "50%_off").order("state").order_descending("id").offset(3).select() == ("SELECT * FROM tasks WHERE title LIKE ? ESCAPE '\\' ORDER BY state, id DESC LIMIT ? OFFSET ?", ("%50\\%\\_off%", -1, 3))
    assert entries.filter_json("data->session", "s").filter_listed("data->call->kind", ("a",)).maximum("data->time", 0) == ("SELECT COALESCE(MAX(json_extract(data, '$.time')), 0) AS value FROM entries WHERE json_extract(data, '$.session') = ? AND json_extract(data, '$.call.kind') IN (?)", ("s", "a"))
    assert tasks.filter_alternatives(tasks.filter(title="a"), tasks.filter(title="b").filter_null("block_reason")).count() == ("SELECT count(*) AS value FROM tasks WHERE (title = ? OR (title = ? AND block_reason IS NULL))", ("a", "b"))
    assert entries.filter(entry_type="ToolStarting").order_descending("id").limit(9).repeated("data->call->command", 2) == ("SELECT value FROM (SELECT json_extract(data, '$.call.command') AS value FROM entries WHERE entry_type = ? ORDER BY id DESC LIMIT ? OFFSET ?) WHERE value != '' GROUP BY value HAVING COUNT(*) >= ?", ("ToolStarting", 9, 0, 2)), "the values a page of rows holds at least so many times"
    assert tasks.filter_absent(Query.build(Link).filter(link_type="in_plan").filter_ref("source", tasks)).count() == ("SELECT count(*) AS value FROM tasks WHERE NOT EXISTS (SELECT 1 FROM links WHERE link_type = ? AND links.source = ? || tasks.id)", ("in_plan", "tasks:"))


def test_a_query_renders_its_writes_and_writes_a_condition_into_its_text():
    tasks = Query.build(Task)
    assert tasks.insert(title="a", state=TaskState.OPEN) == ("INSERT INTO tasks (title, state) VALUES (?, ?)", ("a", "open"))
    assert tasks.filter(id=3).update(title="b", creator=USER) == ("UPDATE tasks SET title = ?, creator = ? WHERE id = ?", ("b", USER.stamp, 3))
    assert tasks.filter(id=3).delete() == ("DELETE FROM tasks WHERE id = ?", (3,)) and tasks.delete() == ("DELETE FROM tasks", ())
    inlined = tasks.filter_listed("title", ("it's", "b")).inlined().filter(id=1)
    assert inlined.clause() == "title IN ('it''s', 'b') AND id = ?" and inlined.select()[1] == (1,), "an inlined condition holds its values in the text, as a partial index's terms must, and what follows is bound"


def test_a_query_fails_on_a_column_its_table_does_not_have():
    with pytest.raises(UnknownColumn):
        Query.build(Task).filter(titel="a")
    with pytest.raises(UnknownColumn):
        Query.build(Task).order("nope")
    with pytest.raises(UnknownColumn):
        Query.build(Entry).filter_json("data->it's", 1)


def test_a_line_said_before_lines_carried_the_tool_use_gains_it_and_its_moment(tmp_path):
    """A nudge entry written by an older journal, with no tool use, is given one at the migration, so a read of the last line of a kind never fails."""
    import json
    import sqlite3
    from journal.app import App
    from journal.config import Config
    first = App(Config(tmp_path, port=0))
    first.runtime().start()
    first.runtime().stop()
    db = sqlite3.connect(first.config.database)
    kind_columns(db)
    db.execute("INSERT INTO entries (environment_id, kind, actor, data, created_at, creator, updated_at, updater) VALUES (1, 'nudge', 'system', ?, '2026-10-01T10:00:00+00:00', 'system', '2026-10-01T10:00:00+00:00', 'system')", (json.dumps({"key": "shell.outputs_ended", "session": "s1", "line": "output 1 finished"}),))
    db.execute("DELETE FROM migrations WHERE number >= 37")
    db.commit()
    db.close()
    second = App(Config(tmp_path, port=0))
    second.runtime().start()
    second.runtime().stop()
    db = sqlite3.connect(second.config.database)
    data = json.loads(db.execute("SELECT data FROM entries WHERE entry_type = 'nudge' AND json_extract(data, '$.line') = 'output 1 finished'").fetchone()[0])
    assert data["tool_use"] == 0 and data["time"] > 0, data


def test_the_tasks_repository_answers_which_tasks_are_open_blocked_and_unclosed(connection, bus, scope):
    from journal.models.plan import Plan
    from journal.models.plan_state import PlanState
    from journal.repositories.scoped_repository import ScopedRepository
    from journal.repositories.tasks import PLAN_LINK

    class PlanRows(ScopedRepository[Plan]):
        model = Plan

    tasks, links = tasks_of(connection, bus, scope), Links(connection, bus, TimeSource())
    with scope.environment(1):
        free = tasks.save(Task(environment_id=1, title="free"), actor=USER)
        drafted = tasks.save(Task(environment_id=1, title="in a draft plan"), actor=USER)
        blocked = tasks.save(Task(environment_id=1, title="blocked", state=TaskState.BLOCKED), actor=USER)
        done = tasks.save(Task(environment_id=1, title="done", state=TaskState.COMPLETED), actor=USER)
        draft = PlanRows(connection, bus, scope, TimeSource()).save(Plan(environment_id=1, title="p", state=PlanState.DRAFT), USER)
        links.save(Link(source=Ref.build(drafted), target=Ref.build(draft), link_type=PLAN_LINK), actor=USER)
        assert [task.id for task in tasks.open_tasks()] == [free.id], "a task of an unapproved plan is no open work"
        assert [task.id for task in tasks.blocked_tasks()] == [blocked.id]
        assert done.id not in [task.id for task in tasks.unclosed_tasks()] and free.id in [task.id for task in tasks.unclosed_tasks()]
        assert tasks.unfinished_ids([free.id, done.id]) == [free.id]












def migration_withdrawn(tmp_path, name: str, scope, tasks, outgoing, actor) -> None:
    """The migration's withdrawals planned and queued on the team journal of that name, with no hub made and no document moved."""
    migration = team_migration(tmp_path, name, scope, tasks, outgoing)
    migration.withdrawal.withdraw(tuple(migration.withdrawal.planned(actor.stamp, migration.placement)), actor)


def test_a_new_journal_has_every_index_and_an_index_whose_definition_changed_is_made_again(tmp_path):
    from journal.app import App
    from journal.config import Config
    from journal.db.indexes import Indexes
    from journal.repositories.declared_indexes import INDEXES

    connection = App(Config(tmp_path / "fresh", port=0)).connection()
    present = {row["name"]: row["sql"] for row in connection.all("SELECT name, sql FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL")}
    assert {index.name: index.sql() for index in INDEXES}.items() <= present.items(), "a journal created fresh has every index its reads rely on"
    assert present["environments_key"].startswith("CREATE UNIQUE INDEX"), "one environment to a key"
    connection.execute("DROP INDEX entries_dispatches")
    connection.execute("CREATE INDEX entries_dispatches ON entries (environment_id, id) WHERE entry_type = 'Stop'")
    Indexes(connection, INDEXES).refresh()
    assert connection.result("SELECT sql FROM sqlite_master WHERE name = 'entries_dispatches'")[0] == next(index.sql() for index in INDEXES if index.name == "entries_dispatches"), "an index made under an older definition is made again under the current one"
    connection.close()




def test_the_developer_numbers_drop_removes_the_timings_table_and_the_numbers_but_not_other_statistics(connection):
    from journal.db.migrations.developer_numbers_drop import DeveloperNumbersDrop
    connection.execute("CREATE TABLE IF NOT EXISTS timings (id INTEGER PRIMARY KEY)")
    connection.execute("INSERT INTO statistics (key, value, created_at, creator) VALUES ('developer.hooks.count', 3, '2026-10-24', 'system'), ('profiles.x.uses', 2, '2026-10-24', 'system')")
    DeveloperNumbersDrop().apply(connection)
    assert connection.one("SELECT name FROM sqlite_master WHERE name = 'timings'") is None
    assert [row["key"] for row in connection.all("SELECT key FROM statistics")] == ["profiles.x.uses"]


def test_a_session_change_keeps_unrelated_sessions_and_marks_when_the_old_session_ended():
    from datetime import datetime, timezone
    from journal.models.agent import Agent
    updated_at = datetime.fromtimestamp(1234.5, timezone.utc)
    agent = Agent(session="old", provider="claude", previous_sessions=("gemini:other", "codex:new", "gemini:old"), updated_at=updated_at)
    changed = agent.with_session("new", "codex")
    assert changed.previous_sessions == ("gemini:other", "claude:old")
    assert changed.previous_session_updated_at == updated_at.timestamp()
    assert changed.last_sessions() == {"gemini": "other", "claude": "old", "codex": "new"}


def test_registered_migrations_keep_unique_numbers_across_the_merged_migration_ids():
    from journal.db.migrations import MIGRATIONS
    numbers = {migration.number: type(migration).__name__ for migration in MIGRATIONS}
    assert len(numbers) == len(MIGRATIONS)
    assert tuple(numbers[number] for number in range(78, 83)) == ("PoolDrop", "TeamColumnsDrop", "FoldSettingDrop", "BrowserSessionsDrop", "DeveloperSwitchRename")
    assert (numbers[76], numbers[77], numbers[83], numbers[84]) == ("BlankAbsenceNulls", "PlanModes", "DuplicateSettingsDrop", "SyncTablesDrop")


def test_a_written_agent_answers_its_next_read_by_id_and_by_session_as_a_load_would_without_loading_it(connection, bus, scope):
    """A write keeps the reads it changed: the next find and session read of the row load nothing and return what a load returns; a rolled-back write, a write superseded in its transaction and a write a secret was masked out of keep nothing, and a session two rows share keeps answering the first."""
    from journal.models.agent import Agent
    from journal.repositories.load_tally import LoadTally
    agents = Agents(connection, bus, scope, TimeSource())
    with scope.environment(1):
        agent = agents.save(Agent(environment_id=1, session="s1", provider="claude"), USER)
        agents.session_agent("s1")
        changed = agents.save(agents.find(agent.id).with_(tool_uses=3, skills_due=("a",)), USER)
        agents.touch(changed, USER, is_overview_read=False)
        LoadTally.begin()
        found, by_session = agents.find(agent.id), agents.session_agent("s1")
        assert LoadTally.ended().points() == 0, "both reads are answered from the writes"
        connection.cache.cleared()
        assert found == by_session == agents.find(agent.id) and found.skills_due == ("a",) and found.is_overview_read is False, "as a load returns it"
        with pytest.raises(Rejection):
            with connection.transaction():
                agents.save(found.with_(tool_uses=9), USER)
                raise Rejection("rolled back")
        assert agents.find(agent.id).tool_uses == 3, "a rolled-back write keeps nothing"
        with connection.transaction():
            agents.save(agents.find(agent.id).with_(tool_uses=4), USER)
            agents.save(agents.find(agent.id).with_(tool_uses=5), USER)
        assert agents.find(agent.id).tool_uses == 5 and agents.session_agent("s1").tool_uses == 5, "the last write of a transaction is the one kept"
        twin = agents.save(Agent(environment_id=1, session="s1", provider="claude"), USER)
        assert agents.session_agent("s1").id == agent.id
        agents.save(twin.with_(tool_uses=7), USER)
        assert agents.session_agent("s1").id == agent.id, "a session two rows share answers the first, whichever is written"
        connection.masks.values.put("GITHUB_KEY", "ghp_0123456789abcdef")
        agents.save(agents.find(agent.id).with_(queued_lines=("the key is ghp_0123456789abcdef",)), USER)
        assert agents.find(agent.id).queued_lines == ("the key is [secret GITHUB_KEY]",), "a row a secret was masked out of is read as it was stored"


def test_a_load_tally_counts_on_the_thread_that_began_it_and_never_work_another_thread_runs_in_its_context():
    import contextvars
    from journal.repositories.load_tally import LoadTally
    LoadTally.begin()
    LoadTally.counted("tasks", ("a row",))
    context = contextvars.copy_context()
    deferred = threading.Thread(target=lambda: context.run(lambda: (LoadTally.counted("tasks", ("deferred",)), LoadTally.count_write("tasks"))))
    deferred.start()
    deferred.join()
    assert [(count.model, count.rows, count.writes) for count in LoadTally.ended().counts] == [("tasks", 1, 0)]


def test_the_agent_lists_a_session_start_reads_hold_only_the_other_agents_they_name(connection, bus, scope):
    from datetime import timedelta
    from journal.models.agent import Agent
    from journal.support.agent_role import AgentRole
    agents = Agents(connection, bus, scope, TimeSource())
    with scope.environment(1):
        own = agents.save(Agent(environment_id=1, session="own", provider="claude"), USER)
        agents.save(Agent(environment_id=1, session="peer", provider="claude"), USER)
        agents.save(Agent(environment_id=1, session="codex", provider="codex"), USER)
        agents.save(Agent(environment_id=1, session="worker", provider="claude", role=AgentRole.WORKER), USER)
        agents.save(Agent(environment_id=1, session="ended", provider="claude", state="ended", stack=({"state": "following_sequence", "data": {"run": {"sequence_id": 1, "title": "n", "steps": []}}},)), USER)
        agents.save(Agent(environment_id=1, session="ended-bare", provider="claude", state="ended"), USER)
        assert [agent.session for agent in agents.running_peers(own)] == ["peer"], "a running main agent of its provider"
        assert agents.ended_stacked_agent(1, "own", "following_sequence") is None, "the newest ended main agent holds no sequence, and an older one's never comes back"
        assert [agent.session for agent in agents.stacked_main_agents("following_sequence")] == [], "no running main agent holds a sequence state"
        start = datetime.now(timezone.utc) - timedelta(minutes=10)
        assert agents.recent_peer("own", start).session == "worker", "the newest peer, as an agent ended a moment after it began is no peer"
        assert agents.recent_peer("own", datetime.now(timezone.utc) + timedelta(minutes=1)) is None


def test_a_read_that_leaves_columns_or_keys_out_loads_its_rows_with_those_fields_at_their_defaults_and_counts_only_what_it_loaded(connection, bus, scope):
    from journal.models.report import Report
    from journal.repositories.entries import Entries
    from journal.repositories.load_tally import LoadTally
    from journal.repositories.reports import Reports
    reports, entries = Reports(connection, bus, scope, TimeSource()), Entries(connection, bus, scope, TimeSource())
    with scope.environment(1):
        reports.save(Report(title="the parser", abstract="what it reads", body="a long body " * 200, items=({"section": "done", "ref": "tasks:1", "title": "t"},)), USER)
        entries.save(Entry(environment_id=1, entry_type="ToolStarting", actor=Actor.agent("s1"), data={"tool_name": "Read", "tool_input": {"file_path": "x" * 3000}, "call": {"read_paths": ["x"]}}), USER)
        LoadTally.begin()
        summary = reports.selected(reports.query().without("body", "items"))[0]
        bare = reports.selected(reports.query().with_columns("title"))[0]
        call = entries.selected(entries.query().without_keys("data", "tool_input"))[0]
        loads = LoadTally.ended()
    assert (summary.title, summary.abstract, summary.body, summary.items) == ("the parser", "what it reads", "", ()), "a column left out holds its default"
    assert (bare.id, bare.title, bare.abstract) == (summary.id, "the parser", ""), "a read of only some columns keeps the number besides"
    assert call.data == {"tool_name": "Read", "call": {"read_paths": ["x"]}}, "a key left out of a JSON column is not in it"
    assert loads.points() < 10, f"what was left out is not loaded: {loads.line()}"
    with pytest.raises(UnknownColumn):
        reports.query().without("no_such_column")


def test_a_change_takes_the_row_as_it_was_from_the_read_its_repository_holds_and_the_timeline_records_only_what_a_view_shows(connection, bus, scope):
    from journal.features.listeners.record_changes import RecordChanges
    from journal.models.agent import Agent
    from journal.models.support.agent_load import AgentLoad
    from journal.repositories.entries import Entries
    from journal.repositories.load_tally import LoadTally
    agents, entries = Agents(connection, bus, scope, TimeSource()), Entries(connection, bus, scope, TimeSource())
    bus.listen(Updated, RecordChanges(entries))
    with scope.environment(1):
        agents.save(Agent(environment_id=1, session="s1", provider="claude"), USER)
        held = agents.session_rows("s1")[0]
        LoadTally.begin()
        counted = agents.save(held.with_(tool_uses=1), USER)
        loads = LoadTally.ended()
        agents.save(counted, USER)
        agents.save(counted.with_(work_queue=AgentLoad(rho=0.5, measured_at=1.0)), USER)
        changes = [entry.data["changed"] for entry in entries.all_matching(entry_type="updated")]
    assert [(load.model, load.rows) for load in loads.counts if load.rows] == [], f"the row as it was comes from the session read the cache holds: {loads.line()}"
    assert changes == [["tool_uses"]], "a save that changed nothing and a change of the load alone are no timeline entries"


def test_a_setting_saved_with_the_value_it_holds_writes_nothing_and_a_listener_of_the_write_reads_what_it_wrote(connection, bus, scope):
    from journal.repositories.load_tally import LoadTally
    from journal.repositories.setting_rows import SettingRows
    settings = SettingRows(connection, bus, scope, TimeSource())

    class ModeReader(Listener[Saved]):
        def __init__(self) -> None:
            self.seen = []

        def handle(self, event: Saved) -> None:
            self.seen.append(settings.project("workers.mode"))

    with scope.environment(1):
        settings.set("workers.mode", "builder", USER)
        LoadTally.begin()
        settings.set("workers.mode", "builder", USER)
        loads = LoadTally.ended()
        reader = ModeReader()
        bus.listen(Saved, reader)
        settings.set("workers.mode", "orchestrator", USER)
        assert [load.writes for load in loads.counts if load.writes] == [], "the value it holds is written no more"
        assert reader.seen == ["orchestrator"] and settings.project("workers.mode") == "orchestrator", "a listener of the write reads the value written"


def test_a_setting_is_the_projects_read_the_same_in_every_environment_and_one_stored_for_an_environment_moves_to_the_project(connection, bus, scope):
    from journal.db.migrations.project_wide_settings import ProjectWideSettings
    from journal.models.setting import Setting
    from journal.repositories.setting_rows import SettingRows
    settings = SettingRows(connection, bus, scope, TimeSource())
    with scope.environment(1):
        settings.set("workers.mode", "orchestrator", USER)
    with scope.environment(2):
        assert settings.project("workers.mode") == "orchestrator" and settings.tree()["workers"]["mode"] == "orchestrator", "set in one environment, it reads the same in another"
        settings.set("workers.mode", "builder", USER)
    with scope.environment(1):
        assert settings.project("workers.mode") == "builder", "and written in that other, the first reads it too"
    for environment_id, key, value in ((2, "faults.developer", True), (3, "faults.developer", False), (2, "workers.mode", "solo")):
        settings.save(Setting(environment_id=environment_id, key=key, value=value), USER)
    ProjectWideSettings().apply(connection)
    rows = {(row["environment_id"], row["key"]): json.loads(row["value"]) for row in connection.all("SELECT environment_id, key, value FROM settings")}
    assert rows == {(0, "workers.mode"): "builder", (0, "faults.developer"): False}, "a key held only for environments moves to the project, its newest row kept, and the project's own value stands"
    booted = SettingRows(connection, bus, scope, TimeSource())
    with scope.environment(3):
        assert booted.project("faults.developer") is False and booted.project("workers.mode") == "builder", "after the move every environment reads the project's values"


def test_the_settings_page_has_no_applies_to_environment_tag():
    from pathlib import Path
    page = (Path(__file__).resolve().parents[1] / "src" / "web" / "src" / "pages" / "SettingsPage.vue").read_text()
    assert "Applies to environment" not in page and "settings-scope" not in page


def test_a_migration_that_raises_is_rolled_back_reported_retried_next_boot_and_the_ones_after_it_ran(connection):
    from journal.db.migration import Migration
    from journal.db.migration_failures import MigrationFailures
    from journal.db.migrator import Migrator
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels

    class Makes(Migration):
        def __init__(self, number: int, table: str, fails: bool = False) -> None:
            self.number, self.table, self.fails = number, table, fails

        def apply(self, connection) -> None:
            connection.execute(f"CREATE TABLE {self.table} (id INTEGER)")
            if self.fails:
                raise RuntimeError("the rows differ from ours")

    schema = Schema(connection, AllModels.MODELS)
    tables = lambda: {row["name"] for row in connection.all("SELECT name FROM sqlite_master WHERE type = 'table'")}
    failures = MigrationFailures()
    first_run = Migrator(connection, schema, (Makes(9001, "first_made"), Makes(9002, "second_made", fails=True), Makes(9003, "third_made")), failures).run()
    assert [m.number for m in first_run] == [9001, 9003] and "second_made" not in tables() and {"first_made", "third_made"} <= tables(), "the failed one is rolled back and the ones after it ran"
    assert [(f.number, "the rows differ from ours" in f.error) for f in failures.rows] == [(9002, True)] and "9002" in failures.lines()[0] and "tried again at the next start" in failures.lines()[0], "it is reported with its number and its error"
    later = MigrationFailures()
    second_run = Migrator(connection, schema, (Makes(9001, "first_made"), Makes(9002, "second_made"), Makes(9003, "third_made")), later).run()
    assert [m.number for m in second_run] == [9002] and not later.rows and "second_made" in tables(), "it was left unrecorded, so the next boot runs it again"


def test_the_delegated_flag_migration_gives_every_delegated_task_the_state_it_really_has(connection):
    from journal.db.migrations.delegated_flag import DelegatedFlag
    kind_columns(connection)
    for number, state in ((1, "delegated"), (2, "delegated"), (3, "open"), (4, "delegated")):
        connection.execute("INSERT INTO tasks (id, environment_id, title, state, created_at, creator) VALUES (?, 1, 't', ?, '2026-10-25', 'system')", (number, state))
    connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES ('workers:1', 'tasks:1', 'in_hand', '2026-10-25', 'system')")
    connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES ('workers:2', 'tasks:2', 'queued_for', '2026-10-25', 'system')")
    connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES ('workers:3', 'tasks:4', 'finished_unmerged', '2026-10-25', 'system')")
    DelegatedFlag().apply(connection)
    rows = {row["id"]: (row["state"], row["delegated"]) for row in connection.all("SELECT id, state, delegated FROM tasks")}
    assert rows == {1: ("started", 1), 2: ("open", 1), 3: ("open", 0), 4: ("open", 1)}, "held in hand is started, queued or finished and not merged is open, all flagged, and the rest not flagged"


def test_an_old_reports_table_gets_its_abstracts_written_and_checked_by_the_database(tmp_path):
    import sqlite3
    from journal.db.connection import Connection
    from journal.db.migrations.abstract_checks import AbstractChecks
    old = Connection(tmp_path / "old.db", Masks(SecretValues(Config(tmp_path))), StageTimes(), QueryTimes(), LargeReads())
    with old.transaction() as db:
        db.execute("CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, environment_id INTEGER, title TEXT, abstract TEXT, body TEXT)")
        db.execute("CREATE INDEX reports_environment ON reports (environment_id)")
        db.execute("INSERT INTO reports (environment_id, title, abstract, body) VALUES (1, 'The cart', '', '## Findings\n\n- The total adds the tax twice. It rounds after.\n')")
        db.execute("INSERT INTO reports (environment_id, title, abstract, body) VALUES (1, 'The pay page', NULL, '')")
        db.execute("INSERT INTO reports (environment_id, title, abstract, body) VALUES (1, 'Kept', 'What the login test found', 'body')")
    with old.transaction() as db:
        AbstractChecks().apply(db)
    abstracts = [row["abstract"] for row in old.all("SELECT abstract FROM reports ORDER BY id")]
    assert abstracts == ["The total adds the tax twice.", "The pay page", "What the login test found"], f"an old report gets its body's first sentence, or its title, and a fit one is kept: {abstracts}"
    assert old.all("SELECT name FROM sqlite_master WHERE type = 'index' AND name = 'reports_environment'"), "its indexes are made again"
    for unfit in ("", "x" * 201):
        with pytest.raises(sqlite3.IntegrityError):
            with old.transaction() as db:
                db.execute("INSERT INTO reports (environment_id, title, abstract, body) VALUES (1, 't', ?, 'b')", (unfit,))
    with old.transaction() as db:
        AbstractChecks().apply(db)
    assert len(old.all("SELECT id FROM reports")) == 3, "a table already checked is left as it is"


def test_the_sequence_step_records_migration_turns_a_stored_string_step_into_a_record(connection):
    """Migration 67: a sequence's step stored as a string becomes a record, its instructions, with file edits allowed."""
    from journal.db.migrations.sequence_step_records import SequenceStepRecords
    connection.execute("INSERT INTO sequences (title, steps, created_at, creator) VALUES ('release', '[\"tag it\", \"push it\"]', '2026-10-26', 'system')")
    SequenceStepRecords().apply(connection)
    steps = json.loads(connection.one("SELECT steps FROM sequences")["steps"])
    assert steps[0] == {"title": "", "instructions": "tag it", "file_edits_allowed": True, "allowed_commands": [], "ending_moment": ""} and steps[1]["instructions"] == "push it", steps


def test_the_sequence_runs_stacked_migration_pushes_each_kept_run_as_a_sequence_state_and_drops_the_runs_column(connection):
    """Migration 68: the runs kept on an agent's row become sequence states on its stack, the run in hand on top, string steps as records and a pause reason under its present name, and the runs column is dropped."""
    from journal.db.migrations.sequence_runs_stacked import SequenceRunsStacked
    from journal.features.sequences.support.stacked_runs import StackedRuns
    from journal.models.agent import Agent
    connection.execute("ALTER TABLE agents ADD COLUMN sequence_runs TEXT DEFAULT '[]'")
    runs = [{"sequence_id": 1, "title": "outer", "steps": ["a", "b"], "step": 1, "suspension_reason": "a question first"}, {"sequence_id": 2, "title": "inner", "steps": ["c"], "step": 0, "adopted_at": "2026-10-26T10:00:00+00:00"}]
    connection.execute("INSERT INTO agents (session, stack, sequence_runs, created_at, creator) VALUES ('s1', ?, ?, '2026-10-26', 'system')", (json.dumps([{"state": "idle", "data": {}}]), json.dumps(runs)))
    SequenceRunsStacked().apply(connection)
    assert "sequence_runs" not in {row["name"] for row in connection.all("PRAGMA table_info(agents)")}, "the runs column is dropped"
    stack = json.loads(connection.one("SELECT stack FROM agents")["stack"])
    assert [layer["state"] for layer in stack] == ["idle", "following_sequence", "following_sequence"]
    stacked = StackedRuns.runs(Agent(session="s1", stack=tuple(stack)))
    assert [(run.sequence_id, run.step, run.text) for run in stacked] == [(1, 1, "b"), (2, 0, "c")] and stacked[-1].adopted_at, "the run in hand is on top, its step and its taking up kept"
    assert stacked[0].pause_reason == "a question first", "a pause reason stored under its old name is kept"


def test_a_sequence_step_stored_or_pulled_as_a_string_loads_as_a_step_record_with_file_edits_allowed():
    from journal.models.sequence import Sequence
    from journal.models.support.column import Column
    from journal.models.support.sequence_step import SequenceStep
    from typing import get_type_hints
    column = Column.build("steps", get_type_hints(Sequence)["steps"])
    steps = column.parsed(json.dumps(["tag it", {"title": "Push", "instructions": "push it", "file_edits_allowed": False, "allowed_commands": ["^git push"]}]))
    assert steps == (SequenceStep(instructions="tag it"), SequenceStep(title="Push", instructions="push it", file_edits_allowed=False, allowed_commands=("^git push",))), "a string from a peer on the old version is its instructions, file edits allowed"
    assert json.loads(column.sql(steps))[1]["allowed_commands"] == ["^git push"], "and a record is stored as a record"


def test_the_load_dispatch_counts_migration_renames_the_keys_of_every_stored_load(connection):
    from journal.db.migrations.load_dispatch_counts import LoadDispatchCounts
    from journal.models.support.agent_load import AgentLoad
    old = {"rho": 0.9, "dispatches_for": 1, "dispatches_against": 2, "over_minutes": 12.0, "under_minutes": 3.0}
    connection.execute("INSERT INTO agents (session, work_queue, message_queue, mode_loads, created_at, creator) VALUES ('s1', ?, ?, ?, '2026-10-26', 'system')", (json.dumps(old), json.dumps({}), json.dumps({"builder": old})))
    LoadDispatchCounts().apply(connection)
    row = connection.one("SELECT work_queue, mode_loads FROM agents")
    load = AgentLoad.parsed(json.loads(row["work_queue"]))
    assert (load.calm_dispatches, load.busy_dispatches, load.busy_minutes, load.low_minutes) == (1, 2, 12.0, 3.0), "the counts and stretches keep their values under their plain names"
    assert AgentLoad.parsed(json.loads(row["mode_loads"])["builder"]).busy_dispatches == 2, "and so does the load of each work mode"


def test_a_memory_fades_by_one_at_a_time_and_at_nought_is_stored_but_no_longer_shown(connection, bus, scope):
    from journal.models.memory import Memory
    from journal.repositories.memories import Memories
    memories = Memories(connection, bus, scope, Links(connection, bus, TimeSource()), TimeSource())
    with scope.environment(1):
        light = memories.save(Memory(text="the port is fixed", weight=1), USER)
        heavy = memories.save(Memory(text="the suite runs in shards", weight=7), USER)
        removed = memories.save(Memory(text="an old truth", weight=9).removed(datetime.now(timezone.utc)), USER)
        assert [m.id for m in memories.shown()] == [heavy.id, light.id], "the shown memories, heaviest first, never a removed one"
        memories.fade_all(None, Actor.system())
        assert [(m.id, m.weight) for m in memories.shown()] == [(heavy.id, 6)], "a compaction lowers every weight by one, and one at nought leaves what is shown"
        assert memories.find(light.id).weight == 0 and memories.find(removed.id).weight == 9, "it stays on its row, and a removed one is not faded"
        assert memories.find(light.id).weighed(4).is_visible(), "weighing a faded memory above nought shows it again"
        with pytest.raises(Rejection, match="from 1 to 10"):
            heavy.weighed(11)
        with pytest.raises(Rejection, match="already removed"):
            memories.find(removed.id).removed(datetime.now(timezone.utc))


def test_the_fact_memories_migration_makes_each_standing_fact_a_memory_of_weight_five_once(connection):
    """Migration 72: every fact still in the table, a struck one being gone from it, becomes a memory of weight 5 in its environment with its text and keywords, and a second run adds nothing."""
    from journal.db.migrations.fact_memories import FactMemories
    connection.execute("CREATE TABLE facts (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, creator TEXT, updated_at TEXT, updater TEXT, environment_id INTEGER, text TEXT, keywords TEXT)")
    connection.execute("INSERT INTO facts (environment_id, text, keywords, created_at, creator) VALUES (1, 'the port is fixed', '[\"port\"]', '2026-10-27', 'system'), (2, 'the suite runs in shards', '[]', '2026-10-27', 'system')")
    FactMemories().apply(connection)
    FactMemories().apply(connection)
    rows = [(row["environment_id"], row["text"], row["weight"], row["keywords"]) for row in connection.all("SELECT environment_id, text, weight, keywords FROM memories ORDER BY id")]
    assert rows == [(1, "the port is fixed", 5, '["port"]'), (2, "the suite runs in shards", 5, "[]")], rows


def test_the_fact_table_drop_moves_each_fact_card_to_its_memory_and_drops_the_table(connection):
    """Migration 73: a card that opened a fact opens the memory made of it, shown as a memory card; a card whose fact had no memory keeps its words and opens nothing; the facts table goes."""
    import json
    from journal.db.migrations.fact_table_drop import FactTableDrop
    connection.execute("CREATE TABLE facts (id INTEGER PRIMARY KEY AUTOINCREMENT, environment_id INTEGER, text TEXT)")
    connection.execute("INSERT INTO facts (environment_id, text) VALUES (1, 'the port is fixed'), (1, 'a fact with no memory')")
    connection.execute("INSERT INTO memories (environment_id, text, weight, created_at, creator) VALUES (1, 'the port is fixed', 5, '2026-10-27', 'system')")
    memory = connection.one("SELECT id FROM memories")["id"]
    for number in (1, 2):
        connection.execute("INSERT INTO messages (environment_id, text, data, created_at, creator) VALUES (1, ?, ?, '2026-10-27', 'system')", (f"Fact {number} recorded", json.dumps({"kind": "card", "row": f"facts:{number}", "shows": "facts"})))
    FactTableDrop().apply(connection)
    cards = [(row["text"], json.loads(row["data"])) for row in connection.all("SELECT text, data FROM messages ORDER BY id")]
    assert cards[0] == (f"Memory {memory} recorded", {"kind": "card", "row": f"memories:{memory}", "shows": "memories"})
    assert cards[1] == ("Fact 2 recorded", {"kind": "card", "shows": "memories"})
    assert not connection.all("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'facts'")


def test_a_load_stored_by_an_older_version_reads_with_its_keys_renamed_and_the_retired_ones_left_out():
    from journal.models.support.agent_load import AgentLoad
    load = AgentLoad.parsed({"under_minutes": 3.0, "over_minutes": 2.0, "dispatches_for": 1, "a_retired_key": 7, "waiting_refs": ["tasks:1"]})
    assert (load.low_minutes, load.busy_minutes, load.calm_dispatches, load.waiting_refs) == (3.0, 2.0, 1, ("tasks:1",)), "an agent row an older journal wrote boots with its load read, never a crash at the start"


def test_a_line_an_older_version_recorded_without_its_values_is_left_out_of_the_values_read_back(connection, bus, scope):
    from journal.repositories.entries import Entries, NUDGE
    entries = Entries(connection, bus, scope, TimeSource())
    with scope.environment(1):
        entries.save(Entry(environment_id=1, entry_type=NUDGE, actor=Actor.system(), data={"key": "shell.add_a_reader", "session": "s1", "line": "an older line", "time": 1.0}), Actor.system())
        entries.save(Entry(environment_id=1, entry_type=NUDGE, actor=Actor.system(), data={"key": "shell.add_a_reader", "values": {"command": "pytest"}, "session": "s1", "line": "a line", "time": 2.0}), Actor.system())
        assert entries.environment_values("shell.add_a_reader", "command") == ["pytest"], "a line recorded before lines kept their values is no fault at every tool use"
        assert entries.project_values("shell.add_a_reader", "command") == {"pytest": 2.0}


def plans_of(connection, bus, scope) -> Plans:
    from journal.repositories.templates import Templates
    links, tasks = Links(connection, bus, TimeSource()), tasks_of(connection, bus, scope)
    return Plans(connection, bus, scope, links, tasks, Phases(connection, bus, scope, TimeSource()), Workers(connection, bus, scope, links, Rows(connection), tasks, TimeSource()), Templates(connection, bus, TimeSource()), TimeSource())


def test_the_plan_modes_migration_makes_every_plan_from_before_a_solo_one(connection, bus, scope):
    """Migration 77 on a plans table from before plans had a mode: the schema adds the column empty, every plan there reads as solo, and a plan given a mode since keeps it."""
    from journal.db.migrations.plan_modes import PlanModes
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.models.plan_mode import PlanMode
    connection.execute("ALTER TABLE plans DROP COLUMN mode")
    for title, state in (("the floors", "draft"), ("the roof", "started")):
        connection.execute("INSERT INTO plans (environment_id, title, state, created_at, creator) VALUES (1, ?, ?, '2026-10-28', 'system')", (title, state))
    Schema(connection, AllModels.MODELS).create()
    connection.execute("INSERT INTO plans (environment_id, title, state, mode, created_at, creator) VALUES (1, 'the walls', 'draft', 'organization', '2026-10-29', 'system')")
    PlanModes().apply(connection)
    with scope.environment(1):
        modes = {plan.title: plan.mode for plan in plans_of(connection, bus, scope).scoped()}
    assert modes == {"the floors": PlanMode.SOLO, "the roof": PlanMode.SOLO, "the walls": PlanMode.ORGANIZATION}, "a plan from before is solo and a plan with a mode keeps it"


def test_a_plans_agent_and_rig_are_links_from_the_plan_never_columns_on_it(connection, bus, scope):
    """A plan's Plan agent and its rig are each a link of its own kind from the plan, read back by id, and a plan with neither reads 0; the plans table holds no column for either."""
    from journal.models.agent import Agent
    from journal.models.plan import Plan
    from journal.models.plan_mode import PlanMode
    from journal.models.rig import Rig
    from journal.repositories.plans import PLAN_AGENT_LINK, RIG_LINK
    from journal.repositories.rigs import Rigs
    plans = plans_of(connection, bus, scope)
    with scope.environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors", mode=PlanMode.ORGANIZATION), USER)
        solo = plans.save(Plan(environment_id=1, title="the roof"), USER)
        agent = Agents(connection, bus, scope, TimeSource()).save(Agent(environment_id=1, session="s1", provider="claude"), USER)
        rig = Rigs(connection, bus, scope, TimeSource()).save(Rig(environment_id=1, name="plan-1"), USER)
        plans.agent_linked(plan, agent, AGENT)
        plans.agent_linked(plan, agent, AGENT)
        plans.rig_linked(plan, rig, AGENT)
        assert (plans.find(plan.id).mode, plans.agent_id(plan), plans.rig_id(plan)) == (PlanMode.ORGANIZATION, agent.id, rig.id)
        assert (plans.find(solo.id).mode, plans.agent_id(solo), plans.rig_id(solo)) == (PlanMode.SOLO, 0, 0), "a plan is solo unless made otherwise and has neither link until one is made"
    kinds = [link.link_type for link in Links(connection, bus, TimeSource()).link_rows(plan)]
    assert kinds == [PLAN_AGENT_LINK, RIG_LINK], "linking the same agent twice leaves one link"
    columns = {row["name"] for row in connection.all("PRAGMA table_info(plans)")}
    assert "mode" in columns and not columns & {"agent_id", "plan_agent", "rig", "rig_id"}, "the relations are rows, not foreign keys"

def test_a_sequence_template_and_profile_travel_as_portable_bodies_and_come_back_whole():
    from journal.features.library.support.portable_body import PortableBody
    from journal.features.library.support.profile_body import ProfileBody
    from journal.features.library.support.sequence_body import SequenceBody
    from journal.features.library.support.template_body import TemplateBody
    from journal.models.sequence import Sequence
    from journal.models.support.sequence_step import SequenceStep
    from journal.models.support.sequence_trigger import SequenceTrigger
    from journal.models.template import Template
    from journal.providers.support.profile import Profile
    from journal.providers.support.profile_type import ProfileType
    sequence = Sequence(id=4, title="Release", steps=(SequenceStep("Tag", "tag it", False, ("^git tag",), ""), SequenceStep("Push", "push it")), triggers=(SequenceTrigger.row("plan.finished"), SequenceTrigger.phrase("ship it")), locked=True)
    back = SequenceBody.sequence(SequenceBody.text(sequence))
    assert (back.title, back.steps, back.triggers, back.locked, back.id) == ("Release", sequence.steps, sequence.triggers, False, None), "only the number, the stamps and the lock are left behind"
    assert SequenceBody.text(back) == SequenceBody.text(sequence) and PortableBody.hash(SequenceBody.text(back)) == PortableBody.hash(SequenceBody.text(sequence)), "an unedited copy hashes the same"
    template = Template(title="Find what is missing", targets=("plan",), purpose="critique", brief="read it", parts=("Gaps: what is missing",))
    assert TemplateBody.template(TemplateBody.text(template)) == template
    profile = Profile("journal-scout", "reads", "Read, Grep", "You read.", ProfileType.SUBAGENT, model="opus")
    assert ProfileBody.profile(ProfileBody.text(profile)) == Profile("journal-scout", "reads", "Read, Grep", "You read.", ProfileType.SUBAGENT), "the model a machine sets stays behind"


def test_every_actor_stamp_reads_back_as_its_kinds_class_with_the_same_stamp():
    from journal.support.actor import Actor
    from journal.support.actor_type import ActorType
    from journal.support.agent_actor import AgentActor
    from journal.support.subagent_actor import SubagentActor
    stamps = [kind.value if kind == ActorType.SYSTEM else f"{kind.value}:7" for kind in ActorType] + ["agent:s1:a2"]
    for stamp in stamps:
        actor = Actor.parse(stamp)
        assert actor.stamp == stamp and type(actor) is not Actor and Actor.parse(actor.stamp) == actor, stamp
    assert type(Actor.parse("agent:s1")) is AgentActor and type(Actor.parse("agent:s1:a2")) is SubagentActor, "a subagent's stamp is its own kind"
