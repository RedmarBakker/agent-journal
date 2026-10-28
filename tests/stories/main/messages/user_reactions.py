from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask


@story(ReadMessage, mode=BUILDER_MODE)
def test_the_agents_own_reaction_is_never_told_back(story):
    story.agent_reacts(story.start.message, "🙏")
    story.agent_reads()
    story.expect_agent_not_told(MessagesNudges.USER_REACTION)
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE)
def test_two_different_reactions_are_each_told(story):
    reply = story.agent_replies_with_number(story.start.message, "it is")
    story.user_reacts(reply, "🎉")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="🎉")
    story.user_reacts(reply, "👀")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="👀")
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_reaction_leaves_the_task_in_hand_as_it_was(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "nearly")
    story.user_reacts(reply, "👍")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="👍")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_reaction_leaves_a_followed_plan_as_it_was(story):
    message = story.user_sends_message("how far is the plan?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "one task in")
    story.user_reacts(reply, "👍")
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_stack(Ready, FollowingPlan)
