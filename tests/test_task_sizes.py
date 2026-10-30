import pytest

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.support.task_size_scale import TaskSizeScale
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.task_sizes import TaskSizes
from journal.repositories.tasks import CURRENT_TASK_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection


def test_task_size_scale_versions_configuration_and_keeps_unknown_distinct_from_zero(app):
    scale = app.container.get(TaskSizeScale)
    assert scale.parse("unknown") is None
    assert scale.parse("13") == 13
    original = scale.version()
    app.container.get(SettingRows).set(EstimatesOptions.SIZE_SCALE.key, [1, 2, 5, 8], Actor.system())
    assert scale.version() != original
    with pytest.raises(Rejection, match="zero is not a size"):
        scale.parse(0)
    with pytest.raises(Rejection, match="split the work"):
        scale.parse(13)
    with pytest.raises(Rejection, match="one of 1, 2, 5, 8"):
        scale.parse(3)


def test_task_size_writer_keeps_baseline_revisions_and_authority_in_history(app):
    with app.container.get(Scope).environment(1):
        plans, tasks, links, sizes = (app.container.get(kind) for kind in (Plans, Tasks, Links, TaskSizes))
        owner = Actor.user(1)
        plan = plans.save(Plan(title="the release"), owner)
        task = sizes.compose(plan, Task(title="deploy the release"), 3, owner)
        links.linked(Ref.build(task), Ref.build(plan), PLAN_LINK, owner)
        sizes.revise(task.row_id, 5, "the proof requires a second environment", owner)
        sizes.revise_scope(task.row_id, 8, "the release also includes the rollback path", owner)

        rows = sizes.history(tasks.find(task.row_id))
        assert [row.change_type for row in rows] == ["planning_baseline", "size_revision", "scope_revision"]
        assert [row.size for row in rows] == [3, 5, 8]
        assert [row.reason for row in rows] == ["plan composition", "the proof requires a second environment", "the release also includes the rollback path"]
        assert all(row.creator == owner and row.created_at is not None and row.scale_version for row in rows)
        assert sizes.show(task.row_id)["planning_baseline_size"] == 3
        assert sizes.show(task.row_id)["current_size"] == 8
        with pytest.raises(Rejection, match="history is immutable"):
            sizes.save(rows[0].with_(reason="rewritten"), owner)
        with pytest.raises(Rejection, match="history is immutable"):
            sizes.delete(rows[0], owner)

        with pytest.raises(Rejection, match="only the plan owner or active plan builder"):
            sizes.revise(task.row_id, 5, "an unrelated user changed it", Actor.user(2))
        assert tasks.find(task.row_id).size == 8
        assert len(sizes.history(tasks.find(task.row_id))) == 3


def test_worker_size_proposal_is_linked_but_never_changes_the_current_task_size(app):
    with app.container.get(Scope).environment(1):
        plans, tasks, workers, links, sizes = (app.container.get(kind) for kind in (Plans, Tasks, Workers, Links, TaskSizes))
        owner = Actor.user(1)
        plan = plans.save(Plan(title="the release"), owner)
        task = sizes.compose(plan, Task(title="write the integration", state=TaskState.STARTED), 3, owner)
        links.linked(Ref.build(task), Ref.build(plan), PLAN_LINK, owner)
        worker = workers.save(Worker(name="Lady Lovelace"), owner)
        links.linked(Ref.build(worker), Ref.build(task), CURRENT_TASK_LINK, owner)

        proposal = sizes.propose(task.row_id, 5, "the integration includes another environment", Actor.worker(worker.row_id))

        assert proposal.change_type == "resize_proposal"
        assert proposal.creator == Actor.worker(worker.row_id)
        assert tasks.find(task.row_id).size == 3
        assert sizes.show(task.row_id)["current_size"] == 3
        assert sizes.show(task.row_id)["proposal_history"][0]["size"] == 5
