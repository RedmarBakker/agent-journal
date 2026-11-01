from dataclasses import asdict

from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from journal.support.process_usage import ProcessUsage
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MAIN_USAGE = ProcessUsage(34.4, 1_288_490_188)
AGENT_PROCESSES = ("environments", 0, "agent", "processes")


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_environments_agent_carries_what_its_processes_take_once_the_machine_is_sampled(story):
    result = story.user_opens("/journal/summary")
    result.expect_viewer_part(AGENT_PROCESSES, None)
    story.agent_processes_sampled(story.agents.subject, MAIN_USAGE)
    result = story.user_opens("/journal/summary")
    result.expect_viewer_part(AGENT_PROCESSES, asdict(MAIN_USAGE))
    story.expect_stack(story.agents.subject, Ready)
