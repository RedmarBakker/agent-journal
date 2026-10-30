from dataclasses import dataclass


@dataclass(frozen=True)
class ReleasedTasks:
    """The tasks a worker let go together, the plan they all belong to if they share one, and the worker."""

    worker_id: int
    task_ids: tuple[int, ...]
    plan_id: int = 0

    def numbers(self) -> str:
        runs, ids = [], sorted(self.task_ids)
        for number in ids:
            if runs and number == runs[-1][1] + 1:
                runs[-1][1] = number
            else:
                runs.append([number, number])
        return ", ".join(f"{first} to {last}" if last - first > 1 else ", ".join(str(n) for n in range(first, last + 1)) for first, last in runs)

    def subject(self) -> str:
        plan = f" of plan {self.plan_id}" if self.plan_id else ""
        return f"tasks {self.numbers()}{plan} are" if len(self.task_ids) > 1 else f"task {self.task_ids[0]}{plan} is"

    def pronoun(self) -> str:
        return "them" if len(self.task_ids) > 1 else "it"
