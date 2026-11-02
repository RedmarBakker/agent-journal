from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_proposal import SupervisorProposal


def proposed(story):
    result = story.supervisor_posts("/_supervisor/v1/apply", story.proposal_request)
    result.expect_viewer_passed()
    return result.viewer_answer["proposal_id"]


def records(story):
    return story.user_opens_in(
        story.supervisor_environment,
        f"/journal/supervisor/records?period=last_7_days&plan_id={story.supervisor_plan}",
    )


@story(SupervisorProposal, subject=AgentRole.MAIN)
def test_an_owner_accepts_a_proposal_as_a_command_and_cannot_reuse_it(story):
    proposal_id = proposed(story)
    path = f"/journal/supervisor/proposals/{proposal_id}/accept"
    accepted = story.user_presses_in(story.supervisor_environment, path, {})
    accepted.expect_viewer_passed()
    accepted.expect_viewer_part(("status",), "accepted")
    accepted.expect_viewer_part(("command",), story.proposal_command)
    accepted.expect_viewer_part_is_truthy(("receipt_id",))
    story.expect_row_in(
        story.supervisor_environment,
        "plans",
        story.supervisor_plan,
        {"priorities": "Review the failing check first"},
    )

    again = story.user_presses_in(story.supervisor_environment, path, {})
    again.expect_viewer_refused("closed")
    again = story.user_presses_in(
        story.supervisor_environment,
        f"/journal/supervisor/proposals/{proposal_id}/decline",
        {},
    )
    again.expect_viewer_refused("closed")
    result = records(story)
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "proposals"), {"accepted": 1, "declined": 0})
    result.expect_viewer_part(("records", 0, "kind"), "proposal_decision")
    result.expect_viewer_part(("records", 0, "status"), "accepted")
    result.expect_viewer_part(("records", 0, "exit_code"), 0)
    result.expect_viewer_part(("records", 1, "kind"), "proposal")
    result.expect_viewer_part(("records", 1, "command"), story.proposal_command)
    result.expect_viewer_part(("records", 1, "wake_up"), story.proposal_wake_up)
    result.expect_viewer_part(("records", 1, "rationale"), story.proposal_rationale)
    story.expect_stack(story.agents.main, Ready)


@story(SupervisorProposal, subject=AgentRole.MAIN)
def test_an_owner_declines_a_proposal_and_cannot_reuse_it(story):
    proposal_id = proposed(story)
    path = f"/journal/supervisor/proposals/{proposal_id}/decline"
    declined = story.user_presses_in(story.supervisor_environment, path, {})
    declined.expect_viewer_passed()
    declined.expect_viewer_part(("status",), "declined")
    declined.expect_viewer_part_is_truthy(("receipt_id",))
    story.expect_row_in(story.supervisor_environment, "plans", story.supervisor_plan, {"priorities": ""})

    again = story.user_presses_in(
        story.supervisor_environment,
        f"/journal/supervisor/proposals/{proposal_id}/accept",
        {},
    )
    again.expect_viewer_refused("closed")
    again = story.user_presses_in(story.supervisor_environment, path, {})
    again.expect_viewer_refused("closed")
    result = records(story)
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "proposals"), {"accepted": 0, "declined": 1})
    result.expect_viewer_part(("records", 0, "kind"), "proposal_decision")
    result.expect_viewer_part(("records", 0, "status"), "declined")
    story.expect_stack(story.agents.main, Ready)


@story(SupervisorProposal, subject=AgentRole.MAIN)
def test_an_owner_cannot_accept_or_decline_a_stale_proposal(story):
    proposal_id = proposed(story)
    changed = story.user_types_in(
        story.supervisor_environment,
        f"plan priorities 'The owner changed the order' --plan {story.supervisor_plan}"
    )
    changed.expect_command_passed()

    result = story.user_presses_in(
        story.supervisor_environment,
        f"/journal/supervisor/proposals/{proposal_id}/accept",
        {},
    )
    result.expect_viewer_refused("stale")
    result = story.user_presses_in(
        story.supervisor_environment,
        f"/journal/supervisor/proposals/{proposal_id}/decline",
        {},
    )
    result.expect_viewer_refused("stale")
    story.expect_row_in(
        story.supervisor_environment,
        "plans",
        story.supervisor_plan,
        {"priorities": "The owner changed the order"},
    )
    result = records(story)
    result.expect_viewer_passed()
    result.expect_viewer_part(("current", "proposals"), {"accepted": 0, "declined": 0})
    story.expect_stack(story.agents.main, Ready)
