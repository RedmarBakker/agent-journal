from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_replacement_owner import SupervisorGrantReplacementOwner


@story(SupervisorGrantReplacementOwner, subject=AgentRole.MAIN)
def test_an_owner_replaces_a_grant_and_a_stale_revision_is_refused(story):
    replacement = {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": 1,
        "change": {"kind": "replace", "enrollment": story.grants.replacement},
    }
    result = story.user_presses("/_supervisor/v1/enrollment/change", replacement)
    result.expect_viewer_passed()
    result.expect_viewer_part(("grant_version",), 2)

    result = story.user_presses("/_supervisor/v1/enrollment/change", replacement)
    result.expect_viewer_refused("grant changed")
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)
    story.expect_stack(story.agents.subject, Ready)
