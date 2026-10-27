from journal.support.large_reads import LargeReads
from journal.support.query_times import QueryTimes
from journal.support.stage_times import StageTimes
from datetime import datetime, timezone
from journal.events.announcer import Announcer
from journal.events.moments.sync_moment import SyncMoment
from journal.features.team.listeners.sync_moment_cards import SyncMomentCards
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
from journal.models.environment_type import EnvironmentType
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.links import Links
from journal.repositories.agents import Agents
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.users import Users
from journal.support.missing_row import MissingRow
from journal.repositories.checks import Checks
from journal.repositories.questions import Questions
from journal.repositories.tasks import Tasks
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
    return Tasks(connection, bus, scope, Links(connection, bus, TimeSource()), Questions(connection, bus, scope, TimeSource()), Checks(connection, bus, TimeSource()), TimeSource())


class SayNo(Listener[Creating]):
    def handle(self, event):
        raise Rejection("not today")


def test_a_saved_task_gets_an_id_and_the_actor_stamp(connection, bus, scope):
    tasks = tasks_of(connection, bus, scope)
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
    task = tasks.save(Task(environment_id=1, title="t"), actor=USER)
    tasks.save(task.with_(state=TaskState.STARTED), actor=AGENT)
    tasks.delete(task, actor=USER)
    kinds = [type(e).__name__ for e in heard.events]
    assert kinds == ["Saving", "Creating", "Created", "Saved", "Saving", "Updating", "Updated", "Saved", "Deleting", "Deleted"]
    assert heard.events[5].actor == AGENT and heard.events[5].model.state == TaskState.STARTED
    with pytest.raises(MissingRow):
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
    scope = Scope(Environments(old, bus, TimeSource()), Links(old, bus, TimeSource()))
    message = Messages(old, bus, scope, Reactions(old, bus, scope, Links(old, bus, TimeSource()), TimeSource()), Links(old, bus, TimeSource()), EnvironmentOwners(Links(old, bus, TimeSource()), Users(old, bus, TimeSource()), Environments(old, bus, TimeSource())), Agents(old, bus, scope, TimeSource()), TimeSource()).find(1)
    assert message.files == () and message.acknowledgement is False and message.idempotency == "" and message.read_at is None


def test_a_title_is_one_line_of_eighty_characters_without_a_colon_and_an_old_one_is_left_alone(connection, bus, scope):
    from journal.support.actor import Actor
    from journal.models.task import Task
    from journal.support.rejection import Rejection
    from journal.repositories.tasks import Tasks
    tasks = tasks_of(connection, bus, scope)
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
    """The workers table as journals kept it before workers and verifiers shared the table of sent agents, for the migrations that ran on it."""
    from journal.db.schema import Schema
    from journal.models.worker import Worker
    columns = ", ".join(f"{column.name} {column.sql_type}" for column in Schema.columns(Worker) if column.name not in ("id", "helper_type"))
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
    connection.execute("ALTER TABLE tasks RENAME COLUMN pause_reason TO suspension_reason")
    connection.execute("INSERT INTO tasks (environment_id, title, state, suspension_reason, created_at, creator) VALUES (1, 'the parser', 'parked', 'waits on the lexer', '2026-10-23', 'system')")
    connection.execute("INSERT INTO plans (environment_id, title, state, created_at, creator) VALUES (1, 'release', 'parked', '2026-10-23', 'system')")
    PausedTasks().apply(connection)
    task = connection.one("SELECT state, pause_reason FROM tasks")
    assert (task["state"], task["pause_reason"]) == ("paused", "waits on the lexer") and connection.one("SELECT state FROM plans")["state"] == "paused"


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


def test_the_environment_teams_migration_makes_the_team_chat_a_session_gives_shared_environments_the_team_key_and_puts_documents_in_the_project(tmp_path):
    """Migration 52 on a copy of a pre-hub database: no row is lost, the Team chat is a session in the team, a shared environment carries the team's key, one known later as unknown, the flags go, and every document is in environment 0."""
    import json
    from journal.config import Config
    from journal.db.connection import Connection
    from journal.db.migrations.environment_teams import EnvironmentTeams
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.support.large_reads import LargeReads
    from journal.support.masks import Masks
    from journal.support.query_times import QueryTimes
    from journal.support.secret_values import SecretValues
    from journal.support.stage_times import StageTimes
    from journal.sync.team_account import TEAM_FILE, TEAMS_FOLDER

    def migrated(root, account: dict, filename: str) -> Connection:
        config = Config(root)
        (config.home / TEAMS_FOLDER).mkdir(parents=True)
        (config.home / filename).write_text(json.dumps(account))
        connection = Connection(config.database, Masks(SecretValues(config)), StageTimes(), QueryTimes(), LargeReads())
        Schema(connection, AllModels.MODELS).create()
        kind_columns(connection)
        connection.execute("ALTER TABLE environments ADD COLUMN is_team_chat INTEGER NOT NULL DEFAULT 0")
        connection.execute("ALTER TABLE environments ADD COLUMN is_shared_with_team INTEGER NOT NULL DEFAULT 0")
        for name, team_chat, shared in (("main", 0, 0), ("team", 1, 0), ("ada-docs", 0, 1)):
            connection.execute("INSERT INTO environments (name, key, kind, team_key, is_team_chat, is_shared_with_team, created_at, creator) VALUES (?, lower(hex(randomblob(16))), 'local', '', ?, ?, '2026-10-24', 'system')", (name, team_chat, shared))
        connection.execute("INSERT INTO docs (title, abstract, body, created_at, creator) VALUES ('Handbook', 'How we work', 'how we work', '2026-10-24', 'system')")
        connection.execute("INSERT INTO doc_revisions (number, title, body, created_at, creator) VALUES (1, 'Handbook', 'how we work', '2026-10-24', 'system')")
        with connection.transaction() as db:
            EnvironmentTeams().apply(db)
        return connection

    keyed = migrated(tmp_path / "keyed", {"address": "https://team.example", "team_key": "k1", "team_number": 0}, f"{TEAMS_FOLDER}/k1.json")
    rows = {row["name"]: (row["kind"], row["team_key"]) for row in keyed.all("SELECT name, kind, team_key FROM environments")}
    assert rows == {"main": ("local", ""), "team": ("session", "k1"), "ada-docs": ("local", "k1")}, "no environment is lost, the Team chat is a session in the team and the shared one carries its key"
    assert not {"is_team_chat", "is_shared_with_team"} & {row["name"] for row in keyed.all("PRAGMA table_info(environments)")}, "the flags they were marked by are gone"
    assert [(row["title"], row["environment_id"]) for row in keyed.all("SELECT title, environment_id FROM docs UNION ALL SELECT title, environment_id FROM doc_revisions")] == [("Handbook", 0)] * 2, "every document and revision from before is the project's"
    keyed.close()
    unkeyed = migrated(tmp_path / "unkeyed", {"address": "https://team.example"}, TEAM_FILE)
    assert {row["name"]: row["team_key"] for row in unkeyed.all("SELECT name, team_key FROM environments")} == {"main": "", "team": "unknown", "ada-docs": "unknown"}, "a journal that has not learnt its team's key places them in the team as unknown, which the sync names once the server does"
    unkeyed.close()


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


def test_the_tasks_repository_answers_which_tasks_are_open_blocked_paused_and_unclosed(connection, bus, scope):
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
        paused = tasks.save(Task(environment_id=1, title="paused", state=TaskState.PAUSED), actor=USER)
        done = tasks.save(Task(environment_id=1, title="done", state=TaskState.COMPLETED), actor=USER)
        draft = PlanRows(connection, bus, scope, TimeSource()).save(Plan(environment_id=1, title="p", state=PlanState.DRAFT), USER)
        links.save(Link(source=Ref.build(drafted), target=Ref.build(draft), link_type=PLAN_LINK), actor=USER)
        assert [task.id for task in tasks.open_tasks()] == [free.id], "a task of an unapproved plan is no open work"
        assert [task.id for task in tasks.blocked_tasks()] == [blocked.id]
        assert [task.id for task in tasks.paused_tasks()] == [paused.id]
        assert done.id not in [task.id for task in tasks.unclosed_tasks()] and free.id in [task.id for task in tasks.unclosed_tasks()]
        assert tasks.unfinished_ids([free.id, done.id]) == [free.id]


def test_each_model_says_whether_it_is_shared_with_the_team_or_kept_on_one_machine():
    from journal.models.all_models import AllModels
    local = sorted(model.__name__ for model in AllModels.MODELS if not model.shared)
    assert local == sorted(["Entry", "Agent", "Statistic", "CommandOutput", "DashboardRow", "Secret", "Phone", "PhoneCode", "MigratedRow", "Version3Migration", "JournalVersion", "ReleaseMessage", "ReaderReport", "ReaderSuggestion", "OutgoingChange", "IdBlock", "PendingUpload", "Plugin", "McpServer", "BrowserSession", "PoolJob", "ScheduledJob", "TestTurn", "Verifier", "Reviewer"]), "the models kept on one machine are the ones NOTES.md names"
    assert all(model.shared for model in AllModels.MODELS if model.__name__ in ("Task", "Message", "Alias", "Worker", "Setting")), "everything else is shared"


