import json
from pathlib import Path

import pytest

from tests.replay import catch_typed, drive_the_clock
from tests.stories.builder.coverage_gaps import CoverageGaps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.path_overlay import PathOverlay
from tests.stories.builder.story import Story
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.story_marks import ENDS_IN_MARK, PROVIDER_MARK, SETTINGS_MARK, STARTS_FROM_MARK
from tests.stories.builder.void_provider import VoidProvider
from tests.test_features import booted
from journal.config import Config
from journal.engine.nudge_registry import NudgeRegistry
from journal.features.faults.support.story_transitions import StoryTransitions
from journal.features.registry import Registry

OVERLAYS = pytest.StashKey[dict[str, PathOverlay]]()
SCENARIOS_RUN = pytest.StashKey[int]()
GAPS = pytest.StashKey[CoverageGaps]()
WALKED = pytest.StashKey[set[str]]()
REPOSITORY = Path(__file__).resolve().parents[2]
STORIES = Path(__file__).parent
STEPS_AND_FIXTURES = ("builder", "fixtures")
collect_ignore = list(STEPS_AND_FIXTURES)


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture(scope="module")
def copies():
    return FixtureCopies()


@pytest.fixture
def story(app, monkeypatch, request, copies):
    """A story played once, on the VoidProvider or the provider its @provider names, on the module's journal from the state its starts_from names, lines typed to the agent caught and seen back at once; its path is kept for the run's overlay once it ends, and a story fails when a setting it set was never read by the journal after."""
    catch_typed(app, monkeypatch, [])
    drive_the_clock(app, monkeypatch)
    reads = SettingReads()
    reads.watch(monkeypatch)
    program = request.node.get_closest_marker(PROVIDER_MARK)
    played = Story(app, program.args[0] if program else VoidProvider, reads, copies)
    for mark in request.node.iter_markers(STARTS_FROM_MARK):
        played.starts_from(mark.args[0])
    for mark in reversed(list(request.node.iter_markers(SETTINGS_MARK))):
        played.user_sets(*mark.args)
    yield played
    for mark in request.node.iter_markers(ENDS_IN_MARK):
        played.expect_stack(*(played.end_stack if played.end_stack is not None else mark.args))
    unused = played.start.rows_never_used()
    assert not unused, f"starts from {type(played.start).__name__} but never used {', '.join(unused)}: start from a fixture whose rows it uses"
    unread = played.settings_never_read()
    assert not unread, f"set by the story but never read by the journal after: {', '.join(unread)}"
    gaps = request.config.stash.setdefault(GAPS, CoverageGaps())
    gaps.known([nudge.key for nudge in app.container.get(NudgeRegistry).all()], [option.key for option in app.container.get(Registry).options()])
    gaps.played(played.said_keys, set(reads.keys))
    overlays = request.config.stash.setdefault(OVERLAYS, {})
    overlays.setdefault(played.program.__name__, PathOverlay()).add(request.node.originalname, played.path)
    request.config.stash.setdefault(WALKED, set()).update(played.log.walked)
    request.config.stash[SCENARIOS_RUN] = request.config.stash.get(SCENARIOS_RUN, 0) + 1


def pytest_sessionfinish(session, exitstatus) -> None:
    """Once every story of the run has played, the run prints the nudges no story made the journal say and the settings none made it read, by feature, and lays their paths over each other per provider: a story reaching nothing of its own, or two walking one path, fail the run with what to do."""
    collected = [item for item in session.items if "story" in getattr(item, "fixturenames", ())]
    if not collected or session.config.stash.get(SCENARIOS_RUN, 0) < len(collected) or session.config.option.keyword:
        return
    if {Path(item.fspath) for item in collected} >= {path for path in STORIES.glob("*/*.py") if path.parent.name not in STEPS_AND_FIXTURES and path.name != "__init__.py"}:
        write_walked(session.config.stash.get(WALKED, set()))
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    failures, warnings = [], []
    for provider, overlay in session.config.stash.get(OVERLAYS, {}).items():
        failures += [f"[{provider}] {line}" for line in overlay.failures()]
        warnings += [f"[{provider}] {line}" for line in overlay.warnings()]
    for line in session.config.stash.get(GAPS, CoverageGaps()).lines():
        reporter.write_line(line)
    for line in warnings:
        reporter.write_line(f"story paths, drifting together: {line}")
    for line in failures:
        reporter.write_line(f"story paths, failed: {line}", red=True)
    if failures:
        session.exitstatus = 1


def write_walked(walked: set[str]) -> None:
    """The kinds of stack change every story of a whole run walked, for journal developer transitions to mark the ones none walks."""
    walked_path = StoryTransitions.walked_path(Config(root=REPOSITORY))
    walked_path.parent.mkdir(parents=True, exist_ok=True)
    walked_path.write_text(json.dumps(sorted(walked)))
