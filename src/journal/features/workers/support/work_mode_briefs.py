from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, SOLO_MODE


class WorkModeBriefs:
    """What each work mode asks of the agent, the one text the workers skill teaches and `journal mode show` prints."""

    BRIEFS = {
        BUILDER_MODE: 'Builder, the default: you build it yourself and send a worker when a job is better done beside you.',
        ORCHESTRATOR_MODE: "Orchestrator: you plan, give every task you can to a worker and review what comes back; a stop or a long idle time with open tasks tells you to check the plans and dispatch, and a current task is one to hand over, never to do yourself. The builder is handed its next task at a stop or when its task closes; the orchestrator asks for its next tasks: `journal task next --quantity <n>` names the next n tasks to give workers, the started plans in turn so each moves fairly and the most pressing first, and starts none; use it to choose what to dispatch or queue unless the user says otherwise, and who takes which stays your choice. The orchestrator decides on its own and keeps the work moving; it waits for the user only before a step that cannot be undone or reaches outside the project. A task that waits on something blocks that task alone: it blocks it and continues with every other open task. A task that waits on another task is blocked with `journal task block <n> --on task:<m>`, one that waits on anything else with `--until '<command>'`, so it opens by itself; a wait written only in words, in a log line or a reply, is one the journal cannot see, and you are told to make it a block. Blocked or paused tasks that stand still for workers.held_still_minutes, or that pass workers.held_share of the tasks not done, are named as a plan to restructure; a started plan with workers.unordered_plan_tasks open tasks and none blocked on another is asked which depend on which.",
        SOLO_MODE: "Solo: you do everything yourself and a worker's dispatch is refused.",
    }

    @classmethod
    def brief(cls, mode: str) -> str:
        return cls.BRIEFS[mode]

    @classmethod
    def teaching(cls) -> str:
        return " ".join(cls.BRIEFS.values())
