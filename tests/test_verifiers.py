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


def test_a_verdict_is_answered_and_kept_and_the_verifiers_process_is_left_to_end_its_turn(app: App):
    report = dismissed(app, "./scripts/test.sh", "the test containers were only booting")
    [verifier] = judging(app, report)
    answer = app.console().run(["verdict", "no", "the run printed a count of tests the card never showed"], Caller.verifier("main", verifier.id, verifier.session, "claude"))
    app.runtime().deferred.drain()
    assert answer.code == 0 and "verdict no on reader report" in answer.text, answer.error
    kept, judged = app.container.get(ReaderReports).find(report.id), app.container.get(Verifiers).find(verifier.id)
    assert kept.is_refuted and judged.state == VerifierState.JUDGED and judged.pid == os.getpid(), "the verdict is kept and the process still running is not stopped under its reply"


def test_a_judged_verifier_takes_the_next_judgement_only_once_its_process_has_ended(app: App):
    app.container.get(SettingRows).save(Setting(environment_id=0, key="workers.verifiers_most", value=1), Actor.system())
    first = dismissed(app, "./scripts/test.sh", "the test containers were only booting")
    [verifier] = judging(app, first)
    second = dismissed(app, "ssh-query", "card numbers, not a count")
    assert not judging(app, second), "past the most verifiers the second judgement waits"
    app.console().run(["verdict", "yes", "the run printed nothing for the reader to show"], Caller.verifier("main", verifier.id, verifier.session, "claude"))
    app.runtime().deferred.drain()
    assert not judging(app, second), "the verifier still ending its turn is not sent the next judgement"
    app.container.get(VerifierRunner).ended(app.container.get(Verifiers).find(verifier.id))
    app.runtime().deferred.drain()
    assert [row.id for row in judging(app, second)] == [verifier.id], "once its process ended, the same verifier takes the waiting judgement in its own session"


def test_a_waiting_judgement_whose_report_was_judged_meanwhile_is_never_sent(app: App):
    app.container.get(SettingRows).save(Setting(environment_id=0, key="workers.verifiers_most", value=1), Actor.system())
    first = dismissed(app, "./scripts/test.sh", "the test containers were only booting")
    [verifier] = judging(app, first)
    second = dismissed(app, "ssh-query", "card numbers, not a count")
    reports = app.container.get(ReaderReports)
    reports.save(reports.find(second.id).cleared(reports.find(second.id).created_at), Actor.system())
    app.console().run(["verdict", "yes", "sound"], Caller.verifier("main", verifier.id, verifier.session, "claude"))
    app.container.get(VerifierRunner).ended(app.container.get(Verifiers).find(verifier.id))
    app.runtime().deferred.drain()
    assert not judging(app, second) and len(app.container.get(Verifiers).scoped()) == 1, "a report no longer waiting for a verdict sends no verifier"
