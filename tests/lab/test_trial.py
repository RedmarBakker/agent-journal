import shlex

import pytest

from journal.support.option import AGENT, USER, Option
from tests.lab.finding_task import FindingTask
from tests.lab.trial_setting import TrialSetting


def trial_option(*, setter=USER, default=False, option_type="switch"):
    return Option("plans.trial_route", "Trial route", "Route trial", default, option_type=option_type, setter=setter)


def test_trial_setting_builds_pinned_designs_with_the_owner_set_switch_off_by_default():
    setting = TrialSetting(trial_option(), "Product owner")

    baseline, candidate = setting.designs("A", "B", {"plans.test_commands": "pytest"})

    assert dict(baseline.settings) == {"plans.test_commands": "pytest", "plans.trial_route": False}
    assert dict(candidate.settings) == {"plans.test_commands": "pytest", "plans.trial_route": True}
    assert baseline.settings_digest != candidate.settings_digest
    assert setting.option.default is False
    assert setting.manifest() == {
        "key": "plans.trial_route",
        "owner": "Product owner",
        "default": False,
        "candidate": True,
    }


def test_trial_setting_rejects_agent_controlled_switches():
    with pytest.raises(ValueError, match="user-controlled"):
        TrialSetting(trial_option(setter=AGENT), "Product owner")


def test_trial_setting_rejects_a_switch_that_is_on_by_default():
    with pytest.raises(ValueError, match="default to off"):
        TrialSetting(trial_option(default=True), "Product owner")


def test_trial_setting_rejects_non_switch_options():
    with pytest.raises(ValueError, match="switch"):
        TrialSetting(trial_option(option_type="choice"), "Product owner")


def test_trial_setting_does_not_replace_a_common_design_value():
    setting = TrialSetting(trial_option(), "Product owner")

    with pytest.raises(ValueError, match="common settings"):
        setting.designs("A", "B", {"plans.trial_route": False})


def test_finding_task_command_carries_report_metric_scenarios_and_replay_traces():
    setting = TrialSetting(trial_option(), "Product owner")
    task = FindingTask(
        finding_id="F-17",
        summary="Domain routing improved handoff traceability",
        report_id=22,
        metric_id="handoff_traceability",
        metric_version="metric-schema-v3",
        scenario_ids=("fleet_operator/tracker_outage", "law_firm/court_filing_deadline"),
        trace_refs=("$LAB_HOME/batches/b1/runs/r1/trace.json",),
        setting=setting,
    )

    command = shlex.split(task.journal_command)

    assert command[:3] == ["journal", "task", "create"]
    assert command[3] == task.title
    assert command[4:6] == ["--report", "22"]
    assert command[6] == "--brief"
    assert command[7] == task.brief
    for reference in (
        "report 22", "handoff_traceability", "metric-schema-v3", "fleet_operator/tracker_outage",
        "law_firm/court_filing_deadline", "$LAB_HOME/batches/b1/runs/r1/trace.json",
        "plans.trial_route", "Product owner", "default off", "doc 10 section 19", "both paths",
        "keep_eligible", "switch removal", "inconclusive", "NOTES.md",
    ):
        assert reference in task.brief


def test_finding_task_requires_replayable_evidence_and_a_report():
    setting = TrialSetting(trial_option(), "Product owner")

    with pytest.raises(ValueError, match="report ID"):
        FindingTask("F-18", "Try a route", 0, "handoff_traceability", "v1", ("fleet/outage",), ("trace.json",), setting)
    with pytest.raises(ValueError, match="scenario IDs"):
        FindingTask("F-18", "Try a route", 22, "handoff_traceability", "v1", (), ("trace.json",), setting)
    with pytest.raises(ValueError, match="trace references"):
        FindingTask("F-18", "Try a route", 22, "handoff_traceability", "v1", ("fleet/outage",), (), setting)
