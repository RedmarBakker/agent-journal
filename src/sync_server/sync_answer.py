from dataclasses import dataclass

from sync_server.pull_answer import PullAnswer
from sync_server.push_answer import PushAnswer


@dataclass(frozen=True)
class SyncAnswer:
    """What a push is answered with: what became of its changes, and the pull it carried, so one request both sends and takes."""

    settlement: PushAnswer
    delivery: PullAnswer

    @classmethod
    def parsed(cls, settlement: dict, delivery: dict) -> "SyncAnswer":
        return cls(PushAnswer.parsed(**settlement), PullAnswer.parsed(**delivery))
