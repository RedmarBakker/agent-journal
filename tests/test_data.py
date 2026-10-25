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
from journal.models.environment_kind import EnvironmentKind
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

USER = Actor.user(1)
AGENT = Actor.agent("abc")


class Heard(Listener[ModelEvent]):
    def __init__(self):
        self.events = []

    def handle(self, event):
        self.events.append(event)


def tasks_of(connection, bus, scope) -> Tasks:
    return Tasks(connection, bus, scope, Links(connection, bus), Questions(connection, bus, scope), Checks(connection, bus))


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
    tasks, links = tasks_of(connection, bus, scope), Links(connection, bus)
    bus.listen(Deleted, UnlinkDeleted(links))
    item = tasks.save(Task(environment_id=1, title="a"), actor=USER)
    b = tasks.save(Task(environment_id=1, title="b"), actor=USER)
    links.save(Link(source=Ref.build(item), target=Ref.build(b), kind="blocks"), actor=AGENT)
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
    scope = Scope(Environments(old, bus), Links(old, bus))
    message = Messages(old, bus, scope, Reactions(old, bus, scope, Links(old, bus)), Links(old, bus), EnvironmentOwners(Links(old, bus), Users(old, bus), Environments(old, bus)), Agents(old, bus, scope)).find(1)
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
    from journal.models.fact import Fact
    from journal.models.plan import Plan
    from journal.models.report import Report
    from journal.models.support.dock_card import DockCard
    from journal.models.support.row_card import RowCard
    report = Report(id=33, title="What the dock showed", abstract="One line about it", body="## First\n\ntext")
    assert report.heading() == "Report 33: What the dock showed" and report.summary_line() == "One line about it"
    assert Doc(id=3, title="Notes", body="# Notes\n\nThe first line.\nThe second.").summary_line() == "The first line."
    task = Task(id=12, title="Write it", brief="First line of the brief\nmore")
    assert task.heading() == "Task 12: Write it" and task.summary_line() == "First line of the brief"
    assert Fact(id=2, text="Ports are fixed").heading() == "Fact 2" and Fact(id=2).summary_line() == ""
    assert task.docked() == DockCard.plain() and [b.label for b in DockCard.plain().buttons] == ["Open", "Close"]
    assert [(b.label, b.act) for b in Plan(id=1).docked().buttons] == [("Open plan", "open"), ("Approve", "approve"), ("Close", "close")]
    assert RowCard.build(report).as_data() == {"row": "reports:33", "heading": "Report 33: What the dock showed", "summary": "One line about it", "dock": {"buttons": [{"label": "Open", "act": "open"}, {"label": "Close", "act": "close"}], "folds": True}}, "a card carries no file: a document is downloaded from where it is read"


def legacy_workers(connection) -> None:
    """The workers table as journals kept it before workers and verifiers shared the table of sent agents, for the migrations that ran on it."""
    from journal.db.schema import Schema
    from journal.models.worker import Worker
    columns = ", ".join(f"{column.name} {column.sql_type}" for column in Schema.columns(Worker) if column.name not in ("id", "kind"))
    connection.execute(f"CREATE TABLE workers (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")


