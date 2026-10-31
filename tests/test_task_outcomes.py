import pytest

from journal.config import Config
from journal.events.rows.worker_spent import WorkerSpent
from journal.events.agent.wait_cleared import WaitCleared
from journal.events.agent.wait_request import WaitRequest
from journal.events.rows.worker_mention import WorkerMention
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.models.model_tier import ModelTier
from journal.repositories.entries import Entries
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.sprints import Sprints
from journal.repositories.task_outcomes import OUTCOME_DOMAIN_LINK, OUTCOME_PLAN_LINK, OUTCOME_TASK_LINK, TaskOutcomes
from journal.repositories.task_sizes import TaskSizes
from journal.repositories.tasks import CURRENT_TASK_LINK, Tasks
from journal.repositories.agents import Agents
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from tests.main_journal import main_journal
from tests.test_features import booted


@pytest.fixture(scope="module")
def boot():
    return booted


def test_replayed_and_out_of_order_outcomes_keep_one_fact_and_union_overlapping_waits(app):
    with app.container.get(Scope).environment(1):
        plan, task, outcomes = planned_task(app)
        owner = Actor.user(1)
        outcomes.record_fact(task.row_id, "task_started", 500, {"prior_state": "paused"}, owner, "resume")
        outcomes.record_row_event(WorkerReviewed(environment_id=1, time=480, worker=WorkerMention(7, "Lady Lovelace", None),
                                                 task=task.row_id, reviewer=3, reviewer_session="reviewer-session",
                                                 report="1 short: the deployment proof is missing"))
        pause = outcomes.record_fact(task.row_id, "task_paused", 400, {"outcome": "paused"}, owner, "pause")
        outcomes.record_fact(task.row_id, "task_started", 300, {}, owner, "start")
        outcomes.record_fact(task.row_id, "task_wait_ended", 450, {}, owner, "wait-ended")
        outcomes.record_fact(task.row_id, "review_started", 420, {"worker_id": 7}, owner, "review-start")
        replay = outcomes.record_fact(task.row_id, "task_paused", 400, {"outcome": "paused"}, owner, "pause")

        summary = outcomes.summary(task.row_id, as_of=600)

        assert replay.row_id == pause.row_id
        assert [row.kind for row in outcomes.facts(task.row_id)] == ["task_started", "task_paused", "review_started", "task_wait_ended", "review_sent_back", "task_started"]
        assert summary["task_wait_seconds"] == 50
        assert summary["review_wait_seconds"] == 60
        assert summary["waiting_seconds"] == 80
        assert summary["execution_status"] == "in_progress"
        assert summary["right_censored"] is True
        with pytest.raises(Rejection, match="task outcome history is immutable"):
            outcomes.save(pause.with_(kind="rewritten"), owner)
        with pytest.raises(Rejection, match="task outcome history is immutable"):
            outcomes.delete(pause, owner)


def test_long_user_usage_and_deployment_waits_remain_open_with_resource_cost_facts(app):
    with app.container.get(Scope).environment(1):
        plan, task, outcomes = planned_task(app)
        owner = Actor.user(1)
        outcomes.record_fact(task.row_id, "task_started", 100, {}, owner, "start")
        outcomes.record_fact(task.row_id, "user_wait_started", 101, {"focus": "production approval"}, owner, "user-wait",
                             agent_session="owner-session")
        outcomes.record_fact(task.row_id, "usage_limited", 200, {"worker_id": 4, "resumes_at": 500}, owner, "usage-limit")
        outcomes.record_fact(task.row_id, "worker_work_merged", 300, {"worker_id": 4}, owner, "merge")
        task = app.container.get(Tasks).save(task.with_(state=TaskState.STARTED, delegated=True), owner)
        worker = app.container.get(Workers).save(Worker(name="Lady Lovelace", model="test-model"), Actor.system())
        app.container.get(Links).linked(Ref.build(worker), Ref.build(task), CURRENT_TASK_LINK, Actor.system())
        spend_event = WorkerSpent(environment_id=1, time=250, worker=worker.mention(), model="test-model", tier=ModelTier.GENERAL,
                                  profile_tier=ModelTier.GENERAL, before_dollars=0.0, cost_dollars=3.5)
        spend = outcomes.record_row_event(spend_event)
        outcomes.record_row_event(spend_event)

        summary = outcomes.summary(task.row_id, as_of=2000)

        open_waits = [row for row in summary["wait_intervals"] if row["end"] is None]
        assert {row["kind"] for row in open_waits} == {"user_wait", "usage_limit", "delivery_wait"}
        assert summary["user_wait_seconds"] == 1899
        assert summary["usage_wait_seconds"] == 1800
        assert summary["delivery_wait_seconds"] == 1700
        assert summary["waiting_seconds"] == 1899
        assert summary["cost_dollars"] == 3.5
        assert summary["worker_costs"][0]["model"] == "test-model"
        assert summary["worker_costs"][0]["tier"] == "general"
        assert "capacity_assumptions" in summary["missing_measurements"]
        assert summary["right_censored"] is True
        assert outcomes.find(spend.row_id).details["missing_measurements"]


