from journal.features.updates.support.update_window import UpdateWindow
from tests.update_matrix_run import pairs


def test_the_update_matrix_tests_each_release_only_from_the_releases_of_the_five_minors_before_it():
    tags = ["v4.60.0", "v4.61.0", "v4.63.0", "v4.63.1", "v4.67.0", "v4.68.0", "v4.68.1"]
    kept = pairs(UpdateWindow(5), tags, "4.69.0", {"v4.60.0 v4.61.0"})
    assert kept == [
        ("v4.60.0", "v4.63.0"), ("v4.60.0", "v4.63.1"),
        ("v4.61.0", "v4.63.0"), ("v4.61.0", "v4.63.1"),
        ("v4.63.0", "v4.63.1"), ("v4.63.0", "v4.67.0"), ("v4.63.0", "v4.68.0"), ("v4.63.0", "v4.68.1"),
        ("v4.63.1", "v4.67.0"), ("v4.63.1", "v4.68.0"), ("v4.63.1", "v4.68.1"),
        ("v4.67.0", "v4.68.0"), ("v4.67.0", "v4.68.1"), ("v4.67.0", "tree"),
        ("v4.68.0", "v4.68.1"), ("v4.68.0", "tree"),
        ("v4.68.1", "tree"),
    ], "a start is kept only for targets at most five minors on, patches with their minor, across the gap from 4.63 to 4.67, less the pairs that passed"
    assert pairs(UpdateWindow(5), ["v4.68.0", "v5.0.0"], "5.0.0", set()) == [("v5.0.0", "tree")], "a new major starts a window of its own"
