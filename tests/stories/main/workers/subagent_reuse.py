from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

MAPPER = "r1"
FILE = "src/journal/features/shell/chain.py"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_job_on_files_one_already_read_goes_back_to_it_and_a_review_is_always_fresh(story):
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, f"map {FILE}", MAPPER)
    story.subagent_ends(MAPPER)
    result = story.agent_sends_subagent(story.agents.subject, RESEARCHER, f"find the edge cases of {FILE}")
    result.expect_refusal_text("SendMessage")
    result.expect_refusal_text(MAPPER)
    result = story.agent_sends_subagent(story.agents.subject, "journal-planner", f"plan the edge cases of {FILE}")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