def test_each_write_to_a_shared_row_is_queued_for_the_team_once_joined_and_waiting_writes_to_a_row_merge(connection, bus, scope, tmp_path):
    from journal.config import Config
    from journal.events.models.model_event import ModelEvent
    from journal.models.release_message import ReleaseMessage
    from journal.repositories.outgoing_changes import OutgoingChanges
    from journal.repositories.release_messages import ReleaseMessages
    from journal.sync.team_account import TEAM_FILE, TeamAccount

    config = Config(tmp_path)
    changes, tasks = OutgoingChanges(connection, bus, TimeSource()), tasks_of(connection, bus, scope)
    bus.listen(ModelEvent, outgoing_recorder(connection, bus, scope, config, changes))
    with scope.environment(1):
        before = tasks.save(Task(environment_id=1, title="before joining"), actor=USER)
        assert changes.waiting() == [], "a journal in no team queues nothing"
        config.home.mkdir(parents=True, exist_ok=True)
        (config.home / TEAM_FILE).write_text("{}")
        task = tasks.save(Task(environment_id=1, title="first"), actor=USER)
        task = tasks.save(task.with_(title="second"), actor=AGENT)
        task = tasks.save(task.with_(brief="a brief"), actor=USER)
        [created] = changes.waiting()
        assert (created.row_table, created.row, created.action) == ("tasks", task.id, "created")
        assert (created.fields["title"], created.fields["brief"], created.writer) == ("second", "a brief", USER.stamp), "a creation and its updates are one creation"
        assert set(created.changed_at) == set(created.fields)
        before = tasks.save(before.with_(title="renamed"), actor=USER)
        before = tasks.save(before.with_(brief="a second brief"), actor=USER)
        update = changes.waiting()[1]
        assert update.action == "updated" and set(update.fields) == {"title", "brief", "updated_at", "updater"}, "two updates are one, with only the columns they changed"
        tasks.delete(task, USER)
        assert [change.row for change in changes.waiting()] == [before.id], "a row created and deleted before sending sends nothing"
        changes.save(changes.waiting()[0].with_(is_sending=True), USER)
        tasks.save(before.with_(title="again"), actor=USER)
        assert [change.fields["title"] for change in changes.waiting()] == ["again"], "a change being sent is never merged into"
        tasks.delete(before, USER)
        assert changes.waiting()[0].action == "deleted" and changes.waiting()[0].fields == {}
        ReleaseMessages(connection, bus, TimeSource()).save(ReleaseMessage(version="9.9.9", text="local"), USER)
        assert [change.row_table for change in changes.waiting()] == ["tasks"], "a model kept on one machine is never queued"


def test_a_new_shared_row_takes_its_number_from_the_machines_blocks_once_joined_and_from_sqlite_before(connection, bus, scope, tmp_path):
    from journal.config import Config
    from journal.events.models.number_request import NumberRequest
    from journal.models.release_message import ReleaseMessage
    from journal.repositories.id_blocks import IdBlocks
    from journal.repositories.release_messages import ReleaseMessages
    from journal.repositories.number_shortage import NumberShortage
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.block_supply import BlockSupply
    from journal.sync.team_server_link import TeamServerLink
    from journal.sync.block_numbers import BlockNumbers
    from journal.sync.team_account import TEAM_FILE, TeamAccount

    config, blocks, tasks = Config(tmp_path), IdBlocks(connection, bus, TimeSource()), tasks_of(connection, bus, scope)
    bus.listen(NumberRequest, block_numbers(connection, bus, scope, config, blocks))
    with scope.environment(1):
        assert [tasks.save(Task(environment_id=1, title=title), actor=USER).id for title in "ab"] == [1, 2], "a journal in no team numbers as before"
        config.home.mkdir(parents=True, exist_ok=True)
        (config.home / TEAM_FILE).write_text(json.dumps({"address": "http://127.0.0.1:9"}))
        blocks.add("tasks", 1001, 1003)
        blocks.add("tasks", 2001, 2010)
        assert [tasks.save(Task(environment_id=1, title=str(n)), actor=USER).id for n in range(4)] == [1001, 1002, 1003, 2001], "past a block's end the next block numbers"
        assert blocks.is_wanted("tasks") and blocks.is_wanted("messages"), "nine numbers left of a block of ten wants another, and a table with no block wants one"
        blocks.add("tasks", 3001, 3010)
        assert not blocks.is_wanted("tasks"), "a block and a fifth of one left is enough"
        assert ReleaseMessages(connection, bus, TimeSource()).save(ReleaseMessage(version="9.9.9"), USER).id == 1, "a model kept on one machine is numbered by SQLite"
        for _ in range(19):
            tasks.save(Task(environment_id=1, title="more"), actor=USER)
        with pytest.raises(NumberShortage):
            tasks.save(Task(environment_id=1, title="one too many"), actor=USER)
        assert not issubclass(NumberShortage, Rejection), "a shortage is a fault, so a hook lets its event through instead of refusing it"


def block_numbers(connection, bus, scope, config, blocks):
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.repositories.environments import Environments
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.block_numbers import BlockNumbers
    from journal.sync.block_supply import BlockSupply
    from journal.sync.team_account import TeamAccount
    from journal.sync.team_accounts import TeamAccounts
    from journal.sync.team_server_link import TeamServerLink

    supply = BlockSupply(TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS)), blocks, SharedTables(connection, bus, TimeSource()), TeamAccount(config))
    return BlockNumbers(blocks, TeamAccount(config), supply, team_placement(connection, bus, scope, config), TeamAccounts(config, Environments(connection, bus, TimeSource())))


def outgoing_recorder(connection, bus, scope, config, changes):
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.repositories.id_blocks import IdBlocks
    from journal.repositories.shared_tables import SharedTables
    from journal.services.service_hooks import ServiceHooks
    from journal.sync.block_supply import BlockSupply
    from journal.sync.record_outgoing_change import RecordOutgoingChange
    from journal.sync.row_renumbering import RowRenumbering
    from journal.sync.team_account import TeamAccount
    from journal.sync.team_server_link import TeamServerLink

    account, blocks, tables = TeamAccount(config), IdBlocks(connection, bus, TimeSource()), SharedTables(connection, bus, TimeSource())
    renumbering = RowRenumbering(connection, blocks, BlockSupply(TeamServerLink(account, Schema(connection, AllModels.MODELS)), blocks, tables, account), config)
    from journal.repositories.environments import Environments
    from journal.sync.team_accounts import TeamAccounts
    return RecordOutgoingChange(changes, account, team_placement(connection, bus, scope, config), Links(connection, bus, TimeSource()), tables, renumbering, TeamAccounts(config, Environments(connection, bus, TimeSource())), ServiceHooks())


def team_placement(connection, bus, scope, config):
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.team_account import TeamAccount
    from journal.sync.team_placement import TeamPlacement

    return TeamPlacement(SharedTables(connection, bus, TimeSource()), team_scopes(connection, bus, scope), TeamAccount(config))


def team_scopes(connection, bus, scope):
    from journal.features.registry import Registry
    from journal.features.standard import Standard
    from journal.repositories.setting_rows import SettingRows
    from journal.sync.setting_scopes import SettingScopes
    from journal.helpers.helpers import Helpers

    return SettingScopes(Registry(Standard.FEATURES, SettingRows(connection, bus, scope, TimeSource()), (), Helpers.ALL))


def environment_withdrawal(config, connection, bus, scope):
    from journal.repositories.environment_owners import EnvironmentOwners
    from journal.repositories.shared_tables import SharedTables
    from journal.repositories.users import Users
    from journal.sync.environment_withdrawal import EnvironmentWithdrawal
    from journal.sync.team_account import TeamAccount

    return EnvironmentWithdrawal(TeamAccount(config), SharedTables(connection, bus, TimeSource()), Links(connection, bus, TimeSource()), EnvironmentOwners(Links(connection, bus, TimeSource()), Users(connection, bus, TimeSource()), scope.environments), team_scopes(connection, bus, scope))


