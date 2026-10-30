def test_the_main_agent_writes(story):
    # @sin StoryStepOutsideScopeDetector
    story.main_agent_writes("parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_writes(story.agents.main, "parser.py")
    # @righteous StoryStepOutsideScopeDetector
    story.agent_clocks_in(story.agents.workers.first())
