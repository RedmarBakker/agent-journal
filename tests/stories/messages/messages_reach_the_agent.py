from tests.stories.fixtures.ended_session import EndedSession
from tests.stories.fixtures.read_message import ReadMessage
from tests.stories.fixtures.two_unread_messages import TwoUnreadMessages
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.started_plan import StartedPlan
from tests.stories.fixtures.started_task import StartedTask


@story(TwoUnreadMessages, end=[Ready])
def test_two_unread_messages_are_named_by_number_at_the_stop(story):
    story.agent_stops()
    story.expect_agent_told(MessagesNudges.NEW_MESSAGES, ns=f"{story.start.first_message}, {story.start.second_message}")


@story(TwoUnreadMessages, end=[Ready])
def test_four_unread_messages_are_named_by_their_count_at_the_stop(story):
    story.repeat(2, lambda: story.user_sends_message("one more thing"))
    story.agent_stops()
    story.expect_agent_told(MessagesNudges.UNREAD_MESSAGES, count=4)
    story.expect_message(story.start.first_message, author="user")
    story.expect_message(story.start.second_message, author="user")


@story(ReadMessage, end=[Ready])
def test_a_message_read_is_not_named_again_at_the_stop(story):
    story.agent_replies(story.start.message, "it is")
    story.agent_stops()
    story.expect_agent_not_told(MessagesNudges.NEW_MESSAGE)


@story(EndedSession, end=[Ready])
def test_a_message_left_while_no_session_ran_is_named_at_the_next_start(story):
    message = story.user_sends_message("start with the header tomorrow")
    story.agent_starts_a_session()
    story.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)


@story(EndedSession, end=[Ready])
def test_a_message_is_named_when_the_user_resumes_the_session(story):
    message = story.user_sends_message("the header first")
    story.agent_resumes_the_session()
    story.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)


@story(StartedTask, end=[Ready, Working])
def test_a_message_to_an_agent_with_a_task_in_hand_leaves_its_task_as_it_was(story):
    story.user_sends_message("is the footer done?")
    story.agent_reads()
    story.expect_stack(Ready, Working)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedPlan, end=[Ready, FollowingPlan])
def test_a_message_to_an_agent_following_a_plan_leaves_the_plan_as_it_was(story):
    story.user_sends_message("how far is the plan?")
    story.agent_reads()
    story.expect_stack(Ready, FollowingPlan)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)


@story(StartedTask, end=[Ready, Working])
def test_the_users_prompt_ends_the_agents_wait(story):
    story.agent_runs("await 'the build' --until false")
    story.expect_stack(Ready, Working, ExternalWait)
    story.agent_is_prompted("look at the header meanwhile")
    story.expect_stack(Ready, Working)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