def team_migration(tmp_path, name: str, scope, tasks, outgoing):
    """The move to the hub on the team journal of that name, as team_journal made it, reaching the team server its team file names."""
    from journal.config import Config
    from journal.db.schema import Schema
    from journal.features.team.support.team_migration import TeamMigration
    from journal.models.all_models import AllModels
    from journal.repositories.doc_revisions import DocRevisions
    from journal.repositories.doc_scope import DocScope
    from journal.repositories.docs import Docs
    from journal.features.docs.support.hub_move import HubMove
    from journal.repositories.environment_owners import EnvironmentOwners
    from journal.repositories.journal_backup import JournalBackup
    from journal.repositories.shared_tables import SharedTables
    from journal.repositories.users import Users
    from journal.services.service_hooks import ServiceHooks
    from journal.sync.migration_withdrawal import MigrationWithdrawal
    from journal.sync.team_account import TeamAccount
    from journal.sync.team_placement import TeamPlacement
    from journal.sync.team_server_link import TeamServerLink

    config, connection, bus = Config(tmp_path / name), tasks.connection, tasks.bus
    tables, scopes, account, visible = SharedTables(connection, bus, TimeSource()), team_scopes(connection, bus, scope), TeamAccount(config), DocScope(scope.environments, scope)
    withdrawal = MigrationWithdrawal(outgoing, tables, environment_withdrawal(config, connection, bus, scope), scopes, ServiceHooks())
    owners = EnvironmentOwners(Links(connection, bus, TimeSource()), Users(connection, bus, TimeSource()), scope.environments)
    docs, revisions = Docs(connection, bus, scope, visible, TimeSource()), DocRevisions(connection, bus, scope, Links(connection, bus, TimeSource()), visible, TimeSource())
    return TeamMigration(account, TeamServerLink(account, Schema(connection, AllModels.MODELS)), scope.environments, owners, withdrawal, TeamPlacement(tables, scopes, account), docs, revisions, HubMove(docs, revisions), tables, JournalBackup(connection), config)


def migration_withdrawn(tmp_path, name: str, scope, tasks, outgoing, actor) -> None:
    """The migration's withdrawals planned and queued on the team journal of that name, with no hub made and no document moved."""
    migration = team_migration(tmp_path, name, scope, tasks, outgoing)
    migration.withdrawal.withdraw(tuple(migration.withdrawal.planned(actor.stamp, migration.placement)), actor)


def served_link(team, server, tmp_path, name: str, email: str, account_id: int) -> None:
    """The team file of the journal of that name, logged in as a new device of that person on the team server served over HTTP."""
    import json
    from journal.sync.team_account import TEAM_FILE

    _, token = team.devices.login(email, "correct horse battery", f"{name}'s migrating device", "10.0.0.9", 5.0)
    (tmp_path / name / ".journal" / TEAM_FILE).write_text(json.dumps({"account_id": account_id, "team_key": team.details.answer().key, "address": f"http://127.0.0.1:{server.server_address[1]}", "token": token}))


def team_journal(tmp_path, name: str):
    from journal.config import Config
    from journal.sync.block_supply import BlockSupply
    from journal.sync.team_server_link import TeamServerLink
    from journal.db.connection import Connection
    from journal.db.schema import Schema
    from journal.events.bus import Bus
    from journal.events.models.model_event import ModelEvent
    from journal.events.models.purged import Purged
    from journal.models.all_models import AllModels
    from journal.repositories.environments import Environments
    from journal.repositories.outgoing_changes import OutgoingChanges
    from journal.repositories.scope import Scope
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.incoming_changes import IncomingChanges
    from journal.sync.record_purge import RecordPurge
    from journal.sync.team_account import TEAM_FILE, TeamAccount
    from journal.features.listeners.unlink_deleted import UnlinkDeleted
    from journal.events.models.deleted import Deleted
    from journal.events.models.number_request import NumberRequest
    from journal.repositories.id_blocks import IdBlocks
    from journal.sync.block_numbers import BlockNumbers
    from journal.services.service_hooks import ServiceHooks
    from journal.events.rows.environment_unshared import EnvironmentUnshared
    from journal.events.models.synced_deletion import SyncedDeletion
    from journal.repositories.pending_uploads import PendingUploads
    from journal.sync.attachments import Attachments
    from journal.sync.pulled_file_removal import PulledFileRemoval
    from journal.sync.record_withdrawal import RecordWithdrawal
    from journal.repositories.journal_backup import JournalBackup

    folder = tmp_path / name
    config = Config(folder)
    config.home.mkdir(parents=True)
    (config.home / TEAM_FILE).write_text("{}")
    connection = Connection(folder / "journal.db", Masks(SecretValues(config)), StageTimes(), QueryTimes(), LargeReads())
    Schema(connection, AllModels.MODELS).create()
    bus = Bus()
    scope = Scope(Environments(connection, bus, TimeSource()), Links(connection, bus, TimeSource()))
    outgoing = OutgoingChanges(connection, bus, TimeSource())
    bus.listen(ModelEvent, outgoing_recorder(connection, bus, scope, config, outgoing))
    bus.listen(Purged, RecordPurge(outgoing, TeamAccount(config), team_placement(connection, bus, scope, config), ServiceHooks()))
    blocks = IdBlocks(connection, bus, TimeSource())
    base = (ord(name[0]) - ord("a")) * 100_000
    for model in AllModels.MODELS:
        if model.shared:
            blocks.add(model.table(), base + 1, base + 99_999)
    bus.listen(NumberRequest, block_numbers(connection, bus, scope, config, blocks))
    bus.listen(Deleted, UnlinkDeleted(Links(connection, bus, TimeSource())))
    bus.listen(EnvironmentUnshared, RecordWithdrawal(outgoing, TeamAccount(config), environment_withdrawal(config, connection, bus, scope), ServiceHooks()))
    bus.listen(SyncedDeletion, PulledFileRemoval(Attachments(config, PendingUploads(connection, bus, TimeSource()), TeamAccount(config), TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS)))))
    return bus, scope, tasks_of(connection, bus, scope), outgoing, IncomingChanges(SharedTables(connection, bus, TimeSource()), outgoing, Links(connection, bus, TimeSource()), TeamAccount(config), JournalBackup(connection), config)


def team_changes(outgoing):
    from journal.sync.team_change import TeamChange

    changes = outgoing.waiting()
    for change in changes:
        outgoing.delete(change, USER)
    return [TeamChange(row_table=change.row_table, row=change.row, action=change.action, writer=change.writer, fields=change.fields or {}) for change in changes]


def test_two_journals_exchange_their_changes_and_a_pulled_write_runs_no_listener_of_a_local_write(tmp_path):
    from journal.events.listener import Listener
    from journal.events.models.created import Created
    from journal.events.rows.task_opened import TaskOpened
    from journal.sync.team_change import TeamChange

    class Heard(Listener):
        def __init__(self) -> None:
            self.events = []

        def handle(self, event) -> None:
            self.events.append(event)

    bus_a, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    bus_b, scope_b, tasks_b, outgoing_b, incoming_b = team_journal(tmp_path, "b")
    created, opened = Heard(), Heard()
    bus_b.listen(Created, created)
    bus_b.listen(TaskOpened, opened)
    with scope_a.environment(1):
        kept = tasks_a.save(Task(environment_id=1, title="kept"), actor=USER)
        gone = tasks_a.save(Task(environment_id=1, title="gone"), actor=USER)
    incoming_b.apply(team_changes(outgoing_a))
    with scope_b.environment(1):
        assert [(task.id, task.title) for task in tasks_b.rows()] == [(kept.id, "kept"), (gone.id, "gone")]
        assert len(opened.events) == 2 and created.events == [], "a pulled creation opens the task and runs no listener of a local creation"
        tasks_b.save(tasks_b.find(kept.id).with_(title="b's title"), actor=AGENT)
    with scope_a.environment(1):
        tasks_a.save(kept.with_(title="a's title", brief="a's brief"), actor=USER)
        tasks_a.delete(gone, USER)
    with scope_b.environment(1):
        tasks_b.save(tasks_b.find(gone.id).with_(brief="b's brief"), actor=AGENT)
    applied_from = datetime.now(timezone.utc)
    incoming_b.apply(team_changes(outgoing_a))
    with scope_b.environment(1):
        [task] = tasks_b.rows()
        assert (task.title, task.brief) == ("b's title", "a's brief"), "a field this machine still has to send is kept as this machine has it"
        assert task.updated_at >= applied_from, "a pulled row is dated when it was applied here, so the viewer's next poll finds it however old the edit"
        assert [change.row for change in outgoing_b.waiting()] == [kept.id], "a pulled deletion drops this machine's waiting change to the row"
    incoming_b.apply([TeamChange(row_table="tasks", row=kept.id, action="updated", writer=USER.stamp, fields={"column_from_a_newer_journal": 1})])


