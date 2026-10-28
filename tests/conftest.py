import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

import pytest

from journal.app import App
from journal.config import Config
from journal.support.large_reads import LargeReads
from journal.support.masks import Masks
from journal.support.query_times import QueryTimes
from journal.support.stage_times import StageTimes
from journal.features.faults.support.test_run_files import TEST_RUN_KEY
from journal.support.secret_values import SecretValues

from journal.db.connection import Connection
from journal.db.schema import Schema
from journal.events.bus import Bus
from journal.models.all_models import AllModels
from journal.repositories.environments import Environments
from journal.repositories.entries import CUT_KEY, Entries
from journal.repositories.links import Links
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.setting_rows import SettingRows
from journal.models.setting import Setting
from journal.support.actor import Actor
from tests.shard_deal import ShardDeal
from tests.shared_journal import SharedJournal
from journal.features.voices.voices_options import VoicesOptions
from journal.support.time_source import TimeSource

# the folder whose stories go to one shard together
SCENARIOS_FOLDER = "tests/scenarios/"


os.environ["AGENT_JOURNAL_SECRETS"] = tempfile.mkdtemp(prefix="journal-test-values-")
os.environ["AGENT_JOURNAL_MACHINE"] = tempfile.mkdtemp(prefix="journal-test-machine-")
"""Every journal a test boots keeps what a machine shares, such as its last look at GitHub for releases, in a scratch folder, never the user's own."""
"""Every test, and every journal a test boots, keeps its secret values in a scratch folder, never the user's own."""

STAND_INS = Path(__file__).resolve().parent / "programs"
LIVE_SUFFIX = "_live_run"

TESTS_MARK = Path(__file__).resolve().parent.parent / ".journal" / "runtime" / f"{TEST_RUN_KEY}.{os.getpid()}"


def pytest_sessionstart(session) -> None:
    """The checkout's own journal is told a run is on, so its profiler does not blame itself for the machine the suite crowds."""
    if TESTS_MARK.parent.is_dir():
        TESTS_MARK.touch()


def pytest_sessionfinish(session, exitstatus) -> None:
    TESTS_MARK.unlink(missing_ok=True)
    out = os.environ.get(DURATIONS_OUT_VARIABLE, "")
    if out:
        Path(out).write_text(json.dumps(seconds_taken))
    if os.environ.get(COVERAGE_OUT_VARIABLE):
        shard = os.environ.get(SHARD_VARIABLE, "0/1").split("/")[0]
        (Path(os.environ[COVERAGE_OUT_VARIABLE]) / f"shard-{shard}.coverage.json").write_text(json.dumps(source_files))


@pytest.fixture(scope="module", autouse=True)
def stand_ins(request):
    """Every program a module's tests start finds the stand-ins for Claude Code and Codex first, never the real ones, which reach the network and are billed, and Claude Code's config and state live in a temp folder, never the person's own; a live file, which says so on its first line, keeps the real ones."""
    if request.module.__name__.endswith(LIVE_SUFFIX):
        yield
        return
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("PATH", f"{STAND_INS}{os.pathsep}{os.environ['PATH']}")
        patch.setenv("CLAUDE_CONFIG_DIR", tempfile.mkdtemp(prefix="claude-config-"))
        yield


@pytest.fixture
def connection(tmp_path: Path) -> Connection:
    connection = Connection(tmp_path / "journal.db", Masks(SecretValues(Config(tmp_path))), StageTimes(), QueryTimes(), LargeReads())
    Schema(connection, AllModels.MODELS).create()
    yield connection
    connection.close()


@pytest.fixture
def bus() -> Bus:
    return Bus()


@pytest.fixture(scope="session")
def template_journal(tmp_path_factory) -> Path:
    """One journal booted for the whole run, its schema made and its seeds drawn, the user's first name set, so no test's journal asks git for it, workers' tests handed over, so no test needs a test command set to send a worker, and its main environment made, as the user would make it first; a test that boots a journal starts from a copy of it, which boots in a hundredth of the time."""
    root = tmp_path_factory.mktemp("template")
    app = App(Config(root, port=0))
    app.container.get(SettingRows).save(Setting(environment_id=PROJECT, key=VoicesOptions.NAME.key, value="Jesse"), Actor.system())
    app.container.get(SettingRows).save(Setting(environment_id=PROJECT, key="workers.testing", value="Hand the tests over"), Actor.system())
    app.container.get(SettingRows).save(Setting(environment_id=PROJECT, key="plans.test_commands", value="pytest, journal suite"), Actor.system())
    app.container.get(SettingRows).save(Setting(environment_id=PROJECT, key="workers.fitness_warnings", value=True), Actor.system())
    app.runtime().start()
    app.container.get(Environments).lookup("main")
    app.runtime().stop()
    return root


@pytest.fixture
def journal_root(tmp_path: Path, template_journal: Path) -> Path:
    """The test's own journal folder, a copy of the booted template, with a project id of its own so no two tests share secret values."""
    return copied(template_journal, tmp_path)


