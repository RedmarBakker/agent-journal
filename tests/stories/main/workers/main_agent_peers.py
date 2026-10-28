from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_main_agent_asking_for_its_peers_is_told_only_a_worker_has_them(story):
    story.agent_runs("worker peers")
    story.expect_command_text("only a worker has peers")
    story.expect_stack(Ready)
