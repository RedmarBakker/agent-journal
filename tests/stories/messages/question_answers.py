from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.questions.questions_nudges import QuestionsNudges
from journal.features.questions.states.waiting import Waiting
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.started_plan import StartedPlan
from tests.stories.fixtures.started_task import StartedTask


@story(WorkingAgent, end=[Ready])
def test_an_answered_question_is_told_to_the_agent_and_ends_its_wait(story):
    question = story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(Ready, Waiting)
    story.user_answers(question, "The agent writes the short one")
    story.expect_agent_told(QuestionsNudges.QUESTION_ANSWERED, n=question)
    story.agent_reads()


@story(StartedTask, end=[Ready, Working])
def test_a_question_asked_with_a_task_in_hand_waits_over_the_task_and_returns_to_it(story):
    question = story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(Ready, Working, Waiting)
    story.user_answers(question, "The agent writes the short one")
    story.agent_reads()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedPlan, end=[Ready, FollowingPlan])
def test_a_question_asked_while_a_plan_is_followed_returns_to_the_plan(story):
    question = story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.expect_stack(Ready, FollowingPlan, Waiting)
    story.user_answers(question, "The agent writes the short one")
    story.agent_reads()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)


@story(WorkingAgent, end=[Ready])
def test_the_agents_own_tool_use_ends_its_wait(story):
    story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_reads()
    story.expect_stack(Ready)


@story(WorkingAgent, end=[Ready, Waiting])
def test_a_journal_command_while_waiting_keeps_the_wait(story):
    story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_creates_task("the header")
    story.expect_stack(Ready, Waiting)


@story(WorkingAgent, end=[Ready, Waiting])
def test_a_stop_while_waiting_for_an_answer_goes_through(story):
    story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_stops()
    story.expect_allowed()


@story(WorkingAgent, end=[Ready])
def test_the_users_own_words_end_the_wait(story):
    story.agent_asks("which footer?", "The agent writes the short one", "The agent writes the long one")
    story.agent_is_prompted("the short one, please")
    story.expect_stack(Ready)


@story(WorkingAgent, end=[Ready])
def test_options_that_say_I_or_we_are_refused(story):
    story.agent_runs("question ask 'which footer?' --options 'I write the short one' 'we write the long one'")
    story.expect_command_refused()