def test_a_withdrawn_change_the_journal_keeps_is_never_read_as_a_deletion_or_an_update_and_a_queued_withdrawal_replaces_the_rows_earlier_change(tmp_path):
    from journal.models.outgoing_change import OutgoingChange
    from journal.sync.team_change import TeamChange
    from sync_server.logged_change import LoggedChange

    _, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, scope_b, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    with scope_a.environment(1):
        kept = tasks_a.save(Task(environment_id=1, title="kept"), actor=USER)
    incoming_b.apply(team_changes(outgoing_a))
    incoming_b.apply([TeamChange(row_table="tasks", row=kept.id, action="withdrawn", writer=USER.stamp, kept_by=keeper) for keeper in (Actor.user(1).stamp, "all")])
    with scope_b.environment(1):
        assert [(task.id, task.title) for task in tasks_b.rows()] == [(kept.id, "kept")], "a withdrawal this journal's person keeps, or every journal does, deletes no row and changes none"
    assert TeamChange.logged(LoggedChange("tasks", kept.id, "withdrawn", USER.stamp, 1, 1, kept_by="all")).kept_by == "all", "the keeper crosses from the server's log to the journal"
    update, withdrawal = OutgoingChange(id=5, row_table="tasks", row=kept.id, action="updated", fields={"title": "x"}), OutgoingChange(row_table="tasks", row=kept.id, action="withdrawn", kept_by="owner")
    assert update.merged(withdrawal).payload() == {"row_table": "tasks", "row": kept.id, "action": "withdrawn", "actor": "", "fields": {}, "changed_at": {}, "local_number": 5, "kept_by": "owner"}, "a withdrawal queued after an update is sent alone in the queued change's place, with its keeper"
    assert update.with_(action="created").merged(withdrawal) is None, "a row withdrawn before it was ever sent is sent not at all"


def served_team_journals(tmp_path):
    """Ada's and Bob's team journals joined to one team server in this process, and the step that carries Ada's waiting writes through the server into Bob's journal."""
    import json
    from journal.sync.team_account import TEAM_FILE
    from journal.sync.team_change import TeamChange
    from sync_server.account import ADMIN, MEMBER
    from sync_server.push_request import PushRequest
    from sync_server.team_server import TeamServer

    (tmp_path / "server").mkdir()
    team = TeamServer(tmp_path / "server")
    team.accounts.create("ada@example.com", "Ada", "correct horse battery", ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", "correct horse battery", MEMBER, 1.0)
    _, ada = team.devices.login("ada@example.com", "correct horse battery", "laptop", "10.0.0.1", 2.0)
    bob, _ = team.devices.login("bob@example.com", "correct horse battery", "desktop", "10.0.0.2", 2.0)
    journal_a, journal_b = team_journal(tmp_path, "a"), team_journal(tmp_path, "b")
    (tmp_path / "a" / ".journal" / TEAM_FILE).write_text(json.dumps({"account_id": 1, "team_key": team.details.answer().key}))
    (tmp_path / "b" / ".journal" / TEAM_FILE).write_text(json.dumps({"account_id": 2, "team_key": team.details.answer().key}))
    outgoing_a, incoming_b, pulled = journal_a[3], journal_b[4], [0]

    def carried():
        changes = outgoing_a.waiting()
        team.pushes.answer(ada, PushRequest.parsed([change.payload() for change in changes]), 3.0)
        outgoing_a.sent(changes)
        incoming_b.apply([TeamChange.logged(change) for change in team.log.pull_page(pulled[0], bob.id)])
        pulled[0] = team.log.head()

    return team, journal_a, journal_b, carried


def test_unsharing_an_environment_withdraws_its_rows_links_and_files_from_the_server_and_the_colleague_and_the_owner_keeps_them(tmp_path):
    from journal.config import Config
    from journal.features.team.support.environment_sharing import EnvironmentSharing
    from journal.models.environment import Environment
    from journal.models.message import Message
    from journal.models.plan import Plan
    from journal.models.user import User
    from journal.repositories.environment_owners import EnvironmentOwners
    from journal.repositories.shared_tables import SharedTables
    from journal.repositories.users import Users
    from journal.sync.team_account import TeamAccount
    from sync_server.file_place import FilePlace

    team, (_, scope_a, tasks_a, outgoing_a, _), (_, _, tasks_b, outgoing_b, _), carried = served_team_journals(tmp_path)
    rows_a, rows_b = SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()), SharedTables(tasks_b.connection, tasks_b.bus, TimeSource())
    links_a, links_b = Links(tasks_a.connection, tasks_a.bus, TimeSource()), Links(tasks_b.connection, tasks_b.bus, TimeSource())

    hub = scope_a.environments.save(Environment(name="hub", environment_type=EnvironmentType.SESSION), USER)
    shared = scope_a.environments.save(Environment(name="mine"), USER)
    links_a.save(Link(source=Ref.build(User(id=1)), target=Ref.build(shared), link_type="owner"), USER)
    with scope_a.environment(hub.id):
        hub_task = tasks_a.save(Task(environment_id=hub.id, title="the hub's task"), actor=USER)
    sharing = EnvironmentSharing(scope_a.environments, EnvironmentOwners(links_a, Users(tasks_a.connection, tasks_a.bus, TimeSource()), scope_a.environments), TeamAccount(Config(tmp_path / "a")))
    shared = sharing.shared(shared, USER)
    with scope_a.environment(shared.id):
        task = tasks_a.save(Task(environment_id=shared.id, title="mine"), actor=USER)
        plan = rows_a.rows("plans").save(Plan(environment_id=shared.id, title="my plan"), USER)
        messages = [rows_a.rows("messages").save(Message(environment_id=shared.id, text=text, files=files), USER) for text, files in (("hello", ("note.txt",)), ("again", ()))]
        to_hub = links_a.save(Link(source=Ref.build(task), target=Ref.build(hub_task), link_type="follows"), USER)
    team.files.put(FilePlace("messages", messages[0].id, "note.txt"), b"a note")
    for side in ("a", "b"):
        (tmp_path / side / ".journal" / "files" / "message" / str(messages[0].id)).mkdir(parents=True)
        (tmp_path / side / ".journal" / "files" / "message" / str(messages[0].id) / "note.txt").write_bytes(b"a note")
    carried()
    withdrawn = [("environments", shared.id), ("tasks", task.id), ("plans", plan.id), *(("messages", message.id) for message in messages), ("links", to_hub.id)]
    on_server = lambda: {(row.row_table, row.row) for row in team.log.copied_rows()}
    on_b = lambda: {(table, id) for table, id in withdrawn if rows_b.rows(table).matching(id=id)}
    assert set(withdrawn) <= on_server() and on_b() == set(withdrawn), "a shared environment's rows reach the server and the colleague"

    sharing.unshared(shared, USER)
    carried()
    assert not set(withdrawn) & on_server() and ("tasks", hub_task.id) in on_server(), "the server's copy holds none of the environment's rows, and the hub's task stays"
    assert all(team.log.row(table, id) is None and not team.store.all("SELECT * FROM changes WHERE row_table = ? AND row = ? AND action != 'withdrawn'", (table, id)) for table, id in withdrawn), "nor any change from before the withdrawal"
    assert not (tmp_path / "server" / "files" / "messages" / str(messages[0].id)).exists(), "the message's file is gone from the server's folder"
    assert on_b() == set() and rows_b.rows("tasks").matching(id=hub_task.id), "the colleague's journal holds none of them and keeps the hub's task"
    assert not (tmp_path / "b" / ".journal" / "files" / "message" / str(messages[0].id)).exists(), "and the file is gone from the colleague's folder"
    assert outgoing_b.waiting() == [], "the colleague sends nothing back for what it let go"
    assert {(table, id) for table, id in withdrawn if rows_a.rows(table).matching(id=id)} == set(withdrawn) and links_a.connecting(task, hub_task), "the owner keeps every row and its link to the hub's task"
    assert (tmp_path / "a" / ".journal" / "files" / "message" / str(messages[0].id) / "note.txt").read_bytes() == b"a note", "and its file"
    team.store.close()


