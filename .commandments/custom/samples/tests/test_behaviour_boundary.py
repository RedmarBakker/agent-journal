def test_hook(app):
    # @sin BehaviourTestOutsideStoriesDetector
    hook(app, "SessionStart")
    # @sin BehaviourTestOutsideStoriesDetector
    app.console().run(["task", "list"], AGENT)
    # @righteous BehaviourTestOutsideStoriesDetector
    parsed = Chain.split("ls && pwd")
    # @righteous BehaviourTestOutsideStoriesDetector
    assert task.started(moment).state == "started"
