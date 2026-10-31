import json
import os
import sys
import threading
from pathlib import Path

import pytest

from tests.agent_hooks import typing_capture, pinned_clock
from tests.stories.builder.coverage_gaps import CoverageGaps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.path_overlay import PathOverlay
from tests.stories.builder.story import Story
from tests.stories.builder.story_run_record import STORY_RECORDS_VARIABLE, StoryRunRecord
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.story_marks import PROVIDER_MARK, SETTINGS_MARK, START_MARK
from tests.stories.builder.void_provider import VoidProvider
from tests.test_features import booted
from journal.app import App
from journal.config import Config
from journal.events.rows.worker_session_bound import WorkerSessionBound
from journal.providers.support.helper_runner import HelperRunner
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker import Worker
from journal.providers.claude import Claude
from journal.support.actor import Actor
from tests.stories.builder.worker_steps import worker_session
from journal.support.agent_role import AgentRole
from journal.engine.nudge_registry import NudgeRegistry
from journal.features.faults.support.story_transitions import StoryTransitions
from journal.features.updates.support.release_check import ReleaseCheck
from journal.features.updates.support.release_check_memory import ReleaseCheckMemory
from journal.features.registry import Registry
from journal.support.time_source import TimeSource
from tests.template_copy import copied
from tests.shared_journal import SharedJournal

OVERLAYS = pytest.StashKey[dict[str, PathOverlay]]()
SCENARIOS_RUN = pytest.StashKey[int]()
GAPS = pytest.StashKey[CoverageGaps]()
WALKED = pytest.StashKey[set[str]]()
SEEDINGS = pytest.StashKey[list[FixtureCopies]]()
REPOSITORY = Path(__file__).resolve().parents[2]
STORIES = Path(__file__).parent
SUPPORT_FOLDERS = ("builder", "fixtures")
collect_ignore = list(SUPPORT_FOLDERS)
# a story file named *_run.py drives a process and is excluded unless named or enabled here
PROCESS_STORIES = "JOURNAL_PROCESS_STORIES"
requested_process_story = any(Path(argument.split("::", 1)[0]).name.endswith("_run.py") for argument in sys.argv[1:])
collect_ignore_glob = [] if os.environ.get(PROCESS_STORIES) or requested_process_story else ["*/*/*_run.py"]


def pytest_configure(config) -> None:
    config.stash[SEEDINGS] = []


@pytest.fixture(scope="session")
def journal(tmp_path_factory, template_journal: Path) -> SharedJournal:
    """The one journal every story of this run's process plays in, put back after each story, so the fixtures it seeds are seeded once for the process and every story file starts from their copies."""
    with pytest.MonkeyPatch.context() as patch:
        app = story_booted(copied(template_journal, tmp_path_factory.mktemp("stories")), patch)
        yield SharedJournal(app)
        app.runtime().stop()


def story_booted(root: Path, patch: pytest.MonkeyPatch) -> App:
    """The journal a story runs against: booted as the tests boot it, and a reviewer or verifier the journal sends is never started, its launch kept on the app with the variables its program would have had, its token among them, so the story plays its hooks instead; a worker's program is never started either, though a worker on Claude is given its session at launch, as the real launch gives it one."""
    launches: list[dict[str, str]] = []
    launches_ready = threading.Condition()
    original_run = HelperRunner.run
    original_worker_start = WorkerRunner.start

    def capture_launch(runner, helper, command, environ) -> None:
        if runner.config.root == root:
            with launches_ready:
                launches.append(environ)
                launches_ready.notify_all()
            return
        original_run(runner, helper, command, environ)

    patch.setattr(HelperRunner, "run", capture_launch)
    ReleaseCheckMemory().store(ReleaseCheck(TimeSource().seconds()))
    app = booted(root, patch)
    patch.setattr(WorkerRunner, "start", worker_session_given)
    app.original_worker_start = original_worker_start
    app.helper_launches = launches
    app.helper_launches_ready = launches_ready
    return app


def worker_session_given(runner: WorkerRunner, worker: Worker, actor: Actor) -> None:
    if worker.provider == Claude.name:
        session = worker.resume or worker_session(worker.id)
        bound = worker.with_(session=session)
        if not worker.session:
            bound = bound.with_event(WorkerSessionBound(environment_id=worker.environment_id))
        runner.workers.save(bound, actor)