def test_only_a_worker_ready_after_a_usage_limit_records_a_usage_resumption(app):
    with app.container.get(Scope).environment(1):
        _plan, task, outcomes = planned_task(app, size=3)
        actor = Actor.system()
        worker = app.container.get(Workers).save(Worker(name="Lady Lovelace", model="test-model"), actor)
        app.container.get(Links).linked(Ref.build(worker), Ref.build(task), CURRENT_TASK_LINK, actor)
        dispatched = worker.dispatched(10)
        ordinary_ready = dispatched.ready(20).events[-1]

        assert ordinary_ready.prior_state == WorkerState.DISPATCHED.value
        assert outcomes.record_row_event(ordinary_ready) is None

        limited = dispatched.limited(30, 50, "the provider's usage limit")
        limited_fact = outcomes.record_row_event(limited.events[-1])
        resumed = limited.ready(40).events[-1]
        resumed_fact = outcomes.record_row_event(resumed)

        assert resumed.prior_state == WorkerState.LIMITED.value
        assert limited_fact.kind == "usage_limited"
        assert resumed_fact.kind == "usage_resumed"
        assert [row.kind for row in outcomes.facts(task.row_id)] == ["usage_limited", "usage_resumed"]
        assert outcomes.summary(task.row_id, as_of=60)["usage_wait_seconds"] == 10


def test_agent_user_wait_events_close_the_interval_on_the_task_it_holds(app):
    with app.container.get(Scope).environment(1):
        plan, task, outcomes = planned_task(app)
        actor = Actor.system()
        agent = app.container.get(Agents).save(Agent(environment_id=1, session="owner-session", provider="claude"), actor)
        task = app.container.get(Tasks).save(task.with_(state=TaskState.STARTED), actor)
        app.container.get(Links).linked(Ref.build(agent), Ref.build(task), CURRENT_TASK_LINK, actor)

        outcomes.record_wait_request(WaitRequest(agent=agent, session=agent.session, environment_id=1, time=100,
                                                  focus="production approval", end_refs="question:17"))
        outcomes.record_wait_cleared(WaitCleared(agent=agent, session=agent.session, environment_id=1, time=200))

        summary = outcomes.summary(task.row_id, as_of=300)

        assert summary["user_wait_seconds"] == 100
        assert summary["waiting_seconds"] == 100
        assert summary["wait_intervals"][0]["start"] == 100
        assert summary["wait_intervals"][0]["end"] == 200


def test_delivery_corrections_keep_generations_and_credit_committed_size_once(app):
    with app.container.get(Scope).environment(1):
        plan, task, outcomes = planned_task(app, size=5)
        owner, sprints = Actor.user(1), app.container.get(Sprints)
        domains = app.container.get(DomainRows)
        domains.task_tied(task, "development", owner)
        sprint = sprints.create("2026-10-30", "UTC", owner)
        sprints.assign(sprint.row_id, plan.row_id, "", owner)
        sprints.start(sprint.row_id, owner)
        outcomes.record_fact(task.row_id, "task_completed", 100, {}, owner, "completed-1")
        outcomes.record_fact(task.row_id, "task_reopened", 200, {"reason": "the accepted delivery was corrected"}, owner, "reopened-task")
        outcomes.record_fact(task.row_id, "task_completed", 300, {}, owner, "completed-2")
        outcomes.record_fact(task.row_id, "delivery_accepted", 400, {"generation": 1}, owner, "delivery-1", plan.row_id,
                             delivery_generation=1)
        outcomes.record_fact(task.row_id, "delivery_reopened", 500, {"generation": 2}, owner, "delivery-reopen", plan.row_id,
                             delivery_generation=2)
        outcomes.record_fact(task.row_id, "delivery_corrected", 600, {"generation": 3}, owner, "delivery-3", plan.row_id,
                             delivery_generation=3)

        summary = outcomes.summary(task.row_id, as_of=700)

        assert summary["execution_status"] == "completed"
        assert summary["delivery_generations"] == [1, 2, 3]
        assert summary["scope_added"] is False
        assert summary["planned_size"] == 5
        assert summary["credited_points"] == 5
        links = app.container.get(Links)
        outcome_ids = {row.row_id for row in outcomes.facts(task.row_id)}
        assert {ref.id for ref in links.targets(plan, OUTCOME_PLAN_LINK)} == outcome_ids
        domain = domains.named("development", owner)
        assert {ref.id for ref in links.targets(domain, OUTCOME_DOMAIN_LINK)} == outcome_ids


def test_outcomes_survive_entry_trimming_and_a_new_database_connection(app):
    with app.container.get(Scope).environment(1):
        plan, task, outcomes = planned_task(app)
        outcome = outcomes.record_fact(task.row_id, "task_started", 100, {}, Actor.system(), "persistent-start")
        entries = app.container.get(Entries)
        entry = entries.recorded(Entry(entry_type="outcome_test", idempotency="outcome-test"), Actor.system())
        entries.trim(entry.row_id, 0)
        assert not entries.is_stored(entry.row_id)

    restarted = main_journal(Config(app.config.root, port=0))
    with restarted.container.get(Scope).environment(1):
        facts = restarted.container.get(TaskOutcomes).facts(task.row_id)
        assert [(row.row_id, row.kind) for row in facts] == [(outcome.row_id, "task_started")]
        assert restarted.container.get(Links).targets(restarted.container.get(Tasks).find(task.row_id), OUTCOME_TASK_LINK)
    restarted.runtime().stop()


def planned_task(app, size=None):
    owner = Actor.user(1)
    plans, tasks, links = app.container.get(Plans), app.container.get(Tasks), app.container.get(Links)
    plan = plans.save(Plan(title="the release"), owner)
    task = app.container.get(TaskSizes).compose(plan, Task(title="deploy the release", brief="- prove the deployment"), size, owner) if size is not None else tasks.save(Task(title="deploy the release", brief="- prove the deployment"), owner)
    links.linked(Ref.build(task), Ref.build(plan), PLAN_LINK, owner)
    return plan, task, app.container.get(TaskOutcomes)
