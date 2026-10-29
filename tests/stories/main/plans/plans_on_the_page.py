from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_pages_start_of_an_unapproved_plan_is_refused(story):
    plan = story.user_creates_plan("p", "b")
    story.user_presses(f"/journal/plans/{plan}/start", {})
    story.expect_viewer_refused("")
    story.expect_plan(plan, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_pages_start_takes_the_first_task_in_hand_and_its_pause_postpones_it_with_the_plan(story):
    story.user_presses(f"/journal/plans/{story.fixture.plan}/start", {})
    story.expect_viewer_shows("state", "started")
    story.expect_task(story.fixture.first_task, state=TaskState.STARTED)
    story.expect_task(story.fixture.second_task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
    story.user_pauses_plan(story.fixture.plan)
    story.expect_task(story.fixture.first_task, state=TaskState.PAUSED)
    story.expect_stack(story.agents.subject, Ready)


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_started_plans_phase_shown_moves_on_once_its_tasks_are_done(story):
    story.user_opens(f"/journal/plans/{story.fixture.plan}")
    story.expect_viewer_shows("current_phase", 1)
    story.agent_runs(story.agents.subject, f"task complete {story.fixture.first_phase_task} --how 'the grid stands'")
    story.user_opens(f"/journal/plans/{story.fixture.plan}")
    story.expect_viewer_shows("current_phase", 2)
    story.expect_task(story.fixture.second_phase_task, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_plans_list_carries_counts_only_while_a_plan_read_by_number_comes_whole(story):
    plan, first, second = story.fixture.plan, story.fixture.first_task, story.fixture.second_task
    story.agent_runs(story.agents.subject, f"plan phase {plan} one --when w")
    story.user_opens("/journal/plans?limit=50")
    story.expect_viewer_rows("rows", "task_count", [2])
    story.expect_viewer_rows("rows", "phase_count", [1])
    story.expect_viewer_rows_without("rows", "phases")
    story.expect_viewer_rows_without("rows", "task_ids")
    story.expect_viewer_rows_without("rows", "reviews")
    story.user_opens(f"/journal/plans?ids={plan}")
    story.expect_viewer_part(("rows", 0, "task_ids"), [first, second])
    story.expect_viewer_part(("rows", 0, "phases", 0, "title"), "one")
    story.expect_stack(story.agents.subject, Ready)