def test_the_time_keys_migration_renames_at_in_the_column_and_the_stored_json(connection):
    """Migration 20: the edits column at becomes time, and the at key inside an entry's data, a check's progress and a dump's question and answers becomes time; a record without them is left as it is."""
    from journal.db.migrations.time_keys import TimeKeys
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
    columns = ", ".join(f"{column.name} {column.sql_type}" for column in Schema.columns(Verifier) if column.name not in ("id", "kind"))
    connection.execute(f"CREATE TABLE verifiers (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")
    for name in ("Ada", "Grace"):
        connection.execute("INSERT INTO workers (environment_id, name, state, created_at, creator) VALUES (1, ?, 'dispatched', '2026-10-25', 'system')", (name,))
    connection.execute("INSERT INTO verifiers (environment_id, name, state, created_at, creator) VALUES (1, 'Diogenes', 'judged', '2026-10-25', 'system')")
    connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES ('verifiers:1', 'reader_reports:4', 'verifies', '2026-10-25', 'system')")
    connection.execute("INSERT INTO messages (environment_id, author, text, data, created_at, creator) VALUES (1, 'system', 'card', ?, '2026-10-25', 'system')", (json.dumps({"key": "verifier:1"}),))
    HelperRows().apply(connection)
    rows = [(row["id"], row["name"], row["kind"]) for row in connection.all("SELECT id, name, kind FROM sent_agents ORDER BY id")]
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
        connection.execute("ALTER TABLE environments ADD COLUMN is_team_chat INTEGER NOT NULL DEFAULT 0")
        connection.execute("ALTER TABLE environments ADD COLUMN is_shared_with_team INTEGER NOT NULL DEFAULT 0")
        for name, team_chat, shared in (("main", 0, 0), ("team", 1, 0), ("ada-docs", 0, 1)):
            connection.execute("INSERT INTO environments (name, key, kind, team_key, is_team_chat, is_shared_with_team, created_at, creator) VALUES (?, lower(hex(randomblob(16))), 'local', '', ?, ?, '2026-10-24', 'system')", (name, team_chat, shared))
        connection.execute("INSERT INTO docs (title, body, created_at, creator) VALUES ('Handbook', 'how we work', '2026-10-24', 'system')")
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
    for n, state in ((1, "reported"), (2, "dispatched"), (3, "dispatched")):
        connection.execute("INSERT INTO workers (environment_id, name, state, created_at, creator) VALUES (1, ?, ?, '2026-10-21', 'system')", (f"w{n}", state))
    for worker, reports in ((1, 3), (2, 2)):
        for message in range(reports):
            connection.execute("INSERT INTO links (source, target, kind, created_at, creator) VALUES (?, ?, 'reported', '2026-10-21', 'system')", (f"workers:{worker}", f"messages:{worker * 10 + message}"))
    connection.execute("UPDATE workers SET reuse_count = NULL, retire_reason = NULL")
    WorkerReuseCounts().apply(connection)
    counts = [(row["name"], row["reuse_count"]) for row in connection.all("SELECT name, reuse_count FROM workers ORDER BY id")]
    assert counts == [("w1", 2), ("w2", 2), ("w3", 0)], "three reports and back is two sends; two reports and out again is two; out on its first job is none"


def test_the_message_agents_migration_moves_the_session_into_its_column_and_puts_every_message_in_the_main_chat(connection):
    """Migration 34: a peer message's session leaves its data for the session column, an agent's own message takes its writer's session, a user's has none, and all of them are the main agent's."""
    from journal.db.migrations.message_agents import MessageAgents
    for creator, data in (("system", {"kind": "peer", "session": "s1", "peer": "other"}), ("agent:s2", {}), ("user:1", {}), ("system", {"session": ""})):
        connection.execute("INSERT INTO messages (environment_id, author, text, data, created_at, creator) VALUES (1, 'agent', 'x', ?, '2026-10-22', ?)", (json.dumps(data), creator))
    connection.execute("UPDATE messages SET session = NULL, agent_role = NULL")
    MessageAgents().apply(connection)
    rows = [(row["session"], row["agent_role"], json.loads(row["data"])) for row in connection.all("SELECT session, agent_role, data FROM messages ORDER BY id")]
    assert rows == [("s1", "main", {"kind": "peer", "peer": "other"}), ("s2", "main", {}), (None, "main", {}), (None, "main", {})]


