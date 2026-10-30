from types import SimpleNamespace

from journal.http.controllers.organization import OrganizationController


def test_plan_points_count_only_positive_integer_sizes_and_leave_every_other_size_unknown():
    completed = SimpleNamespace(value="completed")
    open_state = SimpleNamespace(value="open")
    tasks = [SimpleNamespace(size=5, state=completed),
             SimpleNamespace(size=8, state=open_state),
             SimpleNamespace(size=None, state=open_state),
             SimpleNamespace(size=0, state=open_state),
             SimpleNamespace(size=True, state=open_state),
             SimpleNamespace(size="3", state=open_state)]

    assert OrganizationController.story_points(tasks) == {
        "total": 13,
        "done": 5,
        "sized_tasks": 2,
        "unknown_tasks": 4,
    }
