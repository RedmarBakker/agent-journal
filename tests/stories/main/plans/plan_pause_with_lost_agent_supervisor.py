import json

from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted
from journal.supervisor_link import SupervisorLink


def plan_agent() -> StoryAgent:
    return StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_plan_pauses_and_starts_again_when_its_agent_supervisor_socket_disappears(story):
    plan = story.plans.first
    plan_environment = story.app.container.get(AgentEnvironments).environments.existing(f"plan-{plan}")
    live = True
    attempted = story.app.config.root / ".plan-agent-stop-attempted"
    inbox = story.app.config.home / "runtime" / "inboxes" / plan_environment.name
    original_stop = SupervisorLink.stop

    def supervisor_runs(_link: SupervisorLink, environment_id: int) -> bool:
        return live if environment_id == plan_environment.row_id else False

    def stop_after_supervisor_disappears(link: SupervisorLink, environment_id: int):
        nonlocal live
        socket_path = inbox.parent / "gone.sock"
        inbox.parent.mkdir(parents=True, exist_ok=True)
        inbox.write_text(json.dumps({"socket": str(socket_path), "protocol": 1}))
        attempted.write_text(f"stop {environment_id}")
        reply = original_stop(link, environment_id)
        live = False
        return reply

    def launch_again(_places: AgentEnvironments, environment, _agent, _repositories=()) -> None:
        nonlocal live
        live = True

    story.monkeypatch.setattr(SupervisorLink, "runs", supervisor_runs)
    story.monkeypatch.setattr(SupervisorLink, "stop", stop_after_supervisor_disappears)
    story.monkeypatch.setattr(AgentEnvironments, "launched", launch_again)
    paused = story.user_pauses_plan(plan)
    paused.expect_viewer_passed()
    story.expect_project_file_is(".plan-agent-stop-attempted", f"stop {plan_environment.row_id}")
    story.expect_no_faults()
    story.expect_plan(plan, state=PlanState.PAUSED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)

    started = story.user_starts_plan(plan)
    started.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, f"plan show {plan}")
    result.expect_command_text(f"Plan agent: environment plan-{plan}, running")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(plan_agent(), LeadingPlan, FollowingPlan)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)

