from journal.engine.support.session_agents import SessionAgents
from journal.hooks.support.agent_identity import AgentIdentity
from journal.support.agent_role import AgentRole
from journal.models.environment import Environment
from journal.models.helper import Helper
from journal.repositories.reviewers import Reviewers
from journal.repositories.checkers import Checkers
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.hook import Hook


class CheckerHooks:
    """A hook from the run of a checker the journal sent itself, a verifier or a reviewer: taken in by that agent's token in place of the launch id, its session bound to the agent's row when the row names none yet, and its agent row made in that agent's role."""

    def __init__(self, identity: AgentIdentity, verifiers: Verifiers, reviewers: Reviewers, agents: SessionAgents) -> None:
        self.identity, self.verifiers, self.reviewers, self.agents = identity, verifiers, reviewers, agents

    def is_proven(self, hook: Hook) -> bool:
        verifier = hook.verifier is not None and self.identity.is_verifier_token(hook.verifier, hook.actor_token)
        return verifier or (hook.reviewer is not None and self.identity.is_reviewer_token(hook.reviewer, hook.actor_token))

    def bind(self, hook: Hook, environment: Environment) -> None:
        if hook.verifier is not None:
            self.bound(self.verifiers.find(hook.verifier), self.verifiers, hook, environment, AgentRole.VERIFIER)
        if hook.reviewer is not None:
            self.bound(self.reviewers.find(hook.reviewer), self.reviewers, hook, environment, AgentRole.REVIEWER)

    def bound(self, checker: Helper, rows: Checkers, hook: Hook, environment: Environment, role: AgentRole) -> None:
        if not checker.session:
            rows.save(checker.with_(session=hook.session), Actor.system())
        self.agents.helper_agent(hook.session, environment.row_id, hook.provider, role)
