from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner


@story(SupervisorGrantOwner, subject=AgentRole.MAIN)
def test_an_owner_reads_and_updates_the_version_two_grant_without_losing_its_revision(story):
    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    result.expect_viewer_part(("grant_version",), 1)
    result.expect_viewer_part(("grant", "watched_plans"), [story.plans.first])
    result.expect_viewer_count("areas", 13)

    grant = story.viewer_answer["grant"]
    result = story.user_presses_in(story.supervisor_owner_environment, "/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": 1,
        "change": {"kind": "configure", "grant": {
            **grant,
            "wake_interval_minutes": 30,
            "capabilities": {**grant["capabilities"], "plan approve": {"on": True, "mode": "act"}},
        }},
    })
    result.expect_viewer_passed()
    result.expect_viewer_part(("grant_version",), 2)

    result = story.user_presses_in(story.supervisor_owner_environment, "/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": 1,
        "change": {"kind": "configure", "grant": {**grant, "wake_interval_minutes": 60}},
    })
    result.expect_viewer_refused("settings changed since you opened them; reload")

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    result.expect_viewer_part(("grant_version",), 2)
    result.expect_viewer_part(("grant", "wake_interval_minutes"), 30)
    result.expect_viewer_part(("grant", "capabilities", "plan approve"), {"on": True, "mode": "act"})
    story.expect_stack(story.agents.subject, Ready)
