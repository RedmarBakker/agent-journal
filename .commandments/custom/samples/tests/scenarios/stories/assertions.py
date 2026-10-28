def test_task_completion(scenario):
    # @sin ScenarioAssertDetector
    assert scenario.task.state == "completed"
    if scenario.task:
        # @sin ScenarioAssertDetector
        assert scenario.task.id > 0
    # @righteous ScenarioAssertDetector
    scenario.expect_task(1, state="completed")
    # @righteous ScenarioAssertDetector
    text = "assert is text here"


async def test_task_result(scenario):
    # @sin ScenarioAssertDetector
    assert scenario.task


# @sin ScenarioAssertDetector
assert True
