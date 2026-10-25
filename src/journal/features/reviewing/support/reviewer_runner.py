from journal.config import Config
from journal.models.reviewer import Reviewer
from journal.providers.providers import Providers
from journal.providers.support.helper_runner import HelperRunner
from journal.providers.support.helper_setup import HelperSetup
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.reviewers import Reviewers
from journal.repositories.scope import Scope

REVIEWER_SECONDS = 1200


class ReviewerRunner(HelperRunner[Reviewer]):
    """Runs a reviewer the journal sent, for twenty minutes at most before it ends without a report, time enough to run the tests the proofs name."""

    seconds = REVIEWER_SECONDS

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, reviewers: Reviewers, environments: Environments, agents: Agents, scope: Scope) -> None:
        super().__init__(config, providers, setup, reviewers, environments, agents, scope)
