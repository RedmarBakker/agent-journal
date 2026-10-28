from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import WorkersOptions
from tests.stories.fixtures.main.orchestrator_worker_delivered import OrchestratorWorkerDelivered
from tests.stories.fixtures.state_fixture import StateFixture


class VerifierJudgingModel(StateFixture):
    """With every merge sampled, the orchestrator checked both proofs of its delivered worker and merged its work, so the journal sent a verifier to judge whether the worker's model fit, whose session started: start.verifier."""

    stack = (Orchestrating,)

    parent = OrchestratorWorkerDelivered

    settings = ((WorkersOptions.MODEL_FIT_SAMPLE, 1),)

    def steps(self, story) -> None:
        story.agent_runs(f"worker check {self.worker} 1")
        story.agent_runs(f"worker check {self.worker} 2")
        story.agent_runs(f"worker merge {self.worker}")
        self.verifier = story.newest("verifiers")
        story.verifier_session_starts(self.verifier)

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)
