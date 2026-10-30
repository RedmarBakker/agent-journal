from pathlib import Path

import pytest

from journal.app import App
from journal.config import Config
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.setting import Setting
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from tests.main_journal import main_journal


def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
    """A journal started on a free port with workers held for the test."""
    patch.setattr(Config, "status_home", property(lambda self: root / "status"))
    patch.setattr(WorkerRunner, "start", lambda self, worker, actor: None)
    app = main_journal(Config(root, port=0))
    app.container.get(SettingRows).save(Setting(environment_id=0, key="features.skills", value=False), Actor.system())
    app.container.get(SettingRows).save(Setting(environment_id=0, key="plugins.hold_window_ms", value=2000), Actor.system())
    app.runtime().start()
    return app