def test_a_query_renders_every_read_shape_with_its_values_bound():
    tasks, entries = Query.build(Task), Query.build(Entry)
    assert tasks.filter(state=TaskState.OPEN, creator=None).order_descending("id").limit(5).select() == ("SELECT * FROM tasks WHERE state = ? AND creator IS NULL ORDER BY id DESC LIMIT ? OFFSET ?", ("open", 5, 0)), "a value is turned by its column, and None reads as null"
    assert tasks.filter_listed("id", (1, 2)).filter_unlisted("state", (TaskState.FINISHED,)).filter_present("block_reason").select() == ("SELECT * FROM tasks WHERE id IN (?, ?) AND state NOT IN (?) AND block_reason IS NOT NULL", (1, 2, TaskState.FINISHED.value))
    assert tasks.filter_greater("id", 1).filter_less("id", 9).filter_greater_equal("id", 2).filter_less_equal("id", 8).filter_unequal("title", "x").select()[0] == "SELECT * FROM tasks WHERE id > ? AND id < ? AND id >= ? AND id <= ? AND title IS NOT ?"
    assert tasks.filter_prefix("title", "a").filter_missing_prefix("creator", "user:").select() == ("SELECT * FROM tasks WHERE title >= ? AND title < ? AND (creator IS NULL OR creator < ? OR creator >= ?)", ("a", "a\uffff", "user:", "user:\uffff"))
    assert tasks.filter_containing("title", "50%_off").order("state").order_descending("id").offset(3).select() == ("SELECT * FROM tasks WHERE title LIKE ? ESCAPE '\\' ORDER BY state, id DESC LIMIT ? OFFSET ?", ("%50\\%\\_off%", -1, 3))
    assert entries.filter_json("data->session", "s").filter_listed("data->call->kind", ("a",)).maximum("data->time", 0) == ("SELECT COALESCE(MAX(json_extract(data, '$.time')), 0) AS value FROM entries WHERE json_extract(data, '$.session') = ? AND json_extract(data, '$.call.kind') IN (?)", ("s", "a"))
    assert tasks.filter_alternatives(tasks.filter(title="a"), tasks.filter(title="b").filter_null("block_reason")).count() == ("SELECT count(*) AS value FROM tasks WHERE (title = ? OR (title = ? AND block_reason IS NULL))", ("a", "b"))
    assert entries.filter(kind="ToolStarting").order_descending("id").limit(9).repeated("data->call->command", 2) == ("SELECT value FROM (SELECT json_extract(data, '$.call.command') AS value FROM entries WHERE kind = ? ORDER BY id DESC LIMIT ? OFFSET ?) WHERE value != '' GROUP BY value HAVING COUNT(*) >= ?", ("ToolStarting", 9, 0, 2)), "the values a page of rows holds at least so many times"
    assert tasks.filter_absent(Query.build(Link).filter(kind="in_plan").filter_ref("source", tasks)).count() == ("SELECT count(*) AS value FROM tasks WHERE NOT EXISTS (SELECT 1 FROM links WHERE kind = ? AND links.source = ? || tasks.id)", ("in_plan", "tasks:"))


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
    db.execute("INSERT INTO entries (environment_id, kind, actor, data, created_at, creator, updated_at, updater) VALUES (1, 'nudge', 'system', ?, '2026-10-01T10:00:00+00:00', 'system', '2026-10-01T10:00:00+00:00', 'system')", (json.dumps({"key": "shell.outputs_ended", "session": "s1", "line": "output 1 finished"}),))
    db.execute("DELETE FROM migrations WHERE number >= 37")
    db.commit()
    db.close()
    second = App(Config(tmp_path, port=0))
    second.runtime().start()
    second.runtime().stop()
    db = sqlite3.connect(second.config.database)
    data = json.loads(db.execute("SELECT data FROM entries WHERE kind = 'nudge' AND json_extract(data, '$.line') = 'output 1 finished'").fetchone()[0])
    assert data["tool_use"] == 0 and data["time"] > 0, data


def test_the_tasks_repository_answers_which_tasks_are_open_blocked_paused_and_unclosed(connection, bus, scope):
    from journal.models.plan import Plan
    from journal.models.plan_state import PlanState
    from journal.repositories.scoped_repository import ScopedRepository
    from journal.repositories.tasks import PLAN_LINK

    class PlanRows(ScopedRepository[Plan]):
        model = Plan

    tasks, links = tasks_of(connection, bus, scope), Links(connection, bus)
    with scope.environment(1):
        free = tasks.save(Task(environment_id=1, title="free"), actor=USER)
        drafted = tasks.save(Task(environment_id=1, title="in a draft plan"), actor=USER)
        blocked = tasks.save(Task(environment_id=1, title="blocked", state=TaskState.BLOCKED), actor=USER)
        paused = tasks.save(Task(environment_id=1, title="paused", state=TaskState.PAUSED), actor=USER)
        done = tasks.save(Task(environment_id=1, title="done", state=TaskState.FINISHED), actor=USER)
        draft = PlanRows(connection, bus, scope).save(Plan(environment_id=1, title="p", state=PlanState.DRAFT), USER)
        links.save(Link(source=Ref.build(drafted), target=Ref.build(draft), kind=PLAN_LINK), actor=USER)
        assert [task.id for task in tasks.open_tasks()] == [free.id], "a task of an unapproved plan is no open work"
        assert [task.id for task in tasks.blocked_tasks()] == [blocked.id]
        assert [task.id for task in tasks.paused_tasks()] == [paused.id]
        assert done.id not in [task.id for task in tasks.unclosed_tasks()] and free.id in [task.id for task in tasks.unclosed_tasks()]
        assert tasks.unfinished_ids([free.id, done.id]) == [free.id]


