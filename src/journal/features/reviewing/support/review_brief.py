from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.proofs import Proofs


class ReviewBrief:
    """What a reviewer is handed as its whole brief: the worker, its task's brief and each point with its latest proof, which a clock-out always has, the worker's report, the folder its work is in, and what to do and report."""

    def __init__(self, proofs: Proofs, branch: WorkerBranch) -> None:
        self.proofs, self.branch = proofs, branch

    def text(self, worker: Worker, task: Task, report: str) -> str:
        latest = {proof.point: proof for proof in sorted(self.proofs.task_proofs(task), key=lambda proof: proof.row_id)}
        points = "\n".join(f"{n}. {point}\n   proof, {latest[n].state}: {latest[n].text}" for n, point in enumerate(task.points(), 1))
        folder = self.branch.place(worker)
        return f"""You are the journal's reviewer. Worker {worker.id}, {worker.name}, clocked out of task {task.id}, {task.title}. Review its work for the agent that sent it; that agent decides, and you change no file and merge nothing.

Its work is in {folder}: run every command there, cd {folder} first.

The task's brief:
{task.brief}

Each point and the worker's proof of it:
{points}

The worker's report:
{report}

Do, in order:
1. Read each point and its proof, and the code the proof names.
2. Run the tests the proofs name, by the commands they give, in {folder}.
3. Judge the files the worker changed for sins with journal sins {folder}.
4. Critique the code against the project's rules in its CLAUDE.md and AGENTS.md.

Then give your one report, one short line per point, passed or short with why, and the tests you ran with how they ended:
journal review "1 passed. 2 short: <why>. Tests: <command> passed"
"""