def test_a_journal_backs_up_before_it_deletes_withdrawn_rows_and_one_restored_from_that_backup_converges_after_one_pull(tmp_path):
    import json
    import shutil
    import sqlite3
    from journal.models.environment import Environment
    from journal.models.message import Message
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.team_account import TEAM_FILE
    from journal.sync.team_change import TeamChange

    team, (_, scope_a, tasks_a, _, _), (_, _, tasks_b, _, _), carried = served_team_journals(tmp_path)
    shared = scope_a.environments.save(Environment(name="mine", team_key="k1"), USER)
    with scope_a.environment(shared.id):
        task = tasks_a.save(Task(environment_id=shared.id, title="mine"), actor=USER)
        message = SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()).rows("messages").save(Message(environment_id=shared.id, text="hello"), USER)
    carried()
    before = team.log.head()
    withdrawn = [("environments", shared.id), ("tasks", task.id), ("messages", message.id)]
    scope_a.environments.save(scope_a.environments.find(shared.id).unshared(), USER)
    carried()
    [backup] = (tmp_path / "b" / ".journal").glob("journal-before-withdrawal-*.db")
    held = sqlite3.connect(backup)
    assert all(held.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id,)).fetchone() for table, id in withdrawn), "the backup is written before the withdrawn rows are deleted, so it holds every one of them"
    held.close()
    rows_b = SharedTables(tasks_b.connection, tasks_b.bus, TimeSource())
    assert not any(rows_b.rows(table).matching(id=id) for table, id in withdrawn), "and then they are deleted"

    (tmp_path / "c").mkdir()
    shutil.copy(backup, tmp_path / "c" / "journal.db")
    _, _, tasks_c, _, incoming_c = team_journal(tmp_path, "c")
    (tmp_path / "c" / ".journal" / TEAM_FILE).write_text(json.dumps({"account_id": 2}))
    rows_c = SharedTables(tasks_c.connection, tasks_c.bus, TimeSource())
    assert all(rows_c.rows(table).matching(id=id) for table, id in withdrawn), "the restored journal holds the withdrawn rows again"
    pulled = [TeamChange.logged(change) for change in team.log.pull_page(before, 0)]
    incoming_c.apply(pulled)
    assert not any(rows_c.rows(table).matching(id=id) for table, id in withdrawn), "one pull from where its backup stood leaves it with no withdrawn row"
    incoming_c.apply(pulled)
    assert not any(rows_c.rows(table).matching(id=id) for table, id in withdrawn), "and the same pull again changes nothing"
    team.store.close()


def test_the_migration_withdraws_the_rows_every_journal_keeps_from_the_server_and_every_journal_keeps_its_copy(tmp_path):
    from journal.models.check import Check
    from journal.models.environment import Environment
    from journal.models.rule import Rule
    from journal.models.sequence import Sequence
    from journal.models.template import Template
    from journal.models.trigger import Trigger
    from journal.models.user import User
    from journal.repositories.shared_tables import SharedTables

    team, (_, scope_a, tasks_a, outgoing_a, _), (_, _, tasks_b, outgoing_b, _), carried = served_team_journals(tmp_path)
    rows_a, rows_b = SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()), SharedTables(tasks_b.connection, tasks_b.bus, TimeSource())
    kept = [rows_a.rows(row.table()).save(row, USER) for row in (Rule(text="a rule"), Template(title="a template"), Trigger(phrases=("a phrase",)), Check(title="a check", command="true"), Sequence(title="a sequence"))]
    private = scope_a.environments.save(Environment(name="private"), USER)
    shared = scope_a.environments.save(Environment(name="open", team_key="k1"), USER)
    chat = scope_a.environments.save(Environment.session(team.details.answer().key, "team"), USER)
    owner = Links(tasks_a.connection, tasks_a.bus, TimeSource()).save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), link_type="owner"), USER)
    with scope_a.environment(shared.id):
        task = tasks_a.save(Task(environment_id=shared.id, title="open work"), actor=USER)
    carried()
    withdrawn = [*((row.table(), row.id) for row in kept), ("environments", private.id), ("links", owner.id)]
    on_server = lambda: {(row.row_table, row.row) for row in team.log.copied_rows()}
    assert set(withdrawn) <= on_server(), "before the migration the team server holds them all"

    migration_withdrawn(tmp_path, "a", scope_a, tasks_a, outgoing_a, Actor.system())
    carried()
    assert not set(withdrawn) & on_server() and {("environments", shared.id), ("environments", chat.id), ("tasks", task.id)} <= on_server(), "the server forgets the rules, templates, triggers, checks, sequences and the unshared environment, and keeps the shared ones and their rows"
    assert not team.store.all("SELECT * FROM rows WHERE fields LIKE '%private%'") and not team.store.all("SELECT * FROM changes WHERE fields LIKE '%private%'"), "no unshared environment's name is left on the server"
    assert not any((tmp_path / "server" / "files" / table / str(id)).exists() for table, id in withdrawn), "nor any file of a withdrawn row"
    for rows in (rows_a, rows_b):
        assert all(rows.rows(table).matching(id=id) for table, id in withdrawn), "every journal keeps its copy of each"
    assert outgoing_a.waiting() == [] and outgoing_b.waiting() == [], "nothing goes back to the team for what every journal keeps"
    team.store.close()


