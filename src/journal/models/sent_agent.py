from dataclasses import dataclass, fields

from journal.models.scoped import Scoped

SENT_AGENTS = "sent_agents"
# a verifier, kept on one machine, still numbers its rows from the workers' block, so its number never meets a worker's in the one table
WORKER_POOL = "workers"


@dataclass(frozen=True)
class SentAgent(Scoped):
    """An agent sent on one job, a worker or a verifier, stored in the one table of sent agents, its kind saying which: its name and brief, its program and model, its session, the hash of the token its run proves itself with, and its process."""

    name: str = ""
    brief: str = ""
    provider: str = "claude"
    model: str = ""
    session: str = ""
    token_hash: str = ""
    pid: int = 0
    kind: str = ""

    @classmethod
    def storage(cls) -> str:
        return SENT_AGENTS

    @classmethod
    def kind_filter(cls) -> dict[str, str]:
        return {"kind": next(field.default for field in fields(cls) if field.name == "kind")}

    @classmethod
    def number_pool(cls) -> str | None:
        return WORKER_POOL
