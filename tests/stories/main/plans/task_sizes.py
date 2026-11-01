from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan


@setting(EstimatesOptions.SIZE_SCALE, [1, 2, 3, 5, 8, 13])
@story(ManualDraftPlan, subject=AgentRole.MAIN)
def test_a_plan_builder_keeps_initial_size_and_reasoned_revisions_separate(story):
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'the contact page' --brief 'the page shows the address' --size 3")
    result.expect_command_passed()
    task = story.created_number("task")
    result = story.agent_runs(story.agents.subject, f"task size {task} 5 --reason 'the form needs another validation path'")
    result.expect_command_passed()
    result = story.user_presses("/journal/settings", {"estimates": {"size_scale": [1, 2, 5, 8, 13]}})
    result.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, f"task scope-size {task} 8 --reason 'the delivery scope now includes contact preferences'")
    result.expect_command_passed()
    result = story.user_opens(f"/journal/tasks/{task}/size")
    result.expect_viewer_shows("current_size", 8)
    result.expect_viewer_shows("planning_baseline_size", 3)
    result.expect_viewer_rows("history", "change_type", ["planning_baseline", "size_revision", "scope_revision"])
    result.expect_viewer_rows("history", "size", [3, 5, 8])
    result.expect_viewer_rows_have_fields("history", "actor", "recorded_at", "reason", "scale_version")
    result.expect_viewer_parts_differ(("history", 0, "scale_version"), ("history", 2, "scale_version"))
    result.expect_viewer_parts_equal(("history", 0, "scale_version"), ("history", 1, "scale_version"))
    result.expect_viewer_rows("history", "actor", [f"agent:{story.session_of(story.agents.subject)}"] * 3)
    result.expect_viewer_rows("history", "reason", ["plan composition", "the form needs another validation path", "the delivery scope now includes contact preferences"])
    story.expect_task(task, size=8, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@setting(EstimatesOptions.SIZE_SCALE, [1, 2, 3, 5, 8, 13])
@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_solo_plan_agent_can_set_a_task_size_for_its_plan(story):
    result = story.agent_in_runs(
        story.agents.main,
        f"plan-{story.plans.first}",
        PLAN_AGENT_SESSION,
        f"task size {story.tasks.first} 3 --reason 'the work has one implementation path'",
    )
    result.expect_command_passed()
    story.expect_task(story.tasks.first, size=3, state=TaskState.OPEN)
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}/size")
    result.expect_viewer_shows("current_size", 3)
    result.expect_viewer_rows("history", "change_type", ["planning_baseline", "size_revision"])
    result.expect_viewer_rows("history", "actor", ["user:1", f"agent:{PLAN_AGENT_SESSION}"])
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_first_ready_sprint_commitment_and_current_size_remain_distinct(story):
    result = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {"title": "sized page", "brief": "the page has a complete proof", "size": 3})
    result.expect_viewer_passed()
    result.expect_viewer_shows("size", 3)
    task = result.viewer_answer["id"]
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_part(("commitments", 0, "tasks", 2, "size"), 3)
    result.expect_viewer_part_is_truthy(("commitments", 0, "tasks", 2, "size_scale_version"))
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'the page is accepted'")
    story.agent_runs(story.agents.subject, f"plan todos {story.plans.first} 1 {task}")
    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_passed()
    result = story.user_presses(f"/journal/tasks/{task}/size", {"size": 5, "reason": "the owner clarified the remaining scope"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/tasks/{task}/size")
    result.expect_viewer_shows("first_ready_size", 3)
    result.expect_viewer_part_is_truthy(("first_ready_scale_version",))
    result.expect_viewer_shows("sprint_committed_size", 3)
    result.expect_viewer_shows("current_size", 5)
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.first, size=None, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, size=None, state=TaskState.OPEN)
    story.expect_task(task, size=5, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(ManualDraftPlan, subject=AgentRole.MAIN)
def test_unknown_size_is_not_zero_and_invalid_or_generic_writes_leave_it_unknown(story):
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'unestimated page' --brief 'the page displays the address'")
    result.expect_command_passed()
    task = story.created_number("task")
    result = story.agent_runs(story.agents.subject, f"task size {task} 0 --reason 'attempt to use zero'")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"task size {task} 14 --reason 'too much for one task'")
    result.expect_command_refused()
    result = story.user_presses(f"/journal/tasks/{task}", {"size": 3})
    result.expect_viewer_refused("task size")
    result = story.user_presses("/journal/tasks", {"title": "a generic sized task", "size": 3})
    result.expect_viewer_refused("task size")
    result = story.user_opens(f"/journal/tasks/{task}/size")
    result.expect_viewer_shows("current_size", None)
    result.expect_viewer_shows("planning_baseline_size", None)
    result.expect_viewer_rows("history", "change_type", ["planning_baseline"])
    result.expect_viewer_rows("history", "size", [None])
    story.expect_task_count(1)
    story.expect_task(task, size=None, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)
