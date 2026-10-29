from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.git_status_alias import GitStatusAlias


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_alias_call_runs_a_real_command_which_lifts_a_wait_where_a_journal_command_does_not(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
    story.agent_runs_in_the_shell(story.agents.subject, f"journal {story.aliases.first} -s")
    story.expect_stack(story.agents.subject, Ready)
