from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_proposal_history import SupervisorProposalHistory


@story(SupervisorProposalHistory, subject=AgentRole.MAIN)
def test_an_owner_accepts_a_proposal_once_and_sees_why_a_repeat_is_refused(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    environment = story.app.container.get(Environments).find(plan.environment_id).name
    result = story.user_opens_in(environment, "/journal/supervisor/history")
    result.expect_viewer_passed()
    proposals = [row for row in story.viewer_answer["history"] if row["result"] == "Proposed"]
    first, second = proposals
    first_id, second_id = first["id"], second["id"]
    first_receipt, second_receipt = first["actions"][0]["receipt_id"], second["actions"][0]["receipt_id"]
    accept = f"/journal/plans/{story.plans.first}/supervisor/receipts/{first_receipt}/accept"
    decline = f"/journal/plans/{story.plans.first}/supervisor/receipts/{second_receipt}/decline"

    result = story.user_presses_in(environment, accept, {})
    result.expect_viewer_passed()
    result.expect_viewer_part(("decision",), "accepted")

    result = story.user_presses_in(environment, decline, {})
    result.expect_viewer_passed()
    result.expect_viewer_part(("decision",), "declined")

    result = story.user_opens_in(environment, "/journal/supervisor/history")
    result.expect_viewer_passed()
    accepted_index = next(index for index, row in enumerate(story.viewer_answer["history"])
                          if row["id"] == first_id)
    declined_index = next(index for index, row in enumerate(story.viewer_answer["history"])
                          if row["id"] == second_id)
    result.expect_viewer_part(("history", accepted_index, "actions", 0, "proposal_decision"), "accepted")
    result.expect_viewer_part(("history", declined_index, "actions", 0, "proposal_decision"), "declined")

    result = story.user_presses_in(environment, accept, {})
    result.expect_viewer_refused("already decided")
    story.expect_stack(story.agents.main, Ready)
