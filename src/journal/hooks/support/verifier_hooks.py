from journal.engine.support.session_agents import SessionAgents
from journal.hooks.support.agent_identity import AgentIdentity
from journal.models.agent_role import AgentRole
from journal.models.environment import Environment
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.hook import Hook


class VerifierHooks:
    """A hook from a verifier's run: taken in by the verifier's token in place of the launch id, its session bound to the verifier's row when the row names none yet, and its agent row made in the verifier's role."""

    def __init__(self, identity: AgentIdentity, verifiers: Verifiers, agents: SessionAgents) -> None:
        self.identity, self.verifiers, self.agents = identity, verifiers, agents

    def is_proven(self, hook: Hook) -> bool:
        return hook.verifier is not None and self.identity.is_verifier_token(hook.verifier, hook.actor_token)

    def bind(self, hook: Hook, environment: Environment) -> None:
        if hook.verifier is None:
            return
        verifier = self.verifiers.find(hook.verifier)
        if not verifier.session:
            self.verifiers.save(verifier.with_(session=hook.session), Actor.system())
        self.agents.helper_agent(hook.session, environment.row_id, hook.provider, AgentRole.VERIFIER)
