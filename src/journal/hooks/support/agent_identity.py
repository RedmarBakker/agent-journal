from journal.repositories.verifiers import Verifiers
from journal.repositories.workers import Workers
from journal.support.caller_variables import CallerVariables
from journal.support.agent_token import AgentToken

REFUSAL = "this shell says it is a sent agent's but does not carry that agent's token: the journal takes nothing from it\n"


class AgentIdentity:
    """Checks that a command, a shell line or a hook that claims to be a worker's or a verifier's carries that agent's token; an actor that names a worker or a verifier but no number is refused too, and a worker row from before tokens passes as it did."""

    def __init__(self, workers: Workers, verifiers: Verifiers) -> None:
        self.workers, self.verifiers = workers, verifiers

    def is_proven(self, variables: CallerVariables) -> bool:
        return self.is_worker_proven(variables) and self.is_verifier_proven(variables)

    def is_worker_proven(self, variables: CallerVariables) -> bool:
        return variables.worker is None or self.is_token(variables.worker, variables.actor_token)

    def is_verifier_proven(self, variables: CallerVariables) -> bool:
        return variables.verifier is None or self.is_verifier_token(variables.verifier, variables.actor_token)

    def is_token(self, number: int, token: str | None) -> bool:
        rows = self.workers.global_matching(id=number)
        if not rows:
            return False
        return not rows[0].token_hash or AgentToken.is_proof(token, rows[0].token_hash)

    def is_verifier_token(self, number: int, token: str | None) -> bool:
        rows = self.verifiers.numbered(number)
        return bool(rows) and AgentToken.is_proof(token, rows[0].token_hash)
