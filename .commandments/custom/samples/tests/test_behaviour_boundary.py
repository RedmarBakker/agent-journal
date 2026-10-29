def test_a_hook_is_answered(app):
    # @sin BehaviourTestOutsideStoriesDetector
    hook(app, "SessionStart")
    # @sin BehaviourTestOutsideStoriesDetector
    app.console().run(["task", "list"], AGENT)
    # @righteous BehaviourTestOutsideStoriesDetector
    parsed = Chain.split("ls && pwd")
    # @righteous BehaviourTestOutsideStoriesDetector
    assert task.started(at).state == "started"
