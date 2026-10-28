def test_the_main_agent_writes(story):
    # @sin StoryStepOutsideScopeDetector
    story.main_agent_writes("parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_writes("parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.worker_clocks_in(story.start.worker)
