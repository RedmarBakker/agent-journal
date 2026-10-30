from journal.features.plans.support.plan_branch_merge import PlanBranchMerge
from journal.support.listener_queue import ListenerQueue
from tests.stories.fixtures.main.finished_solo_plan_with_branch import FinishedSoloPlanWithBranch
from tests.stories.fixtures.main.plan_approved import PlanApproved


class FinishedSoloPlanWithBranchBeforeMerge(FinishedSoloPlanWithBranch):
    """A finished solo Plan agent still has its branch because the test is about the explicit merge command."""

    parent = PlanApproved

    def steps(self, story) -> None:
        with story.monkeypatch.context() as patch:
            patch.setattr(PlanBranchMerge, "merge", lambda *_args: "")
            super().steps(story)
            story.app.container.get(ListenerQueue).drain()