def test_a_wiped_environment_and_a_deleted_rows_links_reach_the_other_journal(tmp_path):
    from journal.models.environment import Environment
    from journal.repositories.environments import Environments

    _, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, scope_b, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    environments_a, links_a, links_b = scope_a.environments, Links(tasks_a.connection, tasks_a.bus, TimeSource()), Links(tasks_b.connection, tasks_b.bus, TimeSource())
    environments_a.save(Environment(name="main"), USER)
    second = environments_a.save(Environment(name="second"), USER)
    with scope_a.environment(1):
        first = tasks_a.save(Task(environment_id=1, title="first"), actor=USER)
        other = tasks_a.save(Task(environment_id=1, title="other"), actor=USER)
        links_a.save(Link(source=Ref.build(first), target=Ref.build(other), link_type="follows"), actor=USER)
    with scope_a.environment(second.id):
        tasks_a.save(Task(environment_id=second.id, title="in the second"), actor=USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert len(tasks_b.global_matching(environment_id=1)) == 2 and len(tasks_b.global_matching(environment_id=second.id)) == 1 and len(links_b.rows()) == 1
    with scope_a.environment(1):
        tasks_a.delete(first, USER)
    environments_a.wipe(second, USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert [task.title for task in tasks_b.global_matching(environment_id=1)] == ["other"] and tasks_b.global_matching(environment_id=second.id) == [] and links_b.rows() == [], "the deleted task's links and the wiped environment's rows are gone on the other journal too"
    assert [environment.name for environment in Environments(tasks_b.connection, tasks_b.bus, TimeSource()).rows()] == [environment.name for environment in environments_a.rows()]


def test_a_shipped_template_is_written_once_for_the_team_by_the_machine_that_holds_the_upgrade(tmp_path):
    import json
    from journal.config import Config
    from journal.features.templates.seeds.builtin_templates import BuiltinTemplates
    from journal.features.templates.shipped import SHIPPED
    from journal.repositories.templates import Templates
    from journal.sync.team_account import TEAM_FILE, TeamAccount

    _, _, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, _, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    (tmp_path / "a" / ".journal" / TEAM_FILE).write_text(json.dumps({"device": "a", "upgrade": True}))
    templates_a, templates_b = Templates(tasks_a.connection, tasks_a.bus, TimeSource()), Templates(tasks_b.connection, tasks_b.bus, TimeSource())
    BuiltinTemplates(templates_a, TeamAccount(Config(tmp_path / "a"))).run()
    BuiltinTemplates(templates_b, TeamAccount(Config(tmp_path / "b"))).run()
    assert templates_b.rows() == [], "a machine without the upgrade writes no shipped row of its own"
    incoming_b.apply(team_changes(outgoing_a))
    BuiltinTemplates(templates_b, TeamAccount(Config(tmp_path / "b"))).run()
    assert sorted(template.title for template in templates_b.rows()) == sorted(template.title for template in SHIPPED), "each shipped template once, as the machine with the upgrade wrote it"


def test_only_the_teams_settings_reach_the_other_journal_never_a_machines_or_a_persons(tmp_path):
    from journal.repositories.setting_rows import SettingRows

    _, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, scope_b, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    settings_a, settings_b = SettingRows(tasks_a.connection, tasks_a.bus, scope_a, TimeSource()), SettingRows(tasks_b.connection, tasks_b.bus, scope_b, TimeSource())
    settings_a.set(WorkersOptions.WORKER_LIMIT.key, 3, USER)
    settings_a.set(WorkersOptions.PREPARATION_COMMANDS.key, ["make env"], USER)
    settings_a.set(VoicesOptions.NAME.key, "Ada", USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert settings_b.project_values() == {WorkersOptions.WORKER_LIMIT.key: 3}, "the team's setting arrives; the machine's commands and the person's name stay where they were set"
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.journal_copy import JournalCopy
    from sync_server.copied_row import CopiedRow
    copied = JournalCopy(SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()), team_scopes(tasks_a.connection, tasks_a.bus, scope_a), team_placement(tasks_a.connection, tasks_a.bus, scope_a, Config(tmp_path / "a"))).rows()
    assert sorted(row.fields["key"] for row in copied if row.row_table == "settings") == [WorkersOptions.WORKER_LIMIT.key], "the first upload carries the team's settings alone"
    settings_b.set(WorkersOptions.PREPARATION_COMMANDS.key, ["make mine"], USER)
    copy_b = JournalCopy(SharedTables(tasks_b.connection, tasks_b.bus, TimeSource()), team_scopes(tasks_b.connection, tasks_b.bus, scope_b), team_placement(tasks_b.connection, tasks_b.bus, scope_b, Config(tmp_path / "b")))
    stray = [CopiedRow("settings", 900, {"environment_id": 0, "key": WorkersOptions.PREPARATION_COMMANDS.key, "value": "[\"make theirs\"]"}, {})]
    former = [CopiedRow("tasks", 901, {"environment_id": 1, "title": "kept from before the rename", "state": "parked"}, {})]
    copy_b.replace_whole(tuple(copied) + tuple(stray) + tuple(former))
    assert settings_b.project(WorkersOptions.PREPARATION_COMMANDS.key) == ["make mine"] and settings_b.project(WorkersOptions.WORKER_LIMIT.key) == 3, "a download keeps this machine's own settings and takes the team's"
    assert tasks_b.find(901).state == TaskState.PAUSED, "a team row in a state's former name is read in its new one"


def test_a_full_copy_of_thousands_of_rows_and_the_writes_waiting_on_it_is_laid_in_with_a_bounded_number_of_statements_and_no_events(tmp_path):
    from journal.models.outgoing_change import CREATED, DELETED, UPDATED, OutgoingChange
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.journal_copy import JournalCopy
    from journal.sync.team_account import TeamAccount
    from sync_server.copied_row import CopiedRow
    from sync_server.full_copy import FullCopy

    class Heard(Listener[ModelEvent]):
        def __init__(self):
            self.events = []

        def handle(self, event):
            self.events.append(event)

    bus, scope, tasks, _, _ = team_journal(tmp_path, "b")
    config = Config(tmp_path / "b")
    tables = SharedTables(tasks.connection, tasks.bus, TimeSource())
    copy = JournalCopy(tables, team_scopes(tasks.connection, bus, scope), team_placement(tasks.connection, bus, scope, config))
    rows = tuple(CopiedRow("tasks", number, {"environment_id": 1, "title": f"task {number}"}, {}) for number in range(1, 3001))
    waiting = [
        OutgoingChange(row_table="tasks", row=5, action=UPDATED, fields={"title": "renamed here"}),
        OutgoingChange(row_table="tasks", row=7, action=DELETED, fields={}),
        OutgoingChange(row_table="tasks", row=4000, action=CREATED, fields={"environment_id": 1, "title": "made here"}),
    ]
    heard = Heard()
    bus.listen(ModelEvent, heard)
    tasks.connection.queries.clear()
    copy.replace(FullCopy(rows, 3000, 0.0), waiting, TeamAccount(config))
    statements = sum(query.runs for query in tasks.connection.queries.statements.values())
    assert statements <= 6 * len(tables.names()), f"a copy of 3000 rows takes a few statements per table, not one per row: {statements}"
    assert heard.events == [], "no row of the copy or of the writes waiting on it goes through the events of a pulled row"
    laid = {task.id: task.title for task in tables.rows("tasks").numbered(range(1, 4001))}
    assert len(laid) == 3000 and laid[5] == "renamed here" and 7 not in laid and laid[4000] == "made here", "the copy is laid in with this machine's waiting update, deletion and creation on top"


def test_the_migration_preview_writes_nothing_and_names_what_the_run_withdraws_and_the_servers_backup_brings_the_earlier_rows_back(tmp_path):
    from journal.models.environment import Environment
    from journal.models.rule import Rule
    from journal.models.user import User
    from journal.repositories.shared_tables import SharedTables
    from journal.support.rejection import Rejection

    team, (_, scope_a, tasks_a, outgoing_a, _), _, carried = served_team_journals(tmp_path)
    server = team.started("127.0.0.1", 0)
    served_link(team, server, tmp_path, "a", "ada@example.com", 1)
    links_a = Links(tasks_a.connection, tasks_a.bus, TimeSource())
    try:
        rule = SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()).rows("rules").save(Rule(text="a rule"), USER)
        private = scope_a.environments.save(Environment(name="mine"), USER)
        links_a.save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), link_type="owner"), USER)
        shared = scope_a.environments.save(Environment(name="open", team_key="k1"), USER)
        with scope_a.environment(private.id):
            task = tasks_a.save(Task(environment_id=private.id, title="mine"), actor=USER)
        with scope_a.environment(shared.id):
            open_task = tasks_a.save(Task(environment_id=shared.id, title="open work"), actor=USER)
        carried()
        earlier = {(row.row_table, row.row) for row in team.log.copied_rows()}
        migration = team_migration(tmp_path, "a", scope_a, tasks_a, outgoing_a)

        plan = migration.plan(USER)
        assert outgoing_a.waiting() == [] and scope_a.environments.hubs() == [] and not (tmp_path / "server" / "backups").exists(), "the preview writes nothing, here or on the team server"
        planned = {(change.row_table, change.row, change.kept_by) for change in plan.withdrawals}
        assert {("rules", rule.id, "all"), ("environments", private.id, "all"), ("tasks", task.id, USER.stamp)} <= planned and not {("tasks", open_task.id), ("environments", shared.id)} & {(table, row) for table, row, _ in planned}, "it withdraws the rule and the unshared environment for every journal to keep, the environment's task for its owner, and keeps the shared one"
        assert plan.lines()[0] == "makes the hub environment a" and plan.lines()[-1].startswith("keeps on the team") and "open" in plan.lines()[-1], "the preview names the hub it makes and the environments it keeps"

        backup = migration.run(USER)
        assert {(change.row_table, change.row, change.kept_by) for change in outgoing_a.waiting() if change.action == "withdrawn"} == planned, "the run withdraws exactly what the preview named"
        assert (tmp_path / "server" / "backups" / backup.name).is_file() and [hub.name for hub in scope_a.environments.hubs()] == ["a"], "the team server wrote its backup, and the hub is made"
        with pytest.raises(Rejection, match="runs once"):
            migration.run(USER)
        carried()
        assert not {(table, row) for table, row, _ in planned} & {(row.row_table, row.row) for row in team.log.copied_rows()}, "the server forgets what was withdrawn"
        team.store.restore(tmp_path / "server" / "backups" / backup.name)
        assert earlier <= {(row.row_table, row.row) for row in team.log.copied_rows()}, "restoring the backup brings back the server's earlier rows"
    finally:
        server.shutdown()
        server.server_close()
        team.store.close()


def test_a_team_that_synced_everything_moves_to_the_hub_leaving_each_journal_its_own_and_the_server_only_team_rows(tmp_path):
    from journal.models.doc import Doc
    from journal.models.doc_edit_mode import DocEditMode
    from journal.models.doc_revision import DocRevision
    from journal.models.environment import Environment
    from journal.models.message import Message
    from journal.models.plan import Plan
    from journal.models.user import User
    from journal.repositories.shared_tables import SharedTables

    team, (_, scope_a, tasks_a, outgoing_a, _), (_, _, tasks_b, _, _), carried = served_team_journals(tmp_path)
    server = team.started("127.0.0.1", 0)
    served_link(team, server, tmp_path, "a", "ada@example.com", 1)
    rows_a, rows_b, links_a = SharedTables(tasks_a.connection, tasks_a.bus, TimeSource()), SharedTables(tasks_b.connection, tasks_b.bus, TimeSource()), Links(tasks_a.connection, tasks_a.bus, TimeSource())
    migration = team_migration(tmp_path, "a", scope_a, tasks_a, outgoing_a)
    try:
        ada_own, bob_own = (scope_a.environments.save(Environment(name=name), USER) for name in ("ada-own", "bob-own"))
        shared = scope_a.environments.save(Environment(name="open", team_key=team.details.answer().key), USER)
        for person, environment in ((1, ada_own), (2, bob_own)):
            links_a.save(Link(source=Ref.build(User(id=person)), target=Ref.build(environment), link_type="owner"), USER)
        with scope_a.environment(ada_own.id):
            ada_plan = rows_a.rows("plans").save(Plan(environment_id=ada_own.id, title="Ada's plan"), USER)
            ada_task = tasks_a.save(Task(environment_id=ada_own.id, title="Ada's task"), actor=USER)
        with scope_a.environment(bob_own.id):
            bob_task = tasks_a.save(Task(environment_id=bob_own.id, title="Bob's task"), actor=USER)
        with scope_a.environment(shared.id):
            message = rows_a.rows("messages").save(Message(environment_id=shared.id, text="in the open"), USER)
        doc = migration.docs.save(Doc(title="how we work", abstract="How we work", body="the guide"), USER)
        revision = migration.revisions.added(DocRevision(number=1, title="how we work", body="the guide"), doc, USER)
        carried()
        held = lambda rows, places: {place for place in places if rows.rows(place[0]).matching(id=place[1])}
        ada_rows, bob_rows = {("plans", ada_plan.id), ("tasks", ada_task.id)}, {("tasks", bob_task.id)}
        assert held(rows_b, ada_rows | bob_rows) == ada_rows | bob_rows, "before the migration the team syncs everything"

        migration.run(USER)
        carried()
        [hub] = scope_a.environments.hubs()
        environments = {("environments", ada_own.id), ("environments", bob_own.id), ("environments", shared.id)}
        assert held(rows_a, ada_rows | environments | {("messages", message.id)}) == ada_rows | environments | {("messages", message.id)} and held(rows_a, bob_rows) == set(), "Ada's journal keeps her environments, plan and task and the shared chat, and lets Bob's task go"
        assert held(rows_b, bob_rows | environments | {("messages", message.id)}) == bob_rows | environments | {("messages", message.id)} and held(rows_b, ada_rows) == set(), "Bob's journal keeps his own task and the shared chat, and lets Ada's plan and task go"
        for rows in (rows_a, rows_b):
            moved = rows.rows("docs").find(doc.id)
            assert (moved.environment_id, moved.edit_mode, rows.rows("doc_revisions").find(revision.id).environment_id) == (hub.id, DocEditMode.FREE, hub.id), "the document and its revision are in the hub, free to edit, on both journals"
        on_server = [(row.row_table, row.row) for row in team.log.copied_rows()]
        assert on_server and all(migration.placement.is_team_row(rows_a.rows(table).find(row)) for table, row in on_server), "the server holds only team rows"
        assert not (ada_rows | bob_rows) & set(on_server) and {("docs", doc.id), ("messages", message.id), ("environments", hub.id)} <= set(on_server)
        assert list((tmp_path / "a" / ".journal").glob("journal-before-hub-*.db")) and list((tmp_path / "server" / "backups").glob("team-before-hub-*.db")), "the journal and the team server were backed up first"
    finally:
        server.shutdown()
        server.server_close()
        team.store.close()


