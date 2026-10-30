from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.subagent_state import SubagentState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_plan_with_subagent import SUBAGENT, StartedPlanWithSubagent


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_started_plan_with_a_task_in_hand_is_told_to_continue_without_helpers(story):
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlanWithSubagent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_running_background_subagent_does_not_hide_the_plans_task_at_a_stop(story):
    story.user_opens("/journal/subagents")
    story.expect_viewer_rows("rows", "state", [SubagentState.ACTIVE])
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlanWithSubagent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_idle_subagent_does_not_hide_the_plans_task_at_a_stop(story):
    story.subagent_ends(SUBAGENT)
    story.user_opens("/journal/subagents")
    story.expect_viewer_rows("rows", "state", [SubagentState.FINISHED])
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_out_on_the_next_task_does_not_hide_the_plans_task_at_a_stop(story):
    worker = story.agent_dispatches_worker(story.agents.subject, "Lady Lovelace", story.tasks.second)
    story.expect_worker(story.agents.workers.get(worker), state=WorkerState.DISPATCHED)
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_idle_worker_does_not_hide_the_plans_task_at_a_stop(story):
    worker = story.agent_dispatches_worker(story.agents.subject, "Lady Lovelace", story.tasks.second)
    story.worker_run_ends_with_its_session(story.agents.workers.get(worker), "the worker ended")
    story.expect_worker(story.agents.workers.get(worker), state=WorkerState.REPORTED)
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
