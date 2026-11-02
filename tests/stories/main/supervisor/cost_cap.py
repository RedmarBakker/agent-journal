from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner


@story(SupervisorGrantOwner, subject=AgentRole.MAIN)
def test_an_owner_changes_the_daily_cost_cap_from_the_cost_page(story):
    environment = story.supervisor_owner_environment
    costs = story.user_opens_in(environment, "/journal/supervisor/costs")
    costs.expect_viewer_passed()

    control = story.user_opens_in(environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    control.expect_viewer_part(("grant", "watched_plans"), [story.plans.first])
    grant = control.viewer_answer["grant"]
    prior_cap = grant["limits"]["max_cost_microusd_per_day"]
    new_cap = prior_cap * 2
    costs.expect_viewer_part(("daily_cost_cap_microusd",), prior_cap)
    costs.expect_viewer_part(("wake_interval_minutes",), grant["wake_interval_minutes"])

    saved = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": control.viewer_answer["grant_version"],
        "change": {"kind": "configure", "grant": {
            **grant,
            "limits": {**grant["limits"], "max_cost_microusd_per_day": new_cap},
        }},
    })
    saved.expect_viewer_passed()

    updated = story.user_opens_in(environment, "/journal/supervisor/costs")
    updated.expect_viewer_passed()
    updated.expect_viewer_part(("daily_cost_cap_microusd",), new_cap)
    updated.expect_viewer_part(("wake_interval_minutes",), grant["wake_interval_minutes"])
    story.expect_stack(story.agents.subject, Ready)
