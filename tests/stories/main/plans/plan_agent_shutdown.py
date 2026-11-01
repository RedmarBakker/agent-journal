from journal.engine.states.ended import Ended
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from journal.support.card_type import CardType
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_handoff_seat import OrganizationPlanHandoffSeat
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted


def plan_agent() -> StoryAgent:
    return StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)


def dispatch_worker(story, agent: StoryAgent, task: int) -> int:
    result = story.agent_in_runs(
        agent,
        f"plan-{story.plans.first}",
        PLAN_AGENT_SESSION,
        f"worker dispatch 'Lady Lovelace' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'",
    )
    result.expect_command_passed()
    return story.created_number("worker")


def wait_for_worker(story, agent: StoryAgent, worker: int) -> None:
    result = story.agent_in_runs(
        agent, f"plan-{story.plans.first}", PLAN_AGENT_SESSION, f"worker wait {worker}",
    )
    result.expect_command_passed()


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_cancelling_a_plan_ends_its_plan_agent_waiting_on_a_worker(story):
    agent = plan_agent()
    task = story.tasks.first
    worker = dispatch_worker(story, agent, task)
    wait_for_worker(story, agent, worker)
    story.clock_ticks(300)

    cancelled = story.user_cancels_plan(story.plans.first)
    story.settle()
    cancelled.expect_agent_told_nothing(agent)
    story.expect_worker_in(f"plan-{story.plans.first}", worker, state=WorkerState.RELEASED)
    story.expect_stack(agent, LeadingPlan, Ended)

    quiet = story.agent_is_quiet_for(agent, 6)
    quiet.expect_agent_told_nothing(agent)
    story.expect_chat_marks(CardType.FAULTS)
    story.expect_stack(agent, LeadingPlan, Ended)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_releasing_a_worker_ends_the_plan_agents_wait_on_it(story):
    agent = plan_agent()
    task_created = story.agent_in_runs(
        agent,
        f"plan-{story.plans.first}",
        PLAN_AGENT_SESSION,
        "task create 'separate work' --brief 'Finish the separate work'",
    )
    task_created.expect_command_passed()
    task = story.created_number("task")
    worker = dispatch_worker(story, agent, task)
    wait_for_worker(story, agent, worker)

    cancelled = story.user_presses_in(
        f"plan-{story.plans.first}",
        f"/journal/tasks/{task}/cancel",
        {"why": "the task is no longer needed"},
    )
    cancelled.expect_viewer_passed()
    story.expect_worker_in(f"plan-{story.plans.first}", worker, state=WorkerState.RELEASED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_stack(agent, LeadingPlan, FollowingPlan)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_finishing_a_plan_ends_its_plan_agent(story):
    agent = plan_agent()
    result = story.agent_in_runs(
        agent,
        f"plan-{story.plans.first}",
        PLAN_AGENT_SESSION,
        f"task complete {story.tasks.first} --how done",
    )
    result.expect_command_passed()
    story.expect_stack(agent, LeadingPlan, Ended)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)


@story(OrganizationPlanHandoffSeat, subject=AgentRole.MAIN)
def test_cancelling_an_organization_plan_stops_its_plan_seat(story):
    plan = story.plans.first
    cancelled = story.user_cancels_plan(plan)
    cancelled.expect_agent_told_nothing(story.agents.main)
    story.expect_plan(plan, state=PlanState.CANCELLED)
    story.expect_openrig_seat_stopped("plan")
    story.expect_stack(story.agents.main, LeadingPlan, Ended)
