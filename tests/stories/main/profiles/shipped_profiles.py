from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SHIPPED = ProfileFiles.PROFILES[0]


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shipped_profile_changed_on_disk_is_written_back_as_shipped_at_the_next_start(story):
    story.a_shipped_profiles_file_was_changed(SHIPPED.name, "Do whatever you like.")
    story.journal_starts_again()
    result = story.user_opens(f"/journal/profiles/{SHIPPED.name}")
    result.expect_viewer_shows("body", SHIPPED.body.strip("\n"))
    story.expect_stack(story.agents.subject, Ready)
