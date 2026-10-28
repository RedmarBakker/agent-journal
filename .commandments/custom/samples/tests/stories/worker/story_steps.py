def test_the_worker_writes(story):
    # @sin StoryStepOutsideScopeDetector
    story.worker_writes(story.start.worker, "parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_writes("parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.main_agent_stops()
