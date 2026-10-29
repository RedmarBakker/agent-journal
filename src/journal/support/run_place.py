from dataclasses import dataclass

# the run a subagent's marks gather in, named by its actor
SUBAGENT_RUN = "subagent:"


@dataclass(frozen=True)
class RunPlace:
    """Where a chat card stands in a run of cards: which run, its step in it, the run's title, what its cards are called and the mark it is drawn with, so the viewer gathers a run's cards in step order: a sequence's steps, or one subagent's actions."""

    run: str
    step: int
    run_title: str
    run_noun: str = "steps"
    run_mark: str = "sequence"

    @classmethod
    def subagent(cls, actor_id: str, title: str) -> "RunPlace":
        return cls(f"{SUBAGENT_RUN}{actor_id}", 0, title[0].upper() + title[1:], "actions", "subagent")
