from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_team_admin_invites_with_a_code_and_lists_its_people_and_devices(story):
    story.user_connects_to_a_team()
    result = story.agent_runs(story.agents.subject, "team invite bob@example.com")
    result.expect_command_text("code=")
    result = story.agent_runs(story.agents.subject, "team people")
    result.expect_command_text("Ada")
    result = story.agent_runs(story.agents.subject, "team devices")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_team_member_is_refused_an_invite_since_only_an_admin_invites(story):
    story.user_is_a_team_member()
    result = story.agent_runs(story.agents.subject, "team invite dan@example.com")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
