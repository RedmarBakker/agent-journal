from journal.features.plans.support.plan_branch_merge import PlanBranchMerge
from journal.support.listener_queue import ListenerQueue
from tests.stories.fixtures.main.finished_solo_plan_with_branch import FinishedSoloPlanWithBranch
from tests.stories.fixtures.main.started_solo_plan_branch import PLAN_AGENT_SESSION, StartedSoloPlanBranch


class FinishedSoloPlanWithBranchBeforeMerge(FinishedSoloPlanWithBranch):
    """A finished solo Plan agent still has its branch because the test is about the explicit merge command."""

    parent = StartedSoloPlanBranch

    def steps(self, story) -> None:
        with story.monkeypatch.context() as patch:
            patch.setattr(PlanBranchMerge, "merge", lambda *_args: "")
            environment = f"plan-{self.plans.first}"
            story.agent_in_runs(story.agents.main, environment, PLAN_AGENT_SESSION, f"task complete {self.tasks.second} --how done")
            story.agent_in_runs(story.agents.main, environment, PLAN_AGENT_SESSION, f"task complete {self.tasks.first} --how done")
            story.app.container.get(ListenerQueue).drain()
