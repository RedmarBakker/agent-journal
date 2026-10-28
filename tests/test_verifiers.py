"""A verifier's verdict reaches it and is kept, and a verifier is reused, on what a consumer project's journal showed: 22 verifiers whose every verdict command was answered "no dismissal waiting", because the verdict that went through stopped the verifier's process before the reply reached it, and old judgements kept in the queue were sent again after they were judged."""

import os

import pytest

from journal.app import App
from journal.features.verification.support.verifier_dispatch import VERIFIES
from journal.features.verification.support.verifier_runner import VerifierRunner
from journal.models.reader_report import ReaderReport
from journal.models.setting import Setting
from journal.models.support.ref import Ref
from journal.models.verifier_state import VerifierState
from journal.repositories.links import Links
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.test_features import booted, hook

AGENT = Caller.agent("main", "s1", "claude")
MAIN = 1
FINDINGS = ("the run took 362 seconds and its card showed no progress",)


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App, monkeypatch):
    started = []
    monkeypatch.setattr(VerifierRunner, "start", lambda self, verifier, resume="": started.append(verifier.id) or self.rows.save(verifier.with_(session=resume or f"v-{verifier.id}", pid=os.getpid()), Actor.system()))
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def dismissed(app: App, command: str, why: str) -> ReaderReport:
    report = app.container.get(ReaderReports).save(ReaderReport(environment_id=MAIN, reader="test-sh", output=1, command=command, session="s1", findings=FINDINGS, fixes=("give it --progress",)), Actor.system())
    app.console().run(["reader", "report", str(report.id)], AGENT)
    output = app.console().run(["reader", "dismiss", str(report.id), "--why", why], AGENT)
    assert output.code == 0, output.error
    app.runtime().deferred.drain()
    return report


def judging(app: App, report: ReaderReport):
    links = app.container.get(Links)
    return [verifier for verifier in app.container.get(Verifiers).scoped() if Ref.build(report) in links.targets(verifier, VERIFIES)]