def test_each_model_says_whether_it_is_shared_with_the_team_or_kept_on_one_machine():
    from journal.models.all_models import AllModels
    local = sorted(model.__name__ for model in AllModels.MODELS if not model.shared)
    assert local == sorted(["Entry", "Agent", "Statistic", "CommandOutput", "DashboardRow", "Secret", "Phone", "PhoneCode", "MigratedRow", "Version3Migration", "JournalVersion", "ReleaseMessage", "ReaderReport", "OutgoingChange", "IdBlock", "PendingUpload", "Plugin", "McpServer", "BrowserSession", "PoolJob", "ScheduledJob", "TestTurn", "Verifier", "Reviewer"]), "the models kept on one machine are the ones NOTES.md names"
    assert all(model.shared for model in AllModels.MODELS if model.__name__ in ("Task", "Message", "Alias", "Worker", "Setting")), "everything else is shared"


def test_each_write_to_a_shared_row_is_queued_for_the_team_once_joined_and_waiting_writes_to_a_row_merge(connection, bus, scope, tmp_path):
    from journal.config import Config
    from journal.events.models.model_event import ModelEvent
    from journal.models.release_message import ReleaseMessage
    from journal.repositories.outgoing_changes import OutgoingChanges
    from journal.repositories.release_messages import ReleaseMessages
    from journal.sync.team_account import TEAM_FILE, TeamAccount

    config = Config(tmp_path)
    changes, tasks = OutgoingChanges(connection, bus), tasks_of(connection, bus, scope)
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
        ReleaseMessages(connection, bus).save(ReleaseMessage(version="9.9.9", text="local"), USER)
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

    config, blocks, tasks = Config(tmp_path), IdBlocks(connection, bus), tasks_of(connection, bus, scope)
    bus.listen(NumberRequest, BlockNumbers(blocks, TeamAccount(config), BlockSupply(TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS)), blocks, SharedTables(connection, bus), TeamAccount(config))))
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
        assert ReleaseMessages(connection, bus).save(ReleaseMessage(version="9.9.9"), USER).id == 1, "a model kept on one machine is numbered by SQLite"
        for _ in range(19):
            tasks.save(Task(environment_id=1, title="more"), actor=USER)
        with pytest.raises(NumberShortage):
            tasks.save(Task(environment_id=1, title="one too many"), actor=USER)
        assert not issubclass(NumberShortage, Rejection), "a shortage is a fault, so a hook lets its event through instead of refusing it"


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

    account, blocks, tables = TeamAccount(config), IdBlocks(connection, bus), SharedTables(connection, bus)
    renumbering = RowRenumbering(connection, blocks, BlockSupply(TeamServerLink(account, Schema(connection, AllModels.MODELS)), blocks, tables, account), config)
    return RecordOutgoingChange(changes, account, team_placement(connection, bus, scope, config), Links(connection, bus), tables, renumbering, ServiceHooks())


def team_placement(connection, bus, scope, config):
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.team_account import TeamAccount
    from journal.sync.team_placement import TeamPlacement

    return TeamPlacement(SharedTables(connection, bus), team_scopes(connection, bus, scope), TeamAccount(config))


def team_scopes(connection, bus, scope):
    from journal.features.registry import Registry
    from journal.features.standard import Standard
    from journal.repositories.setting_rows import SettingRows
    from journal.sync.setting_scopes import SettingScopes

    return SettingScopes(Registry(Standard.FEATURES, SettingRows(connection, bus, scope)))


