from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantMutationAttempt


@story(SupervisorGrantMutationAttempt, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_cannot_enroll_its_own_grant(story):
    result = story.supervisor_calls_grant_route(
        story.agents.subject, "/_supervisor/v1/enrollment", story.supervisor_replacement,
    )
    result.expect_viewer_refused("cannot use owner management routes")
    story.expect_supervisor_grant_mutation_wrote_nothing()
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantMutationAttempt, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_cannot_change_its_own_grant(story):
    body = {
        "protocol_version": 1, "grant_id": story.grants.first, "expected_grant_version": 2,
        "change": {"kind": "off"},
    }
    result = story.supervisor_calls_grant_route(story.agents.subject, "/_supervisor/v1/enrollment/change", body)
    result.expect_viewer_refused("cannot use owner management routes")
    story.expect_supervisor_grant_mutation_wrote_nothing()
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantMutationAttempt, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_cannot_revoke_its_own_grant(story):
    body = {
        "protocol_version": 1, "grant_id": story.grants.first, "expected_grant_version": 2,
        "change": {"kind": "revoke"},
    }
    result = story.supervisor_calls_grant_route(story.agents.subject, "/_supervisor/v1/enrollment/change", body)
    result.expect_viewer_refused("cannot use owner management routes")
    story.expect_supervisor_grant_mutation_wrote_nothing()
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantMutationAttempt, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_cannot_edit_its_own_grant(story):
    body = {
        "protocol_version": 1, "grant_id": story.grants.first, "expected_grant_version": 2,
        "change": {"kind": "replace", "enrollment": story.supervisor_replacement},
    }
    result = story.supervisor_calls_grant_route(story.agents.subject, "/_supervisor/v1/enrollment/change", body)
    result.expect_viewer_refused("cannot use owner management routes")
    story.expect_supervisor_grant_mutation_wrote_nothing()
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    story.expect_stack(story.agents.subject)