@pytest.fixture(scope="module")
def journal(tmp_path_factory, template_journal: Path, boot) -> SharedJournal:
    """The journal a module's tests share, a copy of the booted template with a project id of its own, booted by the module's own boot fixture."""
    with pytest.MonkeyPatch.context() as patch:
        app = boot(copied(template_journal, tmp_path_factory.mktemp("module")), patch)
        yield SharedJournal(app)
        app.runtime().stop()


@pytest.fixture
def app(journal: SharedJournal):
    """The module's journal, put back as it booted once the test is done; a line the nudger had to cut to its longest fails the test, naming it."""
    yield journal.app
    cut = []
    for environment in journal.app.container.get(Environments).all():
        with journal.app.container.get(Scope).environment(environment.id):
            cut += [(entry.data["key"], entry.data[CUT_KEY]) for entry in journal.app.container.get(Entries).cut_lines()]
    journal.reset()
    assert not cut, f"lines sent longer than their longest, cut to it (key, length): {cut}"


def copied(template: Path, root: Path) -> Path:
    shutil.copytree(template, root, dirs_exist_ok=True)
    (root / ".journal" / "project-id").unlink(missing_ok=True)
    return root


@pytest.fixture
def scope(connection: Connection, bus: Bus) -> Scope:
    return Scope(Environments(connection, bus, TimeSource()), Links(connection, bus, TimeSource()))


# the shard of a parallel suite this run is, as index/count, set by scripts/suite.py
SHARD_VARIABLE = "JOURNAL_TEST_SHARD"
TALLY_VARIABLE = "JOURNAL_TEST_TALLY"


DURATIONS_IN_VARIABLE = "JOURNAL_TEST_DURATIONS_IN"
DURATIONS_OUT_VARIABLE = "JOURNAL_TEST_DURATIONS_OUT"
seconds_taken: dict[str, float] = {}


def recorded_seconds() -> dict[str, float]:
    path = Path(os.environ.get(DURATIONS_IN_VARIABLE, ""))
    return json.loads(path.read_text()) if path.is_file() else {}


def dealt_unit(nodeid: str) -> str:
    """What a shard is dealt: a test on its own, but the scenarios all together, since their paths are laid over each other at the end of the run that played them."""
    return SCENARIOS_FOLDER if nodeid.startswith(SCENARIOS_FOLDER) else nodeid


def pytest_collection_modifyitems(config, items):
    """A run started as one shard of a parallel suite keeps the tests the deal by last run's seconds gives its shard."""
    shard = os.environ.get(SHARD_VARIABLE, "")
    if not shard:
        return
    index, count = (int(part) for part in shard.split("/"))
    seconds = recorded_seconds()
    dealt = {item.nodeid: dealt_unit(item.nodeid) for item in items}
    unit_seconds = {unit: sum(seconds.get(nodeid, 0.0) for nodeid, owner in dealt.items() if owner == unit) for unit in set(dealt.values())} if seconds else {}
    mine = set(ShardDeal(unit_seconds).shards(sorted(set(dealt.values())), count)[index])
    kept = [item for item in items if dealt[item.nodeid] in mine]
    config.hook.pytest_deselected(items=[item for item in items if item.nodeid not in mine])
    items[:] = kept


def pytest_collection_finish(session) -> None:
    """A shard of the parallel suite, or a run of named tests the suite script counts, prints how many tests it will run, after every deselection, so its progress is counted against it."""
    if os.environ.get(SHARD_VARIABLE) or os.environ.get(TALLY_VARIABLE):
        sys.__stdout__.write(f"collected {len(session.items)} items\n")
        sys.__stdout__.flush()


# set by scripts/suite.py --coverage-map: the folder each shard writes which source files its tests ran to
COVERAGE_OUT_VARIABLE = "JOURNAL_COVERAGE_OUT"
SOURCE_FOLDER = str(Path(__file__).resolve().parent.parent / "src") + os.sep
source_files: dict[str, list[str]] = {}
files_run: set[str] = set()


def code_started(code, offset: int) -> object:
    if code.co_filename.startswith(SOURCE_FOLDER):
        files_run.add("src/" + code.co_filename[len(SOURCE_FOLDER):])
    return sys.monitoring.DISABLE


def pytest_configure(config) -> None:
    if os.environ.get(COVERAGE_OUT_VARIABLE):
        sys.monitoring.use_tool_id(sys.monitoring.COVERAGE_ID, "journal coverage map")
        sys.monitoring.register_callback(sys.monitoring.COVERAGE_ID, sys.monitoring.events.PY_START, code_started)
        sys.monitoring.set_events(sys.monitoring.COVERAGE_ID, sys.monitoring.events.PY_START)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """With the coverage map asked for, each test notes the source files whose code it ran."""
    if not os.environ.get(COVERAGE_OUT_VARIABLE):
        return (yield)
    files_run.clear()
    sys.monitoring.restart_events()
    outcome = yield
    source_files[item.nodeid] = sorted(files_run)
    return outcome


def pytest_runtest_logreport(report) -> None:
    seconds_taken[report.nodeid] = seconds_taken.get(report.nodeid, 0.0) + report.duration
