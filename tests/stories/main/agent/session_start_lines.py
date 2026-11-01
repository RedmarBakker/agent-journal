from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.voices.voices_nudges import VoicesNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.fixtures.main.session_skills_enabled import SessionSkillsEnabled
from tests.stories.fixtures.main.task_queue import TaskQueue
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_start_says_the_journal_is_ready_how_to_handle_it_the_laws_and_asks_for_the_overview(story):
    fresh_session = StoryAgent(AgentRole.MAIN, session="start-lines")
    result = story.agent_starts_a_session(fresh_session)
    result.expect_agent_told(fresh_session, BriefingNudges.JOURNAL_READY)
    result.expect_agent_told(fresh_session, BriefingNudges.JOURNAL_DISCRETION)
    result.expect_agent_told(fresh_session, BriefingNudges.JOURNAL_LAWS)
    result.expect_agent_told(fresh_session, BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(fresh_session, Ready)


@story(SessionSkillsEnabled, subject=AgentRole.MAIN)
def test_a_new_session_is_told_to_read_its_skills_and_overview_before_its_introduction(story):
    fresh_session = StoryAgent(AgentRole.MAIN, session="fresh-start")
    result = story.agent_starts_a_session(fresh_session)
    result.expect_agent_told(fresh_session, SkillsNudges.SKILL_READ_REQUEST)
    result.expect_agent_told_words(fresh_session, SkillsNudges.SKILL_READ_REQUEST, "the journal skill")
    result.expect_agent_told_words(fresh_session, SkillsNudges.SKILL_READ_REQUEST, "the etiquette skill")
    result.expect_agent_told_words(fresh_session, SkillsNudges.SKILL_READ_REQUEST, "the messages skill")
    result.expect_agent_told(fresh_session, BriefingNudges.OVERVIEW_REQUEST)
    result.expect_agent_not_told(fresh_session, BriefingNudges.PENDING_ITEMS)
    result.expect_agent_not_told(fresh_session, VoicesNudges.INTRODUCE_YOURSELF)
    story.expect_typed_text("the journal skill")
    story.expect_typed_text("the etiquette skill")
    story.expect_typed_text("the messages skill")
    story.expect_typed_text("journal environment overview")

    for skill in ("journal", "journal-etiquette", "journal-messages"):
        result = story.agent_reads_a_skill(fresh_session, skill)
        result.expect_allowed()
        if skill == "journal-messages":
            result.expect_agent_told(fresh_session, VoicesNudges.INTRODUCE_YOURSELF)
        else:
            result.expect_agent_not_told(fresh_session, VoicesNudges.INTRODUCE_YOURSELF)

    story.expect_stack(fresh_session, Ready)


@story(TaskQueue, subject=AgentRole.MAIN)
def test_a_start_lists_what_waits_for_the_agent(story):
    story.user_sends_message("is the footer done?")
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, BriefingNudges.PENDING_ITEMS)
    story.expect_task(story.tasks.open, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_session_start_does_not_name_a_missing_task_as_in_hand(story):
    result = story.agent_runs(story.agents.subject, "panic working task_id=1")
    result.expect_command_passed()
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_stack(story.agents.subject, Ready)


