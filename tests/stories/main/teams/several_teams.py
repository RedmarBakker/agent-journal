from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.two_teams_connected import FIRST, SECOND, TwoTeamsConnected
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_connecting_a_second_team_keeps_the_first_connected(story):
    result = story.user_adds_a_team(FIRST)
    result.expect_viewer_shows("team", FIRST)
    result = story.user_adds_a_team(SECOND)
    result.expect_viewer_shows("team", SECOND)
    result = story.user_opens(f"/journal/team?team={FIRST}")
    result.expect_viewer_shows("connected", True)
    result.expect_viewer_shows("team", FIRST)
    story.expect_stack(story.agents.subject, Ready)


@story(TwoTeamsConnected, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_team_page_route_lists_both_teams_with_the_role_and_people_of_each(story):
    result = story.user_opens("/journal/teams")
    result.expect_viewer_rows("teams", "team", [FIRST, SECOND])
    result.expect_viewer_rows("teams", "role", ["admin", "admin"])
    result.expect_viewer_rows("teams", "people", [1, 1])
    story.expect_stack(story.agents.subject, Ready)


@story(TwoTeamsConnected, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_disconnecting_one_team_leaves_the_other_with_its_people_devices_invites_and_items(story):
    result = story.user_presses("/journal/team/disconnect", {"team": FIRST})
    result.expect_viewer_shows("connected", False)
    result = story.user_opens("/journal/teams")
    result.expect_viewer_rows("teams", "team", [SECOND])
    result = story.user_opens(f"/journal/team/people?team={SECOND}")
    result.expect_viewer_rows("people", "name", ["Ada"])
    result = story.user_opens(f"/journal/team/devices?team={SECOND}")
    result.expect_viewer_count("devices", 1)
    result = story.user_presses("/journal/team/invite", {"email": "bob@example.com", "team": SECOND})
    result.expect_viewer_text(story.team_addresses[SECOND])
    result = story.user_opens(f"/journal/library/items?team={SECOND}")
    result.expect_viewer_part(("items",), [])
    story.expect_stack(story.agents.subject, Ready)


@story(TwoTeamsConnected, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_item_published_to_one_team_never_shows_under_the_other(story):
    story.user_types("sequence create 'Night Run' --steps go")
    sequence = story.created_number("sequence")
    result = story.user_types(f"library publish sequence {sequence} --team {FIRST}")
    result.expect_command_passed()
    result = story.user_opens(f"/journal/library/items?team={FIRST}")
    result.expect_viewer_part(("items", 0, "item", "name"), "night-run")
    result = story.user_opens(f"/journal/library/items?team={SECOND}")
    result.expect_viewer_part(("items",), [])
    story.expect_stack(story.agents.subject, Ready)


@story(TwoTeamsConnected, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_library_command_with_two_teams_and_no_team_named_is_refused_naming_the_teams_and_the_option(story):
    result = story.user_types("library list")
    result.expect_command_refused()
    result.expect_command_text("--team")
    result.expect_command_text(FIRST)
    result.expect_command_text(SECOND)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_library_command_with_one_team_needs_no_team_named(story):
    story.user_adds_a_team(FIRST)
    result = story.user_types("library list")
    result.expect_command_text("no items in the library")
    story.expect_stack(story.agents.subject, Ready)


@story(TwoTeamsConnected, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_library_command_naming_an_unknown_team_is_refused_with_that_name(story):
    result = story.user_types("library list --team nowhere")
    result.expect_command_refused()
    result.expect_command_text("nowhere")
    story.expect_stack(story.agents.subject, Ready)
