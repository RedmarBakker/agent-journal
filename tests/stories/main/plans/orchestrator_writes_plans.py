from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_WRITES_PLANS, False)
def test_an_orchestrator_the_user_does_not_let_write_plans_is_refused_a_new_plan(story):
    story.agent_runs(story.agents.subject, "plan create another --brief 'the goal'")
    story.expect_command_refused()
    story.expect_command_text("Orchestrator may write plans is off")
    story.expect_stack(story.agents.subject, Orchestrating)