def test_a_team_setting_reaches_the_other_journal_and_a_personal_one_does_not_before_and_after_the_migration(tmp_path):
    from journal.repositories.setting_rows import SettingRows
    from journal.events.models.synced import Synced
    from journal.sync.pulled_settings import PulledSettings

    team, (_, scope_a, tasks_a, outgoing_a, _), (bus_b, scope_b, tasks_b, _, _), carried = served_team_journals(tmp_path)
    settings_a, settings_b = SettingRows(tasks_a.connection, tasks_a.bus, scope_a, TimeSource()), SettingRows(tasks_b.connection, tasks_b.bus, scope_b, TimeSource())
    bus_b.listen(Synced, PulledSettings(settings_b))
    on_server = lambda: {row.fields["key"]: row.fields["value"] for row in team.log.copied_rows() if row.row_table == "settings"}
    settings_a.set(WorkersOptions.WORKER_LIMIT.key, 3, USER)
    settings_a.set(VoicesOptions.NAME.key, "Ada", USER)
    carried()
    assert settings_b.project_values() == {WorkersOptions.WORKER_LIMIT.key: 3} and set(on_server()) == {WorkersOptions.WORKER_LIMIT.key}, "before the migration the team's setting reaches the other journal and the person's name does not"

    migration_withdrawn(tmp_path, "a", scope_a, tasks_a, outgoing_a, Actor.system())
    carried()
    assert settings_b.project_values() == {WorkersOptions.WORKER_LIMIT.key: 3} and set(on_server()) == {WorkersOptions.WORKER_LIMIT.key}, "the migration moves no setting row: the team's setting stays on the server and the other journal"
    settings_a.set(WorkersOptions.WORKER_LIMIT.key, 5, USER)
    settings_a.set(VoicesOptions.NAME.key, "Ada Lovelace", USER)
    carried()
    assert settings_b.project_values() == {WorkersOptions.WORKER_LIMIT.key: 5} and set(on_server()) == {WorkersOptions.WORKER_LIMIT.key}, "after it a change to the team's setting still reaches the other journal and the person's name still does not"
    assert settings_a.project(VoicesOptions.NAME.key) == "Ada Lovelace", "the person's own setting stays on their journal"
    team.store.close()


def test_team_placement_puts_each_row_in_its_team_or_in_none(tmp_path):
    import json
    from journal.config import Config
    from journal.models.entry import Entry
    from journal.models.environment import Environment
    from journal.models.rule import Rule
    from journal.models.setting import Setting
    from journal.models.task import Task
    from journal.models.template import Template
    from journal.models.user import User
    from journal.repositories.environments import Environments
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.team_account import TEAM_FILE, TEAMS_FOLDER, TeamAccount
    from journal.sync.team_placement import TeamPlacement

    bus, scope, tasks, _, _ = team_journal(tmp_path, "a")
    config = Config(tmp_path / "a")
    (config.home / TEAM_FILE).unlink()
    (config.home / TEAMS_FOLDER).mkdir()
    (config.home / TEAMS_FOLDER / "k1.json").write_text(json.dumps({"team_key": "k1"}))
    environments = Environments(tasks.connection, bus, TimeSource())
    hub, session, shared, private = (environments.save(row, USER) for row in (Environment.hub("k1", "acme"), Environment.session("k1", "team"), Environment(name="open", team_key="k1"), Environment(name="mine")))
    placement = TeamPlacement(SharedTables(tasks.connection, bus, TimeSource()), team_scopes(tasks.connection, bus, scope), TeamAccount(config))
    placed = lambda *rows: [placement.team_key(row) for row in rows]

    work = {}
    for environment in (hub, session, shared, private):
        with scope.environment(environment.row_id):
            work[environment.name] = tasks.save(Task(environment_id=environment.row_id, title=f"in {environment.name}"), USER)
    assert placed(hub, session, shared, private) == ["k1", "k1", "k1", ""], "an environment is in its team when it is the hub, a session or shared, and a private one in none"
    assert placed(*(work[name] for name in ("acme", "team", "open", "mine"))) == ["k1", "k1", "k1", ""], "a row of an environment is placed with its environment, whose chat is shared or not"
    links = Links(tasks.connection, bus, TimeSource())
    together = links.save(Link(source=Ref.build(work["acme"]), target=Ref.build(work["team"]), link_type="mentions"), USER)
    apart = links.save(Link(source=Ref.build(work["mine"]), target=Ref.build(work["acme"]), link_type="copied_from"), USER)
    owner = links.save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), link_type="owner"), USER)
    assert placed(together, apart, owner) == ["k1", "", ""], "a link is in a team only when both its ends are in that team"
    assert placed(User(id=2, name="Bob")) == ["k1"], "a person is in their team"
    assert placed(Rule(text="a rule"), Template(title="a template"), Entry()) == ["", "", ""], "rules and templates are in no team, nor is a row kept on one machine"
    team_setting, own_setting = WorkersOptions.WORKER_LIMIT.key, VoicesOptions.NAME.key
    settings = [Setting(environment_id=0, key=team_setting), Setting(environment_id=0, key=own_setting), Setting(environment_id=shared.row_id, key=team_setting), Setting(environment_id=private.row_id, key=team_setting)]
    assert placed(*settings) == ["k1", "", "k1", ""], "a project setting of the team's scope is in the home team, a person's in none, and one of an environment goes with it"


