from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_whose_every_remaining_task_is_blocked_blocks_itself_and_opens_with_it(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.second} 'waits on the designer'")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how done")
    story.expect_plan(story.plans.first, state=PlanState.BLOCKED)
    story.expect_agent_told(story.agents.subject, PlansNudges.PLAN_BLOCKED, n=story.plans.first)
    story.agent_runs(story.agents.subject, f"task unblock {story.tasks.second}")
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_agent_told(story.agents.subject, PlansNudges.PLAN_REOPENED, n=story.plans.first)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_blocked_with_no_reason_is_refused(story):
    story.agent_runs(story.agents.subject, f"plan block {story.plans.first}")
    story.expect_command_refused()
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_started_while_its_first_task_waits_on_another_hands_out_the_next(story):
    dependency = story.agent_creates_task(story.agents.subject, "dependency")
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first} --on task:{dependency}")
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.BLOCKED)
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_that_blocks_itself_hands_out_the_next_open_task_and_takes_its_own_up_again_once_it_opens(story):
    outside = story.agent_creates_task(story.agents.subject, "outside work")
    story.agent_runs(story.agents.subject, f"task block {story.tasks.second} 'waits on the designer'")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how done")
    story.expect_plan(story.plans.first, state=PlanState.BLOCKED)
    story.expect_task(outside, state=TaskState.STARTED)
    story.agent_runs(story.agents.subject, f"task unblock {story.tasks.second}")
    story.agent_runs(story.agents.subject, f"task complete {outside} --how done")
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
