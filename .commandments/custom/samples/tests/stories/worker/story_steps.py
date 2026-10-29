def test_the_worker_writes(story):
    # @sin StoryStepOutsideScopeDetector
    story.worker_writes(story.agents.workers.first(), "parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_writes(story.agents.subject, "parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_stops(story.agents.main)
