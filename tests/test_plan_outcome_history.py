import pytest

from journal.config import Config
from journal.models.entry import Entry
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.plan_outcome_history import PlanOutcomeHistory
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.task_outcomes import TaskOutcomes
from journal.repositories.task_sizes import TaskSizes
from journal.support.actor import Actor
from journal.support.missing_row import MissingRow
from journal.support.rejection import Rejection
from tests.main_journal import main_journal
from tests.test_features import booted


@pytest.fixture(scope="module")
def boot():
    return booted


def test_history_is_owner_only_and_scoped_to_the_current_environment(app):
    with app.container.get(Scope).environment(1):
        plan, task = planned_task(app, PlanMode.SOLO)
        history = app.container.get(PlanOutcomeHistory)
        with pytest.raises(Rejection, match="only the plan owner"):
            history.read(plan.row_id, Actor.user(2))

    with app.container.get(Scope).environment(2):
        with pytest.raises(MissingRow):
            app.container.get(PlanOutcomeHistory).read(plan.row_id, Actor.user(1))


def test_feature_off_history_keeps_unknown_measurements_in_organization_and_solo_plans(app):
    with app.container.get(Scope).environment(1):
        history = app.container.get(PlanOutcomeHistory)
        organization, task = planned_task(app, PlanMode.ORGANIZATION)
        solo, solo_task = planned_task(app, PlanMode.SOLO)

        organization_data = history.read(organization.row_id, Actor.user(1))
        solo_data = history.read(solo.row_id, Actor.user(1))

        assert organization_data["schema_version"] == "plan-outcome-history-v1"
        assert organization_data["estimates_mode"] == "off"
        assert organization_data["scope"]["plan_mode"] == "organization"
        assert solo_data["scope"]["plan_mode"] == "solo"
        for data, task_id in ((organization_data, task.row_id), (solo_data, solo_task.row_id)):
            row = data["tasks"][0]
            assert row["task_id"] == task_id
            assert row["execution"]["active_seconds"] is None
            assert row["execution"]["execution_status"] is None
            assert row["measurements"]["active_time"] == {"status": "not_measured", "seconds": None}
            assert row["measurements"]["cost"] == {"status": "not_measured", "label": "Not measured", "amount_dollars": None}
            assert row["measurements"]["delivery"]["status"] == "not_evidenced"
            assert row["measurements"]["delivery"]["accepted_at"] is None
            assert row["measurements"]["delivery"]["evidence_time_status"] == "not_measured"
            assert row["data_quality"]["status"] == "incomplete"


def test_history_counts_are_unchanged_after_entry_trim_and_connection_restart(app):
    with app.container.get(Scope).environment(1):
        plan, task = planned_task(app, PlanMode.SOLO)
        outcomes = app.container.get(TaskOutcomes)
        outcomes.record_fact(task.row_id, "task_started", 100, {"source_actor": "user:1"}, Actor.system(), "persisted-start")
        before = app.container.get(PlanOutcomeHistory).read(plan.row_id, Actor.user(1))
        entries = app.container.get(Entries)
        entry = entries.recorded(Entry(entry_type="history_export_test", idempotency="history-export"), Actor.system())
        entries.trim(entry.row_id, 0)

    restarted = main_journal(Config(app.config.root, port=0))
    with restarted.container.get(Scope).environment(1):
        after = restarted.container.get(PlanOutcomeHistory).read(plan.row_id, Actor.user(1))
        assert history_counts(after) == history_counts(before)
        assert after["tasks"][0]["outcomes"][0]["cohort_key"] == before["tasks"][0]["outcomes"][0]["cohort_key"]
        assert restarted.container.get(Entries).is_stored(entry.row_id) is False
    restarted.runtime().stop()


def test_history_marks_legacy_outcomes_without_reliable_timestamps_as_incomplete(app):
    with app.container.get(Scope).environment(1):
        plan, task = planned_task(app, PlanMode.SOLO)
        app.container.get(TaskOutcomes).record_fact(task.row_id, "task_started", 0, {"source_actor": "imported"},
                                                    Actor.system(), "imported-start")

        history = app.container.get(PlanOutcomeHistory).read(plan.row_id, Actor.user(1))

        assert history["tasks"][0]["execution"]["active_seconds"] is None
        assert history["tasks"][0]["outcomes"][0]["occurred_at"] is None
        names = {flag["name"] for flag in history["tasks"][0]["data_quality"]["flags"]}
        assert {"active_time", "outcome_timestamp"} <= names


def planned_task(app, mode: PlanMode):
    owner = Actor.user(1)
    plans = app.container.get(Plans)
    plan = plans.save(Plan(title=f"{mode.value} plan", mode=mode), owner)
    task = app.container.get(TaskSizes).compose(plan, Task(title="unmeasured task", brief="- keep unknown facts explicit"), 5, owner)
    app.container.get(Links).linked(Ref.build(task), Ref.build(plan), PLAN_LINK, owner)
    return plan, task


def history_counts(history: dict) -> tuple[int, int, int, int]:
    return (len(history["sprints"]), len(history["delivery"]["history"]),
            sum(len(task["estimate_history"]["history"]) + len(task["estimate_history"]["proposal_history"]) for task in history["tasks"]),
            sum(len(task["outcomes"]) for task in history["tasks"]))