def test_an_environment_deleted_on_one_journal_is_gone_from_the_other_with_everything_in_it(tmp_path):
    from journal.models.environment import Environment
    from journal.models.task import Task
    from journal.repositories.environments import Environments

    _, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, scope_b, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    environments_a, environments_b = Environments(tasks_a.connection, tasks_a.bus, TimeSource()), Environments(tasks_b.connection, tasks_b.bus, TimeSource())
    side = environments_a.save(Environment(name="side"), USER)
    with scope_a.environment(side.row_id):
        task = tasks_a.save(Task(environment_id=side.row_id, title="in the side line"), USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert environments_b.find(side.row_id) and tasks_b.find(task.row_id).title == "in the side line"
    environments_a.wipe(environments_a.find(side.row_id), USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert side.row_id not in [row.row_id for row in environments_b.rows()] and task.row_id not in [row.row_id for row in tasks_b.global_matching()], "deleting an environment deletes it, and everything in it, from the other journal too"


def test_a_checks_runs_stay_on_the_machine_that_ran_them_while_its_definition_is_the_teams(tmp_path):
    from datetime import datetime, timezone
    from journal.models.check import Check
    from journal.repositories.checks import Checks

    _, scope_a, tasks_a, outgoing_a, _ = team_journal(tmp_path, "a")
    _, scope_b, tasks_b, _, incoming_b = team_journal(tmp_path, "b")
    checks_a, checks_b = Checks(tasks_a.connection, tasks_a.bus, TimeSource()), Checks(tasks_b.connection, tasks_b.bus, TimeSource())
    check = checks_a.save(Check(title="lint", command="true", interval=5), USER)
    sent = len(outgoing_a.waiting())
    checks_a.save(check.completed(True, "all clean", datetime.now(timezone.utc), 0.1, None, "", 0.0), USER)
    assert len(outgoing_a.waiting()) == sent, "a run's results leave no change for the team, not even its stamps"
    incoming_b.apply(team_changes(outgoing_a))
    arrived = checks_b.find(check.row_id)
    assert arrived.title == "lint" and arrived.last_output == "" and arrived.last_run_at is None, "the check reaches the other journal without the first machine's run"


def test_a_database_from_before_the_type_columns_keeps_every_type_under_its_new_name(connection, bus):
    """Migration 75: each column named kind becomes its table's type name, entry_type, link_type and the rest, keeping its values and its indexes, the empty column the schema already added and the index made on it dropped first; a sequence's triggers and an edit's rows keep their types as trigger_type and line_type, and a write still waiting for the team is sent under the new name."""
    from journal.db.migrations.type_columns import TypeColumns
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.models.outgoing_change import CREATED, OutgoingChange
    from journal.repositories.outgoing_changes import OutgoingChanges

    kind_columns(connection)
    connection.execute("CREATE INDEX IF NOT EXISTS links_by_kind ON links (kind, source)")
    Schema(connection, AllModels.MODELS).create()
    connection.execute("CREATE INDEX entries_dispatches ON entries (environment_id, id) WHERE entry_type = 'Stop'")
    for table, value in (("entries", "nudge"), ("links", "mentions"), ("sent_agents", "worker"), ("secrets", "browser login"), ("environments", "hub")):
        connection.execute(f"INSERT INTO {table} (kind, created_at, creator) VALUES (?, '2026-10-27', 'system')", (value,))
    connection.execute("INSERT INTO reports (kind, abstract, created_at, creator) VALUES ('update', 'what changed', '2026-10-27', 'system')")
    connection.execute("INSERT INTO edits (kind, rows, created_at, creator) VALUES ('create', ?, '2026-10-27', 'system')", (json.dumps([{"kind": "add", "line": 1, "text": "x = 1", "hidden": 0}]),))
    connection.execute("INSERT INTO sequences (title, triggers, created_at, creator) VALUES ('Ship', ?, '2026-10-27', 'system')", (json.dumps([{"kind": "row", "moment": "plan.created"}]),))
    outgoing = OutgoingChanges(connection, bus, TimeSource())
    outgoing.queued(OutgoingChange(row_table="links", row=1, action=CREATED, fields={"kind": "mentions", "source": "tasks:1"}, changed_at={"kind": 1.0, "source": 1.0}, writer="user:1"), Actor.system())
    with connection.transaction():
        TypeColumns().apply(connection)
    for table, column, value in (("entries", "entry_type", "nudge"), ("links", "link_type", "mentions"), ("sent_agents", "helper_type", "worker"), ("secrets", "secret_type", "browser login"), ("edits", "edit_type", "create"), ("environments", "environment_type", "hub"), ("reports", "report_type", "update")):
        columns = {row["name"] for row in connection.all(f"PRAGMA table_info({table})")}
        assert "kind" not in columns and connection.one(f"SELECT {column} AS value FROM {table}")["value"] == value, f"{table} keeps its type under {column}"
    assert "link_type" in connection.one("SELECT sql FROM sqlite_master WHERE name = 'links_by_kind'")["sql"], "an index on the old column follows it"
    assert json.loads(connection.one("SELECT rows FROM edits")["rows"]) == [{"line_type": "add", "line": 1, "text": "x = 1", "hidden": 0}], "an edit's rows name their type line_type"
    assert json.loads(connection.one("SELECT triggers FROM sequences")["triggers"]) == [{"trigger_type": "row", "moment": "plan.created"}], "a sequence's triggers name theirs trigger_type"
    [change] = outgoing.waiting()
    assert change.fields == {"link_type": "mentions", "source": "tasks:1"} and set(change.changed_at) == {"link_type", "source"}, "a write waiting for the team is sent under the new name"


def test_a_team_row_on_the_names_before_the_type_columns_is_stored_under_the_new_ones(connection, bus):
    """A change or a copy from the team made by a journal before migration 75 names a type column kind; this journal stores it under the column's name now, and a sequence trigger stored as kind reads as its trigger_type."""
    from journal.models.support.sequence_trigger import SequenceTrigger
    from journal.models.support.sequence_trigger_type import SequenceTriggerType
    from journal.repositories.environments import Environments
    from journal.repositories.links import Links

    links = Links(connection, bus, TimeSource())
    pulled = links.pulled_creation(41, {"source": "tasks:1", "target": "tasks:2", "kind": "mentions"}, Actor.system())
    links.restored([(42, {"source": "tasks:3", "target": "tasks:4", "kind": "copied_from"})])
    assert (pulled.link_type, links.find(41).link_type, links.find(42).link_type) == ("mentions", "mentions", "copied_from"), "a pulled row and a copy laid in keep their type"
    environments = Environments(connection, bus, TimeSource())
    environments.pulled_creation(43, {"name": "acme", "team_name": "acme", "key": "k43", "kind": "hub"}, Actor.system())
    environments.pulled_update(43, {"kind": "session"}, Actor.system())
    assert environments.find(43).environment_type == "session", "an update on the old name changes the type too"
    assert SequenceTrigger.parsed({"kind": "row", "moment": "plan.created"}) == SequenceTrigger.parsed({"trigger_type": "row", "moment": "plan.created"}) == SequenceTrigger(SequenceTriggerType.ROW, moment="plan.created"), "a trigger reads under either name"


def test_a_write_queued_before_a_column_rename_is_sent_under_the_new_name(connection, bus):
    from journal.db.migration import Migration
    from journal.models.outgoing_change import UPDATED, OutgoingChange
    from journal.repositories.outgoing_changes import OutgoingChanges

    connection.execute("ALTER TABLE tasks ADD COLUMN headline TEXT")
    outgoing = OutgoingChanges(connection, bus, TimeSource())
    outgoing.queued(OutgoingChange(row_table="tasks", row=7, action=UPDATED, fields={"headline": {"words": "kept whole"}, "state": "open"}, changed_at={"headline": 1.0, "state": 1.0}, writer="user:2"), Actor.system())
    with connection.transaction():
        Migration.column_rename(connection, "tasks", "headline", "subtitle")
    [change] = outgoing.waiting()
    assert change.fields == {"subtitle": {"words": "kept whole"}, "state": "open"} and change.changed_at == {"subtitle": 1.0, "state": 1.0}, "a write queued offline before the rename goes out under the new name, its value intact"


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


def test_a_transaction_reads_its_own_writes_even_when_another_thread_stored_the_table_meanwhile(connection, bus):
    """Two links made in one transaction once took one number: a reader on another thread stored the blocks as committed, and the writer read that copy back, missing its own write."""
    import threading
    from journal.repositories.id_blocks import IdBlocks
    blocks = IdBlocks(connection, bus, TimeSource())
    blocks.add("links", 100, 199)
    taken = []
    with connection.transaction():
        taken.append(blocks.next_id("links"))
        reader = threading.Thread(target=lambda: blocks.all_matching(row_table="links"))
        reader.start()
        reader.join()
        taken.append(blocks.next_id("links"))
    assert taken == [100, 101], "the second number follows the first, whatever another thread read in between"


def test_the_developer_numbers_drop_removes_the_timings_table_and_the_numbers_but_not_other_statistics(connection):
    from journal.db.migrations.developer_numbers_drop import DeveloperNumbersDrop
    connection.execute("CREATE TABLE IF NOT EXISTS timings (id INTEGER PRIMARY KEY)")
    connection.execute("INSERT INTO statistics (key, value, created_at, creator) VALUES ('developer.hooks.count', 3, '2026-10-24', 'system'), ('profiles.x.uses', 2, '2026-10-24', 'system')")
    DeveloperNumbersDrop().apply(connection)
    assert connection.one("SELECT name FROM sqlite_master WHERE name = 'timings'") is None
    assert [row["key"] for row in connection.all("SELECT key FROM statistics")] == ["profiles.x.uses"]


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


def test_two_writers_of_one_team_account_never_race_on_one_draft(tmp_path):
    import threading
    from journal.sync.team_account import TeamAccount
    config = Config(tmp_path)
    config.home.mkdir(parents=True, exist_ok=True)
    account = TeamAccount(config)
    failures = []

    def write(n: int) -> None:
        try:
            for i in range(200):
                account.write({"team_key": "1c7515639941a0de24bcf599be24a3ab", "account_id": n, "round": i})
        except OSError as error:
            failures.append(error)

    writers = [threading.Thread(target=write, args=(n,)) for n in (1, 2, 3)]
    for writer in writers:
        writer.start()
    for writer in writers:
        writer.join(timeout=60)
    assert failures == [], f"each write has a draft of its own, so none is replaced away under another (the FileNotFoundError on the .draft seen in the team tests under load): {failures[:1]}"
    assert not list((config.home / "teams").glob("*.draft")), "and no draft is left behind"


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
