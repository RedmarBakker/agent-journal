from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

MODEL_ERROR = "Model 'haiku-9' not found"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_the_tool_could_not_run_is_failed_with_the_tools_error(story):
    story.agent_sends_subagent_that_fails(story.agents.subject, RESEARCHER, "no such model", MODEL_ERROR)
    story.user_opens("/journal/subagents")
    story.expect_viewer_rows("rows", "state", ["failed"])
    story.expect_viewer_rows("rows", "reason", [MODEL_ERROR])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_with_no_answer_ends_with_its_turn_and_one_in_the_background_goes_on_through_a_compaction(story):
    story.agent_sends_subagent(story.agents.subject, RESEARCHER, "cut off")
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "in the background", "a7")
    story.agent_stops(story.agents.subject)
    story.context_is_compacted()
    story.user_opens("/journal/subagents")
    story.expect_viewer_rows("rows", "task", ["cut off", "in the background"])
    story.expect_viewer_rows("rows", "state", ["stopped", "running"])
    story.expect_stack(story.agents.subject, Ready, ReadingOverview)
