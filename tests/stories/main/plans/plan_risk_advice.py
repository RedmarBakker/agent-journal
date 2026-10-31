from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan
from tests.stories.fixtures.main.paused_plan import PausedPlan
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(EstimatesOptions.MODE, "report")
def test_a_busy_plan_with_no_history_gets_an_honest_forecast_basis_at_stop(story):
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")

    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "Not enough history yet")
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "no finish date or sprint probability")
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_scope_growth_is_advised_without_rewriting_the_plan(story):
    task = story.tasks.first
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result = story.user_presses(f"/journal/tasks/{task}/size", {"size": 5, "reason": "the owner added the production rollout"})
    result.expect_viewer_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    size = story.user_opens(f"/journal/tasks/{task}/size")
    size.expect_viewer_shows("first_ready_size", 3)
    size.expect_viewer_shows("current_size", 5)

    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.SCOPE_GROWTH, "2 story points")
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.SCOPE_GROWTH, "ask the owner")
    story.expect_task(task, state=TaskState.STARTED, size=5)
    story.expect_plan(story.plans.first, state="started")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(EstimatesOptions.RISK_REPEAT_MINUTES, 1)
@setting(EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS, 2)
def test_a_silent_plan_gets_bounded_advice_at_a_tick(story):
    task = story.tasks.first
    ready = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    ready.expect_command_passed()
    ready.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "Not enough history yet")
    resized = story.user_presses(f"/journal/tasks/{task}/size", {"size": 5, "reason": "the owner added production rollout"})
    resized.expect_viewer_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.time_travel(minutes=2)

    tick = story.clock_ticks(1)
    tick.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "Not enough history yet")
    tick.expect_agent_told_words(story.agents.subject, EstimatesNudges.SCOPE_GROWTH, "2 story points")
    story.expect_task(task, state=TaskState.STARTED, size=5)
    story.expect_plan(story.plans.first, state="started")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PausedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(EstimatesOptions.MODE, "report")
@setting(EstimatesOptions.RISK_REPEAT_MINUTES, 1)
def test_an_owner_paused_plan_stays_paused_when_the_agent_ticks(story):
    story.time_travel(minutes=2)

    tick = story.clock_ticks(1)
    tick.expect_agent_not_told(story.agents.subject, EstimatesNudges.FORECAST_BASIS, n=story.plans.first)
    story.expect_plan(story.plans.first, state="paused")
    story.expect_task(story.tasks.first, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_open_critical_prerequisite_is_advised_without_changing_the_dependency(story):
    prerequisite = story.tasks.first
    second = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development --size 5 --phase 1 --after {prerequisite} --reason 'deployment uses the built artifact'")
    second.expect_command_passed()
    dependent = story.created_number("task")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")

    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.CRITICAL_PREREQUISITE, f"task {dependent}")
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.CRITICAL_PREREQUISITE, f"task {prerequisite}")
    story.expect_task(prerequisite, state=TaskState.STARTED, size=3)
    story.expect_task(dependent, state=TaskState.OPEN, size=5)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(EstimatesOptions.AGING_MINIMUM_OUTCOMES, 1)
def test_a_task_beyond_its_comparable_historical_p85_gets_advice(story):
    historical = story.tasks.first
    second = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development --size 3 --phase 1")
    second.expect_command_passed()
    current = story.created_number("task")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.time_travel(minutes=60)
    result = story.agent_runs(story.agents.subject, f"task complete {historical} --how 'the artifact builds'")
    result.expect_command_passed()
    story.time_travel(minutes=61)
    history = story.user_opens(f"/journal/plans/{story.plans.first}/outcomes")
    history.expect_viewer_passed()
    history.expect_viewer_part_is_truthy(("tasks", 0, "outcomes", 0, "cohort_key"))
    history.expect_viewer_parts_equal(("tasks", 0, "outcomes", 0, "cohort_key"), ("tasks", 1, "outcomes", 0, "cohort_key"))
    history.expect_viewer_part(("tasks", 0, "execution", "active_seconds"), 3600)
    history.expect_viewer_part(("tasks", 1, "execution", "active_seconds"), 3660)

    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.AGING_TASK, f"task {current}")
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.AGING_TASK, "1h 1m")
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.AGING_TASK, "1h 0m")
    story.expect_task(historical, state=TaskState.COMPLETED, size=3)
    story.expect_task(current, state=TaskState.STARTED, size=3)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
