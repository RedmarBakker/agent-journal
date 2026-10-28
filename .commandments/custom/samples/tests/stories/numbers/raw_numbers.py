@story(StartedTask)
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_quiet(story):
    # @sin StoryNumberDetector
    story.agent_is_quiet_for(minutes=31)
    # @righteous StoryNumberDetector
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES) + 1)
    # @righteous StoryNumberDetector
    story.expect_agent_messages(0)