def home_inside_the_story_folder(root: Path, patch: pytest.MonkeyPatch) -> None:
    (root / "home" / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    patch.setenv("HOME", str(root / "home"))
    patch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    patch.delenv("CODEX_HOME", raising=False)
    patch.delenv("XDG_CONFIG_HOME", raising=False)
    patch.delenv("AGENT_JOURNAL_SECRETS", raising=False)


@pytest.fixture(scope="session")
def copies(request):
    fixture_copies = FixtureCopies()
    request.config.stash[SEEDINGS].append(fixture_copies)
    return fixture_copies


@pytest.fixture
def story(app, monkeypatch, request, copies):
    home_inside_the_story_folder(app.config.root, monkeypatch)
    typed: list[str] = []
    typing_capture(app, monkeypatch, typed)
    pinned_clock(app, monkeypatch)
    reads = SettingReads()
    reads.watch(monkeypatch)
    program = request.node.get_closest_marker(PROVIDER_MARK)
    played = Story(app, program.args[0] if program else VoidProvider, reads, copies)
    played.typed = typed
    played.monkeypatch = monkeypatch
    for mark in request.node.iter_markers(START_MARK):
        played.reach(mark.args[0])
        played.plays_in(request.param if isinstance(mark.args[1], tuple) else mark.args[1])
    played.scope = story_scope(request)
    for mark in request.node.iter_markers(SETTINGS_MARK):
        played.user_sets(*mark.args)
    yield played
    for close in played.closers:
        close()
    if request.node.rep_call.failed:
        return
    assert played.is_stack_checked_last(), f"{request.node.originalname} does not close with story.expect_stack(story.agents.subject, ...) after its last step: every story says the stack it ends on"
    unused = played.fixture.unused_rows()
    assert not unused, f"starts from {type(played.fixture).__name__} but never used {', '.join(unused)}: start from a fixture whose rows it uses"
    unread = played.unread_settings()
    assert not unread, f"set by the story but never read by the journal after: {', '.join(unread)}"
    gaps = request.config.stash.setdefault(GAPS, CoverageGaps())
    gaps.known([nudge.key for nudge in app.container.get(NudgeRegistry).all()], [option.key for option in app.container.get(Registry).options()])
    gaps.played(played.line_keys, set(reads.keys))
    overlays = request.config.stash.setdefault(OVERLAYS, {})
    overlays.setdefault(f"{played.program.__name__} {played.mode}", PathOverlay()).add(request.node.name, played.path)
    request.config.stash.setdefault(WALKED, set()).update(played.log.walked)
    request.config.stash[SCENARIOS_RUN] = request.config.stash.get(SCENARIOS_RUN, 0) + 1


def pytest_generate_tests(metafunc) -> None:
    start = metafunc.definition.get_closest_marker(START_MARK)
    if start is not None and isinstance(start.args[1], tuple):
        metafunc.parametrize("story", start.args[1], indirect=True, ids=list(start.args[1]))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    report = (yield).get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_terminal_summary(terminalreporter) -> None:
    seeded = sum(len(fixture_copies.seedings) for fixture_copies in terminalreporter.config.stash.get(SEEDINGS, []))
    if seeded:
        terminalreporter.write_line(f"story fixtures seeded: {seeded}")


def pytest_sessionfinish(session, exitstatus) -> None:
    collected = [item for item in session.items if "story" in getattr(item, "fixturenames", ())]
    if not collected or session.config.stash.get(SCENARIOS_RUN, 0) < len(collected) or session.config.option.keyword:
        return
    record = stashed_record(session.config)
    if os.environ.get(STORY_RECORDS_VARIABLE):
        record.saved(Path(os.environ[STORY_RECORDS_VARIABLE]) / f"stories-{os.getpid()}.json")
        return
    if {Path(item.fspath) for item in collected} >= story_files():
        record_walked_kinds(record.walked)
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    for line, is_failure in record.report_lines():
        reporter.write_line(line, red=is_failure)
    if record.failures():
        session.exitstatus = 1


def story_scope(request) -> AgentRole:
    named, folder = request.node.get_closest_marker(START_MARK).args[2], AgentRole(Path(request.node.path).relative_to(STORIES).parts[0])
    assert named == folder, f"{request.node.originalname} names subject {named.value} on its mark but lives under {folder.value}/: the mark and the folder name the same subject"
    return named


def stashed_record(config) -> StoryRunRecord:
    fixture_paths: dict[str, dict[str, list[str]]] = {}
    for fixture_copies in config.stash[SEEDINGS]:
        for (fixture, provider), path in fixture_copies.seedings.items():
            fixture_paths.setdefault(provider, {})[fixture.__name__] = path
    story_paths = {key: overlay.paths for key, overlay in config.stash.get(OVERLAYS, {}).items()}
    return StoryRunRecord(story_paths, fixture_paths, config.stash.get(GAPS, CoverageGaps()), config.stash.get(WALKED, set()))


def story_files() -> set[Path]:
    return {path for path in STORIES.glob("*/*/*.py") if path.parent.parent.name not in SUPPORT_FOLDERS and path.name != "__init__.py" and not path.name.endswith("_run.py")}


def record_walked_kinds(walked: set[str]) -> None:
    walked_path = StoryTransitions.walked_path(Config(root=REPOSITORY))
    walked_path.parent.mkdir(parents=True, exist_ok=True)
    walked_path.write_text(json.dumps(sorted(walked)))
