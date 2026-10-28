from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

RULE = "Always name the model"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_rule_the_user_made_binds_the_whole_project_and_is_read_in_every_environment(story):
    other = story.another_environment("other")
    story.user_types(f"rule create '{RULE}' --reason 'every dispatch names it'")
    story.session_starts_in(other, "s-other")
    story.agent_in_runs(other, "s-other", "rule list")
    story.expect_command_text(RULE)
    story.expect_stack(Ready)