def environment_withdrawal(config, connection, bus, scope):
    from journal.repositories.environment_owners import EnvironmentOwners
    from journal.repositories.shared_tables import SharedTables
    from journal.repositories.users import Users
    from journal.sync.environment_withdrawal import EnvironmentWithdrawal
    from journal.sync.team_account import TeamAccount

    return EnvironmentWithdrawal(TeamAccount(config), SharedTables(connection, bus), Links(connection, bus), EnvironmentOwners(Links(connection, bus), Users(connection, bus), scope.environments), team_scopes(connection, bus, scope))


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
    tables, scopes, account, visible = SharedTables(connection, bus), team_scopes(connection, bus, scope), TeamAccount(config), DocScope(scope.environments, scope)
    withdrawal = MigrationWithdrawal(outgoing, tables, environment_withdrawal(config, connection, bus, scope), scopes, ServiceHooks())
    owners = EnvironmentOwners(Links(connection, bus), Users(connection, bus), scope.environments)
    docs, revisions = Docs(connection, bus, scope, visible), DocRevisions(connection, bus, scope, Links(connection, bus), visible)
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
    scope = Scope(Environments(connection, bus), Links(connection, bus))
    outgoing = OutgoingChanges(connection, bus)
    bus.listen(ModelEvent, outgoing_recorder(connection, bus, scope, config, outgoing))
    bus.listen(Purged, RecordPurge(outgoing, TeamAccount(config), team_placement(connection, bus, scope, config), ServiceHooks()))
    blocks = IdBlocks(connection, bus)
    base = (ord(name[0]) - ord("a")) * 100_000
    for model in AllModels.MODELS:
        if model.shared:
            blocks.add(model.table(), base + 1, base + 99_999)
    bus.listen(NumberRequest, BlockNumbers(blocks, TeamAccount(config), BlockSupply(TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS)), blocks, SharedTables(connection, bus), TeamAccount(config))))
    bus.listen(Deleted, UnlinkDeleted(Links(connection, bus)))
    bus.listen(EnvironmentUnshared, RecordWithdrawal(outgoing, TeamAccount(config), environment_withdrawal(config, connection, bus, scope), ServiceHooks()))
    bus.listen(SyncedDeletion, PulledFileRemoval(Attachments(config, PendingUploads(connection, bus), TeamAccount(config), TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS)))))
    return bus, scope, tasks_of(connection, bus, scope), outgoing, IncomingChanges(SharedTables(connection, bus), outgoing, Links(connection, bus), TeamAccount(config), JournalBackup(connection), config)


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
    rows_a, rows_b = SharedTables(tasks_a.connection, tasks_a.bus), SharedTables(tasks_b.connection, tasks_b.bus)
    links_a, links_b = Links(tasks_a.connection, tasks_a.bus), Links(tasks_b.connection, tasks_b.bus)

    hub = scope_a.environments.save(Environment(name="hub", kind=EnvironmentKind.SESSION), USER)
    shared = scope_a.environments.save(Environment(name="mine"), USER)
    links_a.save(Link(source=Ref.build(User(id=1)), target=Ref.build(shared), kind="owner"), USER)
    with scope_a.environment(hub.id):
        hub_task = tasks_a.save(Task(environment_id=hub.id, title="the hub's task"), actor=USER)
    sharing = EnvironmentSharing(scope_a.environments, EnvironmentOwners(links_a, Users(tasks_a.connection, tasks_a.bus), scope_a.environments), TeamAccount(Config(tmp_path / "a")))
    shared = sharing.shared(shared, USER)
    with scope_a.environment(shared.id):
        task = tasks_a.save(Task(environment_id=shared.id, title="mine"), actor=USER)
        plan = rows_a.rows("plans").save(Plan(environment_id=shared.id, title="my plan"), USER)
        messages = [rows_a.rows("messages").save(Message(environment_id=shared.id, text=text, files=files), USER) for text, files in (("hello", ("note.txt",)), ("again", ()))]
        to_hub = links_a.save(Link(source=Ref.build(task), target=Ref.build(hub_task), kind="follows"), USER)
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
        message = SharedTables(tasks_a.connection, tasks_a.bus).rows("messages").save(Message(environment_id=shared.id, text="hello"), USER)
    carried()
    before = team.log.head()
    withdrawn = [("environments", shared.id), ("tasks", task.id), ("messages", message.id)]
    scope_a.environments.save(scope_a.environments.find(shared.id).unshared(), USER)
    carried()
    [backup] = (tmp_path / "b" / ".journal").glob("journal-before-withdrawal-*.db")
    held = sqlite3.connect(backup)
    assert all(held.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id,)).fetchone() for table, id in withdrawn), "the backup is written before the withdrawn rows are deleted, so it holds every one of them"
    held.close()
    rows_b = SharedTables(tasks_b.connection, tasks_b.bus)
    assert not any(rows_b.rows(table).matching(id=id) for table, id in withdrawn), "and then they are deleted"

    (tmp_path / "c").mkdir()
    shutil.copy(backup, tmp_path / "c" / "journal.db")
    _, _, tasks_c, _, incoming_c = team_journal(tmp_path, "c")
    (tmp_path / "c" / ".journal" / TEAM_FILE).write_text(json.dumps({"account_id": 2}))
    rows_c = SharedTables(tasks_c.connection, tasks_c.bus)
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
    rows_a, rows_b = SharedTables(tasks_a.connection, tasks_a.bus), SharedTables(tasks_b.connection, tasks_b.bus)
    kept = [rows_a.rows(row.table()).save(row, USER) for row in (Rule(text="a rule"), Template(title="a template"), Trigger(phrases=("a phrase",)), Check(title="a check", command="true"), Sequence(title="a sequence"))]
    private = scope_a.environments.save(Environment(name="private"), USER)
    shared = scope_a.environments.save(Environment(name="open", team_key="k1"), USER)
    chat = scope_a.environments.save(Environment.session(team.details.answer().key, "team"), USER)
    owner = Links(tasks_a.connection, tasks_a.bus).save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), kind="owner"), USER)
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
    environments_a, links_a, links_b = scope_a.environments, Links(tasks_a.connection, tasks_a.bus), Links(tasks_b.connection, tasks_b.bus)
    environments_a.save(Environment(name="main"), USER)
    second = environments_a.save(Environment(name="second"), USER)
    with scope_a.environment(1):
        first = tasks_a.save(Task(environment_id=1, title="first"), actor=USER)
        other = tasks_a.save(Task(environment_id=1, title="other"), actor=USER)
        links_a.save(Link(source=Ref.build(first), target=Ref.build(other), kind="follows"), actor=USER)
    with scope_a.environment(second.id):
        tasks_a.save(Task(environment_id=second.id, title="in the second"), actor=USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert len(tasks_b.global_matching(environment_id=1)) == 2 and len(tasks_b.global_matching(environment_id=second.id)) == 1 and len(links_b.rows()) == 1
    with scope_a.environment(1):
        tasks_a.delete(first, USER)
    environments_a.wipe(second, USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert [task.title for task in tasks_b.global_matching(environment_id=1)] == ["other"] and tasks_b.global_matching(environment_id=second.id) == [] and links_b.rows() == [], "the deleted task's links and the wiped environment's rows are gone on the other journal too"
    assert [environment.name for environment in Environments(tasks_b.connection, tasks_b.bus).rows()] == [environment.name for environment in environments_a.rows()]


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
    templates_a, templates_b = Templates(tasks_a.connection, tasks_a.bus), Templates(tasks_b.connection, tasks_b.bus)
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
    settings_a, settings_b = SettingRows(tasks_a.connection, tasks_a.bus, scope_a), SettingRows(tasks_b.connection, tasks_b.bus, scope_b)
    settings_a.set(WorkersOptions.WORKER_LIMIT.key, 3, USER)
    settings_a.set(WorkersOptions.PREPARATION_COMMANDS.key, ["make env"], USER)
    settings_a.set(VoicesOptions.NAME.key, "Ada", USER)
    incoming_b.apply(team_changes(outgoing_a))
    assert settings_b.project_values() == {WorkersOptions.WORKER_LIMIT.key: 3}, "the team's setting arrives; the machine's commands and the person's name stay where they were set"
    from journal.repositories.shared_tables import SharedTables
    from journal.sync.journal_copy import JournalCopy
    from sync_server.copied_row import CopiedRow
    copied = JournalCopy(SharedTables(tasks_a.connection, tasks_a.bus), team_scopes(tasks_a.connection, tasks_a.bus, scope_a), team_placement(tasks_a.connection, tasks_a.bus, scope_a, Config(tmp_path / "a"))).rows()
    assert sorted(row.fields["key"] for row in copied if row.row_table == "settings") == [WorkersOptions.WORKER_LIMIT.key], "the first upload carries the team's settings alone"
    settings_b.set(WorkersOptions.PREPARATION_COMMANDS.key, ["make mine"], USER)
    copy_b = JournalCopy(SharedTables(tasks_b.connection, tasks_b.bus), team_scopes(tasks_b.connection, tasks_b.bus, scope_b), team_placement(tasks_b.connection, tasks_b.bus, scope_b, Config(tmp_path / "b")))
    stray = [CopiedRow("settings", 900, {"environment_id": 0, "key": WorkersOptions.PREPARATION_COMMANDS.key, "value": "[\"make theirs\"]"}, {})]
    former = [CopiedRow("tasks", 901, {"environment_id": 1, "title": "kept from before the rename", "state": "parked"}, {})]
    copy_b.replace_whole(tuple(copied) + tuple(stray) + tuple(former))
    assert settings_b.project(WorkersOptions.PREPARATION_COMMANDS.key) == ["make mine"] and settings_b.project(WorkersOptions.WORKER_LIMIT.key) == 3, "a download keeps this machine's own settings and takes the team's"
    assert tasks_b.find(901).state == TaskState.PAUSED, "a team row in a state's former name is read in its new one"


def test_the_migration_preview_writes_nothing_and_names_what_the_run_withdraws_and_the_servers_backup_brings_the_earlier_rows_back(tmp_path):
    from journal.models.environment import Environment
    from journal.models.rule import Rule
    from journal.models.user import User
    from journal.repositories.shared_tables import SharedTables
    from journal.support.rejection import Rejection

    team, (_, scope_a, tasks_a, outgoing_a, _), _, carried = served_team_journals(tmp_path)
    server = team.started("127.0.0.1", 0)
    served_link(team, server, tmp_path, "a", "ada@example.com", 1)
    links_a = Links(tasks_a.connection, tasks_a.bus)
    try:
        rule = SharedTables(tasks_a.connection, tasks_a.bus).rows("rules").save(Rule(text="a rule"), USER)
        private = scope_a.environments.save(Environment(name="mine"), USER)
        links_a.save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), kind="owner"), USER)
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
    rows_a, rows_b, links_a = SharedTables(tasks_a.connection, tasks_a.bus), SharedTables(tasks_b.connection, tasks_b.bus), Links(tasks_a.connection, tasks_a.bus)
    migration = team_migration(tmp_path, "a", scope_a, tasks_a, outgoing_a)
    try:
        ada_own, bob_own = (scope_a.environments.save(Environment(name=name), USER) for name in ("ada-own", "bob-own"))
        shared = scope_a.environments.save(Environment(name="open", team_key=team.details.answer().key), USER)
        for person, environment in ((1, ada_own), (2, bob_own)):
            links_a.save(Link(source=Ref.build(User(id=person)), target=Ref.build(environment), kind="owner"), USER)
        with scope_a.environment(ada_own.id):
            ada_plan = rows_a.rows("plans").save(Plan(environment_id=ada_own.id, title="Ada's plan"), USER)
            ada_task = tasks_a.save(Task(environment_id=ada_own.id, title="Ada's task"), actor=USER)
        with scope_a.environment(bob_own.id):
            bob_task = tasks_a.save(Task(environment_id=bob_own.id, title="Bob's task"), actor=USER)
        with scope_a.environment(shared.id):
            message = rows_a.rows("messages").save(Message(environment_id=shared.id, text="in the open"), USER)
        doc = migration.docs.save(Doc(title="how we work", body="the guide"), USER)
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
    settings_a, settings_b = SettingRows(tasks_a.connection, tasks_a.bus, scope_a), SettingRows(tasks_b.connection, tasks_b.bus, scope_b)
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
    environments = Environments(tasks.connection, bus)
    hub, session, shared, private = (environments.save(row, USER) for row in (Environment.hub("k1", "acme"), Environment.session("k1", "team"), Environment(name="open", team_key="k1"), Environment(name="mine")))
    placement = TeamPlacement(SharedTables(tasks.connection, bus), team_scopes(tasks.connection, bus, scope), TeamAccount(config))
    placed = lambda *rows: [placement.team_key(row) for row in rows]

    work = {}
    for environment in (hub, session, shared, private):
        with scope.environment(environment.row_id):
            work[environment.name] = tasks.save(Task(environment_id=environment.row_id, title=f"in {environment.name}"), USER)
    assert placed(hub, session, shared, private) == ["k1", "k1", "k1", ""], "an environment is in its team when it is the hub, a session or shared, and a private one in none"
    assert placed(*(work[name] for name in ("acme", "team", "open", "mine"))) == ["k1", "k1", "k1", ""], "a row of an environment is placed with its environment, whose chat is shared or not"
    links = Links(tasks.connection, bus)
    together = links.save(Link(source=Ref.build(work["acme"]), target=Ref.build(work["team"]), kind="mentions"), USER)
    apart = links.save(Link(source=Ref.build(work["mine"]), target=Ref.build(work["acme"]), kind="copied_from"), USER)
    owner = links.save(Link(source=Ref.build(User(id=1)), target=Ref.build(private), kind="owner"), USER)
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
    environments_a, environments_b = Environments(tasks_a.connection, tasks_a.bus), Environments(tasks_b.connection, tasks_b.bus)
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
    checks_a, checks_b = Checks(tasks_a.connection, tasks_a.bus), Checks(tasks_b.connection, tasks_b.bus)
    check = checks_a.save(Check(title="lint", command="true", interval=5), USER)
    sent = len(outgoing_a.waiting())
    checks_a.save(check.completed(True, "all clean", datetime.now(timezone.utc), 0.1, None, ""), USER)
    assert len(outgoing_a.waiting()) == sent, "a run's results leave no change for the team, not even its stamps"
    incoming_b.apply(team_changes(outgoing_a))
    arrived = checks_b.find(check.row_id)
    assert arrived.title == "lint" and arrived.last_output == "" and arrived.last_run_at is None, "the check reaches the other journal without the first machine's run"


