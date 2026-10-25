from journal.config import Config
from journal.models.verifier import Verifier
from journal.providers.providers import Providers
from journal.providers.support.helper_runner import HelperRunner
from journal.providers.support.helper_setup import HelperSetup
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.verifiers import Verifiers

VERIFIER_SECONDS = 600


class VerifierRunner(HelperRunner[Verifier]):
    """Runs a verifier the journal sent, for ten minutes at most before it ends without a verdict."""

    seconds = VERIFIER_SECONDS

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, verifiers: Verifiers, environments: Environments, agents: Agents, scope: Scope) -> None:
        super().__init__(config, providers, setup, verifiers, environments, agents, scope)
