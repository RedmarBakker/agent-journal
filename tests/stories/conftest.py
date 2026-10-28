import json
from pathlib import Path

import pytest

from tests.replay import typing_capture, pinned_clock
from tests.stories.builder.coverage_gaps import CoverageGaps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.path_overlay import PathOverlay
from tests.stories.builder.story import Story
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.story_marks import PROVIDER_MARK, SETTINGS_MARK, START_MARK
from tests.stories.builder.void_provider import VoidProvider
from tests.test_features import booted
from journal.config import Config
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


def pytest_configure(config) -> None:
    config.stash[SEEDINGS] = []


@pytest.fixture(scope="module")
def boot():
    return booted


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
    played.scope = AgentRole(Path(request.node.path).relative_to(STORIES).parts[0])
    for mark in reversed(list(request.node.iter_markers(SETTINGS_MARK))):
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
    if {Path(item.fspath) for item in collected} >= {path for path in STORIES.glob("*/*/*.py") if path.parent.parent.name not in SUPPORT_FOLDERS and path.name != "__init__.py"}:
        record_walked_kinds(session.config.stash.get(WALKED, set()))
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    failures, warnings = [], []
    for provider, overlay in session.config.stash.get(OVERLAYS, {}).items():
        failures += [f"[{provider}] {line}" for line in overlay.failures()]
        warnings += [f"[{provider}] {line}" for line in overlay.warnings()]
    fixtures: dict[str, PathOverlay] = {}
    for fixture_copies in session.config.stash[SEEDINGS]:
        for (fixture, provider), path in fixture_copies.seedings.items():
            fixtures.setdefault(provider, PathOverlay()).add(fixture.__name__, path)
    for provider, overlay in fixtures.items():
        failures += [f"[fixtures on {provider}] {line}" for line in overlay.failures() if " reaches nothing " not in line]
        failures += [f"[fixtures on {provider}] {name} adds no step to the fixture it starts from" for name, path in overlay.paths.items() if len(path) < 2]
    for line in session.config.stash.get(GAPS, CoverageGaps()).lines():
        reporter.write_line(line)
    for line in warnings:
        reporter.write_line(f"story paths, drifting together: {line}")
    for line in failures:
        reporter.write_line(f"story paths, failed: {line}", red=True)
    if failures:
        session.exitstatus = 1


def record_walked_kinds(walked: set[str]) -> None:
    walked_path = StoryTransitions.walked_path(Config(root=REPOSITORY))
    walked_path.parent.mkdir(parents=True, exist_ok=True)
    walked_path.write_text(json.dumps(sorted(walked)))
