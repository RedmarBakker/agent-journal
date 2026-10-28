from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.plan_just_started import PlanJustStarted
from tests.stories.fixtures.task_in_hand import TaskInHand


@story(AgentAtWork, end=[Ready])
def test_the_agents_own_reaction_is_never_told_back(story):
    message = story.user_sends_message("thanks")
    story.agent_reads_message(message)
    story.agent_reacts(message, "🙏")
    story.agent_reads()
    story.expect_agent_not_told(MessagesNudges.USER_REACTION)


@story(AgentAtWork, end=[Ready])
def test_two_different_reactions_are_each_told(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "it is")
    story.user_reacts(reply, "🎉")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="🎉")
    story.user_reacts(reply, "👀")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="👀")


@story(TaskInHand, end=[Ready, Working])
def test_a_reaction_leaves_the_task_in_hand_as_it_was(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "nearly")
    story.user_reacts(reply, "👍")
    story.expect_agent_told(MessagesNudges.USER_REACTION, n=reply, emoji="👍")
    story.expect_task(story.start.task_in_hand, state=TaskState.STARTED)


@story(PlanJustStarted, end=[Ready, FollowingPlan])
def test_a_reaction_leaves_a_followed_plan_as_it_was(story):
    message = story.user_sends_message("how far is the plan?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "one task in")
    story.user_reacts(reply, "👍")
    story.expect_stack(Ready, FollowingPlan)
    story.expect_task(story.start.task_in_hand, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