def test_a_write_queued_before_a_column_rename_is_sent_under_the_new_name(connection, bus):
    from journal.db.migration import Migration
    from journal.models.outgoing_change import UPDATED, OutgoingChange
    from journal.repositories.outgoing_changes import OutgoingChanges

    connection.execute("ALTER TABLE tasks ADD COLUMN headline TEXT")
    outgoing = OutgoingChanges(connection, bus)
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
    connection.execute("CREATE INDEX entries_dispatches ON entries (environment_id, id) WHERE kind = 'Stop'")
    Indexes(connection, INDEXES).refresh()
    assert connection.result("SELECT sql FROM sqlite_master WHERE name = 'entries_dispatches'")[0] == next(index.sql() for index in INDEXES if index.name == "entries_dispatches"), "an index made under an older definition is made again under the current one"
    connection.close()


def test_a_transaction_reads_its_own_writes_even_when_another_thread_stored_the_table_meanwhile(connection, bus):
    """Two links made in one transaction once took one number: a reader on another thread stored the blocks as committed, and the writer read that copy back, missing its own write."""
    import threading
    from journal.repositories.id_blocks import IdBlocks
    blocks = IdBlocks(connection, bus)
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
    agents = Agents(connection, bus, scope)
    with scope.environment(1):
        agent = agents.save(Agent(environment_id=1, session="s1", provider="claude"), USER)
        agents.session_agent("s1")
        changed = agents.save(agents.find(agent.id).with_(tool_uses=3, sequence_runs=({"name": "n"},), skills_due=("a",)), USER)
        agents.touch(changed, USER, is_overview_read=False)
        LoadTally.begin()
        found, by_session = agents.find(agent.id), agents.session_agent("s1")
        assert LoadTally.ended().points() == 0, "both reads are answered from the writes"
        connection.cache.cleared()
        assert found == by_session == agents.find(agent.id) and found.sequence_runs == ({"name": "n"},) and found.is_overview_read is False, "as a load returns it"
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
    from journal.models.agent_role import AgentRole
    agents = Agents(connection, bus, scope)
    with scope.environment(1):
        own = agents.save(Agent(environment_id=1, session="own", provider="claude"), USER)
        agents.save(Agent(environment_id=1, session="peer", provider="claude"), USER)
        agents.save(Agent(environment_id=1, session="codex", provider="codex"), USER)
        agents.save(Agent(environment_id=1, session="worker", provider="claude", role=AgentRole.WORKER), USER)
        agents.save(Agent(environment_id=1, session="ended", provider="claude", state="ended", sequence_runs=({"name": "n"},)), USER)
        agents.save(Agent(environment_id=1, session="ended-bare", provider="claude", state="ended"), USER)
        assert [agent.session for agent in agents.running_peers(own)] == ["peer"], "a running main agent of its provider"
        assert [agent.session for agent in agents.ended_sequence_agents("own")] == ["ended"], "an ended agent with sequence runs"
        start = datetime.now(timezone.utc) - timedelta(minutes=10)
        assert [agent.session for agent in agents.recent_peers("own", start)] == ["peer", "codex", "worker"], "an agent ended a moment after it began is no peer"
        assert agents.recent_peers("own", datetime.now(timezone.utc) + timedelta(minutes=1)) == []
