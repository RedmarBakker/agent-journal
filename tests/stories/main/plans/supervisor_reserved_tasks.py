from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted
from tests.stories.fixtures.main.solo_plan_agent_task_started import SoloPlanAgentTaskStarted
from tests.stories.fixtures.main.supervisor_reserved_plan import SupervisorReservedPlan


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_a_plan_driver_stays_idle_when_its_only_task_is_reserved_for_supervisor_diagnosis(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    story.agent_stops_plan_seat(agent, story.plans.first)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_state_data(agent, FollowingPlan, task_id=0)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_a_plan_driver_cannot_start_the_reserved_seed_task(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    result = story.agent_in_runs(agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, f"task start {story.tasks.first}")
    result.expect_command_refused()
    result.expect_command_text("reserved for supervisor diagnosis")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_a_plan_driver_cannot_assign_the_reserved_seed_to_a_worker(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    result = story.agent_in_runs(agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, f"worker dispatch 'Ada, diagnostic writer' --task {story.tasks.first} --changes 'the diagnostic' --profile journal-medior --model sonnet")
    result.expect_command_refused()
    result.expect_command_text("reserved for supervisor diagnosis")
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_unblocking_a_reserved_task_does_not_make_it_executable(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    story.user_blocks_task(story.tasks.first, "the smoke is being prepared").expect_viewer_passed()
    story.user_did(f"/journal/tasks/{story.tasks.first}/unblock", {}, "the owner unblocks the reserved seed").expect_viewer_passed()
    story.agent_stops_plan_seat(agent, story.plans.first)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, supervisor_reserved=True)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_a_restarted_plan_driver_keeps_its_reserved_task_out_of_its_hand(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    story.session_starts_in(f"plan-{story.plans.first}", PLAN_AGENT_SESSION, "resume").expect_allowed()
    story.agent_in_runs(agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, "environment overview").expect_command_passed()
    story.agent_stops_plan_seat(agent, story.plans.first)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, supervisor_reserved=True)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_the_owner_can_release_a_reserved_task_for_the_plan_driver(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    story.user_did(f"/journal/tasks/{story.tasks.first}", {"supervisor_reserved": False}, "the owner releases the supervisor reservation").expect_viewer_passed()
    story.agent_in_runs(agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, f"task start {story.tasks.first}").expect_command_passed()
    story.expect_task(story.tasks.first, state=TaskState.STARTED, supervisor_reserved=False)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_an_ordinary_diagnostic_runs_while_the_seed_stays_reserved(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    diagnostic = story.user_adds_plan_task(story.plans.first, "Diagnose the failed smoke check")
    story.agent_stops_plan_seat(agent, story.plans.first)
    story.expect_task(diagnostic, state=TaskState.STARTED, supervisor_reserved=False)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, supervisor_reserved=True)
    story.expect_task_unheld(story.tasks.first)
    story.expect_state_data(agent, FollowingPlan, task_id=diagnostic)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SupervisorReservedPlan, subject=AgentRole.MAIN)
def test_a_supervisor_reservation_must_be_a_boolean(story):
    result = story.user_did(f"/journal/tasks/{story.tasks.first}", {"supervisor_reserved": "yes"}, "the owner sends an invalid reservation")
    result.expect_viewer_refused("true or false")
    story.expect_task(story.tasks.first, supervisor_reserved=True)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(SoloPlanAgentTaskStarted, subject=AgentRole.MAIN)
def test_work_already_in_progress_cannot_be_reserved_for_supervisor_diagnosis(story):
    result = story.user_did(f"/journal/tasks/{story.tasks.first}", {"supervisor_reserved": True}, "the owner tries to reserve started work")
    result.expect_viewer_refused("unstarted, unheld")
    story.expect_task(story.tasks.first, state=TaskState.STARTED, supervisor_reserved=False)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_work_assigned_to_a_worker_cannot_be_reserved_for_supervisor_diagnosis(story):
    agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    story.agent_in_runs(agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, f"worker dispatch 'Ada, diagnostic writer' --task {story.tasks.first} --changes 'the diagnostic' --profile journal-medior --model sonnet").expect_command_passed()
    result = story.user_did(f"/journal/tasks/{story.tasks.first}", {"supervisor_reserved": True}, "the owner tries to reserve assigned work")
    result.expect_viewer_refused("unstarted, unheld")
    story.expect_task(story.tasks.first, delegated=True, supervisor_reserved=False)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
