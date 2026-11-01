from journal.features.health.health_options import HealthOptions
from journal.features.health.support.hook_health_file import FILE_NAME
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SLOW_MACHINE_SECONDS = 8


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_hook_scripts_health_wait_is_written_at_boot_and_again_when_the_user_changes_it(story):
    story.expect_runtime_file(FILE_NAME, f"{HealthOptions.HOOK_HEALTH_SECONDS.default}\n")
    story.user_sets(HealthOptions.HOOK_HEALTH_SECONDS, SLOW_MACHINE_SECONDS)
    story.expect_runtime_file(FILE_NAME, f"{SLOW_MACHINE_SECONDS}\n")
    story.expect_stack(story.agents.subject, Ready)
