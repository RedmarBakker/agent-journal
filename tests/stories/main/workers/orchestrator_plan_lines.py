from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.UNORDERED_PLAN_TASKS, 2)
def test_a_started_plan_of_open_tasks_none_blocked_is_asked_which_depend_on_which(story):
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_told(story.agents.subject, WorkersNudges.UNLINKED_TASKS, plan=story.plans.first, open=2)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan)


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_blocked_work_that_stands_still_past_the_setting_is_named_to_the_orchestrator(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.invoice} 'waits on the payment provider'")
    story.time_travel(minutes=story.setting(WorkersOptions.STALLED_BLOCK_MINUTES) + 1)
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_told(story.agents.subject, WorkersNudges.UNMOVED_TASKS)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan)


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_the_orchestrators_answer_on_its_priorities_is_kept_on_the_plan_and_quiets_the_line(story):
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_told(story.agents.subject, WorkersNudges.PRIORITIES, plan=story.plans.first)
    story.agent_runs(story.agents.subject, "plan priorities 'task one first: the notes come before the tag'")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    story.expect_command_text("priorities: task one first: the notes come before the tag")
    story.agent_is_quiet_for(story.agents.subject, 20)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.PRIORITIES)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan)
