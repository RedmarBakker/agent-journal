from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_other_owner_feedback import SupervisorOtherOwnerFeedback
from tests.stories.fixtures.main.supervisor_proposal_history import SupervisorProposalHistory


@story(SupervisorProposalHistory, subject=AgentRole.MAIN)
def test_an_owner_saves_feedback_turns_a_correction_into_a_rule_and_removes_it(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    environment = story.app.container.get(Environments).find(plan.environment_id).name
    result = story.user_opens_in(environment, "/journal/supervisor/history")
    result.expect_viewer_passed()
    history_id = story.viewer_answer["history"][0]["id"]

    result = story.user_presses_in(environment, f"/journal/supervisor/history/{history_id}/feedback", {
        "useful": True,
        "comment": "The proposal matched the failed check.",
        "correction": "Inspect the check output before changing its interval.",
    })
    result.expect_viewer_passed()
    result.expect_viewer_part(("feedback", "useful"), True)
    result.expect_viewer_part(("feedback", "comment"), "The proposal matched the failed check.")

    result = story.user_presses_in(environment, f"/journal/supervisor/history/{history_id}/feedback/rule", {})
    result.expect_viewer_passed()
    rule_id = story.viewer_answer["rule"]["id"]

    result = story.user_opens_in(environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    result.expect_viewer_part(("rules", 0, "id"), rule_id)

    result = story.user_presses_in(environment, f"/journal/supervisor/rules/{rule_id}/delete", {})
    result.expect_viewer_passed()
    result = story.user_opens_in(environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    result.expect_viewer_part(("rules",), [])
    story.expect_stack(story.agents.main, Ready)


@story(SupervisorOtherOwnerFeedback, subject=AgentRole.MAIN)
def test_a_nonowner_can_give_feedback_but_cannot_turn_a_correction_into_a_rule(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    environment = story.app.container.get(Environments).find(plan.environment_id).name
    result = story.user_opens_in(environment, "/journal/supervisor/history")
    result.expect_viewer_passed()
    history_id = story.viewer_answer["history"][0]["id"]

    result = story.user_presses_in(environment, f"/journal/supervisor/history/{history_id}/feedback", {
        "useful": False,
        "comment": "The proposed change did not use the failure output.",
        "correction": "Use the failure output before choosing a check interval.",
    })
    result.expect_viewer_passed()
    result.expect_viewer_part(("feedback", "useful"), False)

    result = story.user_presses_in(environment, f"/journal/supervisor/history/{history_id}/feedback/rule", {})
    result.expect_viewer_refused("not authorized")
    story.expect_stack(story.agents.main, Ready)
