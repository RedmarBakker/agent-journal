import json
import os
from pathlib import Path

import pytest

from tests.replay import typing_capture, pinned_clock
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
from journal.providers.support.helper_runner import HelperRunner
from journal.support.agent_role import AgentRole
from journal.engine.nudge_registry import NudgeRegistry
from journal.features.faults.support.story_transitions import StoryTransitions
from journal.features.registry import Registry

OVERLAYS = pytest.StashKey[dict[str, PathOverlay]]()
SCENARIOS_RUN = pytest.StashKey[int]()
GAPS = pytest.StashKey[CoverageGaps]()
WALKED = pytest.StashKey[set[str]]()
SEEDINGS = pytest.StashKey[list[FixtureCopies]]()
REPOSITORY = Path(__file__).resolve().parents[2]
STORIES = Path(__file__).parent
SUPPORT_FOLDERS = ("builder", "fixtures")
collect_ignore = list(SUPPORT_FOLDERS)
# a story file named *_run.py drives a process (git, a worker's worktree) and runs only when this variable asks for it
PROCESS_STORIES = "JOURNAL_PROCESS_STORIES"
collect_ignore_glob = [] if os.environ.get(PROCESS_STORIES) else ["*/*/*_run.py"]


def pytest_configure(config) -> None:
    config.stash[SEEDINGS] = []


@pytest.fixture(scope="module")
def boot():
    return story_booted


def story_booted(root: Path, patch: pytest.MonkeyPatch) -> App:
    """The journal a story runs against: booted as the tests boot it, and a reviewer or verifier the journal sends is never started, its launch kept on the app with the variables its program would have had, its token among them, so the story plays its hooks instead."""
    launches: list[dict[str, str]] = []
    patch.setattr(HelperRunner, "run", lambda self, helper, command, environ: launches.append(environ))
    app = booted(root, patch)
    app.helper_launches = launches
    return app


@pytest.fixture(scope="module")
def copies(request):
    fixture_copies = FixtureCopies()
    request.config.stash[SEEDINGS].append(fixture_copies)
    return fixture_copies


@pytest.fixture
def story(app, monkeypatch, request, copies):
    typing_capture(app, monkeypatch, [])
    pinned_clock(app, monkeypatch)
    reads = SettingReads()
    reads.watch(monkeypatch)
    program = request.node.get_closest_marker(PROVIDER_MARK)
    played = Story(app, program.args[0] if program else VoidProvider, reads, copies)
    for mark in request.node.iter_markers(START_MARK):
        played.reach(mark.args[0])
        played.plays_in(request.param if isinstance(mark.args[1], tuple) else mark.args[1])
    played.scope = story_scope(request)
    for mark in request.node.iter_markers(SETTINGS_MARK):
        played.user_sets(*mark.args)
    yield played
    if request.node.rep_call.failed:
        return
    assert played.is_stack_checked_last(), f"{request.node.originalname} does not close with story.expect_stack(...) after its last step: every story says the stack it ends on"
    unused = played.start.unused_rows()
    assert not unused, f"starts from {type(played.start).__name__} but never used {', '.join(unused)}: start from a fixture whose rows it uses"
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
    assert named == folder, f"{request.node.originalname} names scope {named.value} on its mark but lives under {folder.value}/: the mark and the folder say the same scope"
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
