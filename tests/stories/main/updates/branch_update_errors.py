from journal.features.tasks.states.ready import Ready
from journal.features.updates.support.updater import Updater
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.session_opening import SessionOpening


@story(SessionOpening, subject=AgentRole.MAIN)
def test_a_branch_install_reports_an_ancestry_read_failure(story):
    updating = story.app.container.get(Updater)

    def ancestry_read_fails(head, installed, repository, branch):
        raise OSError("git fetch timed out after 60 seconds")

    story.monkeypatch.setattr(updating.source, "head_commit", lambda repository, branch: "c" * 40)
    story.monkeypatch.setattr(updating.ancestry, "is_newer", ancestry_read_fails)
    followed = story.agent_runs(story.agents.subject, "update follow development")
    followed.expect_command_passed()
    followed.expect_command_text("could not be checked")

    result = story.agent_runs(story.agents.subject, "update install")
    result.expect_command_refused()
    result.expect_command_text("could not be checked")
    result.expect_command_text("git fetch timed out after 60 seconds")
    result.expect_command_text_without("nothing newer")
    story.expect_stack(story.agents.subject, Ready)
