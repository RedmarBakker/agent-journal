from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EMAIL, PASSWORD = "ada@example.com", "correct horse battery"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_connects_to_one_team_by_its_password_sees_its_status_logs_in_again_and_disconnects(story):
    team = story.a_team_server_runs()
    result = story.agent_runs(story.agents.subject, f"team connect {team} --email {EMAIL}")
    result.expect_command_text("run this line yourself")
    result = story.agent_runs(story.agents.subject, f"team connect {team} --email {EMAIL} --name Ada --password '{PASSWORD}'")
    result.expect_command_text("as Ada, admin")
    result = story.agent_runs(story.agents.subject, "team status")
    result.expect_command_text(f"team {story.team_addresses['team']}, as Ada (admin)")
    result = story.agent_runs(story.agents.subject, f"team connect {team} --email {EMAIL} --password x")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"team login --email {EMAIL} --password '{PASSWORD}'")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "team disconnect")
    result.expect_command_text("disconnected")
    result = story.agent_runs(story.agents.subject, "team status")
    result.expect_command_text("connected to no team")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_user_connects_to_a_team_and_disconnects_through_the_viewer_without_its_token_shown(story):
    team = story.a_team_server_runs()
    result = story.user_presses("/journal/team/connect", {"url": team, "email": EMAIL, "name": "Ada", "password": PASSWORD})
    result.expect_viewer_shows("connected", True)
    result.expect_viewer_shows("name", "Ada")
    result.expect_viewer_shows("token", "")
    result = story.agent_runs(story.agents.subject, "team status")
    result.expect_command_text(f"team {story.team_addresses['team']}, as Ada (admin)")
    result = story.user_presses("/journal/team/disconnect", {})
    result.expect_viewer_shows("connected", False)
    result = story.agent_runs(story.agents.subject, "team status")
    result.expect_command_text("connected to no team")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_library_no_longer_connects_and_its_refusal_names_journal_team_connect(story):
    team = story.a_team_server_runs()
    result = story.agent_runs(story.agents.subject, f"library connect {team} --email {EMAIL} --name Ada --password '{PASSWORD}'")
    result.expect_command_refused()
    result.expect_command_text("journal team connect")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_team_server_is_claimed_only_with_its_setup_code(story):
    story.a_team_server_runs()
    address = story.team_addresses["team"]
    result = story.agent_runs(story.agents.subject, f"team connect {address} --email {EMAIL} --name Ada --password '{PASSWORD}'")
    result.expect_command_refused()
    result.expect_command_text("claim it with the setup URL in its log")
    result.expect_command_text("/setup?code=<code>")
    result = story.agent_runs(story.agents.subject, f"team connect '{address}/setup?code=guessed' --email {EMAIL} --name Ada --password '{PASSWORD}'")
    result.expect_command_refused()
    result.expect_command_text("claimed only with its setup code")
    story.expect_stack(story.agents.subject, Ready)
