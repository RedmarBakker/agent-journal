from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(UserDraftedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_users_approval_is_told_to_the_agent(story):
    story.user_approves_plan(story.start.plan)
    story.expect_agent_told(PlansNudges.PLAN_APPROVED, n=story.start.plan)
    story.expect_plan(story.start.plan, state=PlanState.APPROVED)
    story.expect_task(story.start.first_task, state=TaskState.OPEN)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agent_cancelling_its_plan_cancels_the_open_tasks_and_frees_the_stack(story):
    story.agent_runs(f"plan cancel {story.start.plan}")
    story.expect_plan(story.start.plan, state=PlanState.CANCELLED)
    story.expect_task(story.start.first_task, state=TaskState.CANCELLED)
    story.expect_task(story.start.second_task, state=TaskState.CANCELLED)
    story.expect_stack(Ready)


@story(PlanApproved, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_the_user_cancelled_and_its_tasks_are_shown_with_the_closed_ones(story):
    story.user_cancels_plan(story.start.plan)
    story.user_opens("/journal/plans?closed=1")
    story.expect_viewer_rows("rows", "state", ["cancelled"])
    story.user_opens(f"/journal/tasks?closed=1&ids={story.start.first_task},{story.start.second_task}")
    story.expect_viewer_rows("rows", "state", ["cancelled", "cancelled"])
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_closed_on_its_card_stays_a_draft_and_the_agent_brings_the_card_back(story):
    plan = story.user_creates_plan("the floors", "the floors are laid")
    story.user_closes_the_plan_card(plan)
    story.expect_plan(plan, is_dismissed=True, state=PlanState.DRAFT)
    story.agent_runs(f"plan card {plan}")
    story.expect_plan(plan, is_dismissed=False)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_cancelled_plan_is_shown_with_its_phases_and_their_tasks(story):
    plan = story.user_creates_plan("release", "ship it")
    story.agent_runs(f"plan phase {plan} build --when built")
    notes, tag, loose = (story.user_adds_plan_task(plan, title) for title in ("write the notes", "tag it", "loose end"))
    story.agent_runs(f"plan todos {plan} 1 {notes} {tag}")
    story.user_cancels_plan(plan)
    story.user_opens(f"/journal/plans?closed=1&ids={plan}")
    story.expect_viewer_part(("rows", 0, "phases", 0, "task_ids"), [notes, tag])
    story.expect_viewer_part(("rows", 0, "unphased_task_ids"), [loose])
    story.expect_stack(Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_cancelled_plan_takes_its_own_open_tasks_and_leaves_its_done_ones_and_those_another_plan_holds(story):
    old, own, finished = story.start.plan, story.start.first_task, story.start.second_task
    story.agent_runs(f"task start {finished}")
    story.agent_runs(f"task complete {finished} --how done")
    new = story.user_creates_plan("new", "b")
    shared = story.user_adds_plan_task(new, "shared")
    story.agent_runs(f"plan phase {old} p --when w")
    story.agent_runs(f"plan todos {old} 1 {shared}")
    story.user_cancels_plan(old)
    story.expect_task(own, state=TaskState.CANCELLED)
    story.expect_task(finished, state=TaskState.COMPLETED)
    story.expect_task(shared, state=TaskState.OPEN)
    story.expect_stack(Ready)


@story(ManualDraftPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_approved_with_a_comment_tells_the_agent_to_read_that_comment(story):
    story.agent_runs(f"plan phase {story.start.plan} Server --when 'it answers'")
    tables = story.agent_adds_plan_task(story.start.plan, "Tables")
    story.agent_runs(f"plan todos {story.start.plan} 1 {tables}")
    story.agent_runs(f"plan ready {story.start.plan}")
    comment = story.user_approves_plan_with_a_comment(story.start.plan, "go, but keep it small")
    story.expect_agent_told(PlansNudges.PLAN_APPROVED_WITH_COMMENT, n=story.start.plan, comment=comment)
    story.expect_stack(Ready)
