from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import WorkersOptions
from tests.stories.fixtures.main.orchestrator_worker_delivered import OrchestratorWorkerDelivered
from tests.stories.fixtures.state_fixture import StateFixture


class VerifierJudgingModel(StateFixture):
    """With every merge sampled, the orchestrator checked both proofs of its delivered worker and merged its work, so the journal sent a verifier to judge whether the worker's model fit, whose session started: story.agents.verifiers.first()."""

    stack = (Orchestrating,)

    parent = OrchestratorWorkerDelivered

    settings = ((WorkersOptions.MODEL_FIT_SAMPLE, 1),)

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"worker check {self.workers.first} 1")
        story.agent_runs(story.agents.main, f"worker check {self.workers.first} 2")
        story.agent_runs(story.agents.main, f"worker merge {self.workers.first}")
        self.verifiers.first = story.newest("verifiers")
        story.agent_starts_a_session(story.agents.verifiers.first())

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Orchestrating)
