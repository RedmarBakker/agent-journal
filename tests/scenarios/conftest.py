import pytest

from tests.replay import PROVIDERS, catch_typed
from tests.scenarios.builder.path_overlay import PathOverlay
from tests.scenarios.builder.scenario import Scenario
from tests.scenarios.builder.setting_reads import SettingReads
from tests.scenarios.builder.story_values import STARTS_FROM_MARK
from tests.test_features import booted

OVERLAYS = pytest.StashKey[dict[str, PathOverlay]]()
SCENARIOS_RUN = pytest.StashKey[int]()


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture(params=PROVIDERS)
def scenario(app, monkeypatch, request):
    """A story played for each provider in turn on the module's journal from the state its starts_from names, lines typed to the agent caught and seen back at once; its path is kept for the run's overlay once it ends, and a story fails when a setting it set was never read by the journal after."""
    catch_typed(app, monkeypatch, [])
    reads = SettingReads()
    reads.watch(monkeypatch)
    played = Scenario(app, request.param, reads)
    for mark in request.node.iter_markers(STARTS_FROM_MARK):
        played.starts_from(mark.args[0])
    yield played
    unread = played.settings_never_read()
    assert not unread, f"set by the story but never read by the journal after: {', '.join(unread)}"
    overlays = request.config.stash.setdefault(OVERLAYS, {})
    overlays.setdefault(request.param, PathOverlay()).add(request.node.originalname, played.path)
    request.config.stash[SCENARIOS_RUN] = request.config.stash.get(SCENARIOS_RUN, 0) + 1


def pytest_sessionfinish(session, exitstatus) -> None:
    """Once every scenario of the run has played, their paths are laid over each other per provider: a story reaching nothing of its own, or two walking one path, fail the run with what to do."""
    collected = [item for item in session.items if "scenario" in getattr(item, "fixturenames", ())]
    if not collected or session.config.stash.get(SCENARIOS_RUN, 0) < len(collected) or session.config.option.keyword:
        return
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    failures, warnings = [], []
    for provider, overlay in session.config.stash.get(OVERLAYS, {}).items():
        failures += [f"[{provider}] {line}" for line in overlay.failures()]
        warnings += [f"[{provider}] {line}" for line in overlay.warnings()]
    for line in warnings:
        reporter.write_line(f"scenario paths, drifting together: {line}")
    for line in failures:
        reporter.write_line(f"scenario paths, failed: {line}", red=True)
    if failures:
        session.exitstatus = 1
