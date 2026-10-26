"""The event simulator's runs: not in the default run (pytest collects only test_*.py); run with python3 -m pytest tests/simulation_run.py."""
from pathlib import Path

import pytest

from journal.config import Config
from journal.models.setting import Setting
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from tests.main_journal import main_journal
from tests.replay import Frozen, differences
from tests.replays_run import a_queue_runs_to_merge
from tests.simulation.simulator import Simulator
from tests.test_features import MAIN


@pytest.fixture
def simulated(tmp_path: Path, monkeypatch):
    """One fresh journal under the simulator, started, its skills off and lines delivered at once."""
    monkeypatch.setattr(Config, "status_home", property(lambda self: self.root / "status"))
    app = main_journal(Config(tmp_path / "journal", port=0))
    settings = app.container.get(SettingRows)
    for key, value in (("features.skills", False), ("delivery.batch_seconds", 0), ("workers.testing", "Hand the tests over")):
        settings.save(Setting(environment_id=0, key=key, value=value), Actor.system())
    app.runtime().start()
    with app.container.get(Scope).environment(MAIN):
        yield Simulator(app, monkeypatch)
    app.runtime().stop()


def test_the_simulator_plays_a_queue_to_its_merge_as_the_replay_recorded_it(simulated):
    a_queue_runs_to_merge(simulated.app, simulated, "claude")
    assert differences(Frozen("a_queue_runs_to_merge_claude").record(), simulated.record(), True) == [], "the simulator sees what the frozen replay saw: the same lines typed and nudges said at each step"
