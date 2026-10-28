def test_task_completion(scenario):
    # @sin StoryAssertDetector
    assert scenario.task.state == "completed"
    if scenario.task:
        # @sin StoryAssertDetector
        assert scenario.task.id > 0
    # @righteous StoryAssertDetector
    scenario.expect_task(1, state="completed")
    # @righteous StoryAssertDetector
    text = "assert is text here"


async def test_task_result(scenario):
    # @sin StoryAssertDetector
    assert scenario.task


# @sin StoryAssertDetector
assert True
