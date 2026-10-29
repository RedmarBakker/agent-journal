from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.questions.questions_nudges import QuestionsNudges
from journal.features.questions.states.waiting import Waiting
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_answered_question_is_told_to_the_agent_and_ends_its_wait(story):
    question = story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(story.agents.subject, Ready, Waiting)
    card = story.card_number(f"question:{question}")
    story.expect_card(card, card_type="process", process="question", active=True)
    story.user_opens(f"/journal/cards/active?ids={card}")
    story.expect_viewer_shows(str(card), {"answer": None, "active": True})
    story.user_answers(question, "The agent writes the short one")
    story.expect_agent_told(story.agents.subject, QuestionsNudges.QUESTION_ANSWERED, n=question)
    story.expect_card(card, answer="The agent writes the short one", active=False)
    story.user_opens(f"/journal/cards/active?ids={card}")
    story.expect_viewer_shows(str(card), None)
    story.agent_reads(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_question_asked_with_a_task_in_hand_waits_over_the_task_and_returns_to_it(story):
    question = story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(story.agents.subject, Ready, Working, Waiting)
    story.user_answers(question, "The agent writes the short one")
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_question_asked_while_a_plan_is_followed_returns_to_the_plan(story):
    question = story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan, Waiting)
    story.user_answers(question, "The agent writes the short one")
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agents_own_tool_use_ends_its_wait(story):
    story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_reads(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_command_while_waiting_keeps_the_wait(story):
    story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_creates_task(story.agents.subject, "the header")
    story.expect_stack(story.agents.subject, Ready, Waiting)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_stop_while_waiting_for_an_answer_goes_through(story):
    story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_stops(story.agents.subject)
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Waiting)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_users_own_words_end_the_wait(story):
    story.agent_asks(story.agents.subject, "which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_is_prompted(story.agents.subject, "the short one, please")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_options_that_say_I_or_we_are_refused(story):
    story.agent_runs(story.agents.subject, "question ask 'which footer?' --options 'I write the short one' 'we write the long one'")
    story.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_question_asked_from_outside_an_agents_session_is_refused(story):
    story.user_types("question ask 'Which?'")
    story.expect_command_refused()
    story.expect_command_text("worker's report")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_providers_own_question_tool_is_refused_for_the_journals(story):
    story.agent_uses_the_providers_tool(story.agents.subject, "AskUserQuestion", question="which?")
    story.expect_refused(story.agents.subject, QuestionsNudges.JOURNAL_QUESTION_TOOL)
    story.expect_stack(story.agents.subject, Ready)
