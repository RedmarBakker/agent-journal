from journal.features.health.health_nudges import HealthNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_what_went_around_the_journal_while_it_did_not_answer_is_told_once_at_the_next_hook(story):
    story.a_hook_went_around_the_journal()
    story.a_hook_went_around_the_journal()
    story.a_shell_line_went_around_the_journal("git status")
    story.agent_reads(story.agents.subject)
    story.expect_allowed()
    story.expect_agent_told(story.agents.subject, HealthNudges.UNCHECKED_WORK)
    story.expect_answer_text("git status")
    story.expect_chat_holds("The journal was too slow to check some of the agent's work")
    story.agent_reads(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, HealthNudges.UNCHECKED_WORK)
    story.expect_stack(story.agents.subject, Ready)
