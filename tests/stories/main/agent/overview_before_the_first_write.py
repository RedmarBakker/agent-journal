from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(NewSession, subject=AgentRole.MAIN)
def test_a_write_before_the_overview_is_refused(story):
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_reads_and_journal_commands_go_through_before_the_overview(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_the_overview_frees_the_writes(story):
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_a_stop_before_the_overview_is_refused(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, BriefingNudges.OVERVIEW_STOP)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_resumed_session_needs_no_new_overview(story):
    story.agent_resumes_the_session(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
