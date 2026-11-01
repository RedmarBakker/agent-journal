from journal.features.tasks.states.ready import Ready
from journal.features.updates.support.commit_ancestry import CommitAncestry
from journal.features.updates.support.release_source import ReleaseSource
from journal.features.updates.updates_options import UpdatesOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.session_opening import SessionOpening


@story(SessionOpening, subject=AgentRole.MAIN)
def test_a_branch_install_reports_an_ancestry_read_failure(story):
    def ancestry_read_fails(ancestry, head, installed, repository, branch):
        raise OSError("git fetch timed out after 60 seconds")

    story.monkeypatch.setattr(ReleaseSource, "head_commit", lambda source, repository, branch: "c" * 40)
    story.monkeypatch.setattr(CommitAncestry, "is_newer", ancestry_read_fails)
    followed = story.agent_runs(story.agents.subject, "update follow development")
    followed.expect_command_passed()
    followed.expect_command_text("could not be checked")

    result = story.agent_runs(story.agents.subject, "update install")
    result.expect_command_refused()
    result.expect_command_text("could not be checked")
    result.expect_command_text("git fetch timed out after 60 seconds")
    result.expect_command_text_without("nothing newer")
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, subject=AgentRole.MAIN)
@setting(UpdatesOptions.BRANCH, "development")
def test_a_new_branch_head_is_reported_as_available(story):
    story.monkeypatch.setattr(ReleaseSource, "head_commit", lambda source, repository, branch: "d" * 40)
    story.monkeypatch.setattr(CommitAncestry, "is_newer", lambda ancestry, head, installed, repository, branch: True)

    result = story.agent_runs(story.agents.subject, "update check")
    result.expect_command_passed()
    result.expect_command_text("development at ddddddd is out")
    result.expect_command_text("journal update installs it")
    story.expect_stack(story.agents.subject, Ready)
