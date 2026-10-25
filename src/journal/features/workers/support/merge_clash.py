from journal.support.rejection import Rejection

REBASE_JOB = "rebase your branch onto the project's branch, keep both sides of each conflict, commit and clock out again"


class MergeClash(Rejection):
    """A worker's merge refused because its branch clashes with the branch it merges into, saying in one line the files that clash and the command that sends the worker back to rebase; its proofs and its task are kept."""

    def __init__(self, worker: int, clashing: str) -> None:
        self.clashing = clashing
        super().__init__(f"worker {worker}'s work was not merged: its branch clashes\n{clashing}\nsend it back to rebase with journal worker send {worker} \"{REBASE_JOB}\"; its proofs and its task are as they were")
