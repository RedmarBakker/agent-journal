from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.supervisor.supervisor_proposal import SupervisorProposal


class SupervisorProposalToDecide(SupervisorProposal):
    """The supervisor has a proposal waiting for the owner."""

    parent = SupervisorProposal

    def steps(self, story) -> None:
        proposal = story.supervisor_posts("/_supervisor/v1/apply", story.proposal_request)
        proposal.expect_viewer_passed()
        self.proposal_id = story.viewer_answer["proposal_id"]

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
