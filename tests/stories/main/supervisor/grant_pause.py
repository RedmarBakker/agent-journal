from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_gate_closed import SupervisorGrantGateClosed
from tests.stories.fixtures.main.supervisor_grant_paused import SupervisorGrantPaused


def grant_change(story, version: int, kind: str) -> dict:
    return {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": version,
        "change": {"kind": kind},
    }


@story(SupervisorGrantPaused, subject=AgentRole.MAIN)
def test_an_owner_pauses_the_grant_and_a_wake_does_nothing(story):
    wake = story.supervisor_posts("/_supervisor/v1/admit", {
        "protocol_version": 1, "source": "timer", "observation_cursor": None,
        "wakeup_id": "paused-wakeup-1", "kind": "scheduled",
    })
    wake.expect_viewer_refused("supervisor grant is paused")
    action = story.supervisor_posts("/_supervisor/v1/apply", {})
    action.expect_viewer_refused("supervisor grant is paused")
    story.expect_supervisor_grant_state(story.grants.first, paused=True, revoked=False)
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorGrantPaused, subject=AgentRole.MAIN)
def test_an_owner_turns_the_paused_grant_on_and_wakes_resume(story):
    result = story.user_presses("/_supervisor/v1/enrollment/change", grant_change(story, 2, "on"))
    result.expect_viewer_passed()
    result.expect_viewer_part(("grant_version",), 3)
    story.expect_supervisor_grant_state(story.grants.first, paused=False, revoked=False)

    wake = story.supervisor_posts("/_supervisor/v1/admit", {
        "protocol_version": 1, "source": "timer", "observation_cursor": None,
        "wakeup_id": "resumed-wakeup-1", "kind": "scheduled",
    })
    wake.expect_viewer_text("skipped")
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorGrantGateClosed, subject=AgentRole.MAIN)
def test_an_owner_cannot_turn_on_the_grant_while_the_installation_gate_is_closed(story):
    result = story.user_presses("/_supervisor/v1/enrollment/change", grant_change(story, 2, "on"))
    result.expect_viewer_refused("installation gate is closed")
    story.expect_supervisor_grant_state(story.grants.first, paused=True, revoked=False)
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)
    story.expect_stack(story.agents.subject, Ready)


@story(SupervisorGrantPaused, subject=AgentRole.MAIN)
def test_revoking_a_paused_grant_still_ends_it_for_good(story):
    result = story.user_presses("/_supervisor/v1/enrollment/change", grant_change(story, 2, "revoke"))
    result.expect_viewer_passed()
    story.expect_supervisor_grant_state(story.grants.first, paused=True, revoked=True)

    result = story.user_presses("/_supervisor/v1/enrollment/change", grant_change(story, 3, "on"))
    result.expect_viewer_refused("already revoked")
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, story.plans.first)
    story.expect_stack(story.agents.subject, Ready)
