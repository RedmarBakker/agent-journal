from journal.engine.states.demand_block import DemandBlock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import settings, story
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.held_for_an_answer import HeldForAnAnswer
from tests.stories.fixtures.plan_just_started import PlanJustStarted
from tests.stories.fixtures.task_in_hand import TaskInHand
from tests.stories.fixtures.task_with_points_open import TaskWithPointsOpen


@story(AgentAtWork, end=[Ready])
@settings(MessagesOptions.ANSWER_REQUEST_LIMIT, 2)
def test_a_message_read_and_not_answered_is_asked_about_before_tools_wait(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    story.agent_consumes(MessagesOptions.ANSWER_REQUEST_LIMIT)
    story.agent_reads()
    story.expect_agent_told(MessagesNudges.UNANSWERED_COUNTDOWN, messages=message)


@story(AgentAtWork, end=[Ready])
@settings(MessagesOptions.TOOL_BLOCK_LIMIT, 2)
def test_every_tool_waits_after_the_set_uses_until_the_agent_replies(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    story.agent_consumes(MessagesOptions.TOOL_BLOCK_LIMIT)
    story.agent_reads()
    story.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=message)
    story.expect_stack(Ready, DemandBlock)
    story.agent_replies(message, "it is")
    story.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=message)
    story.agent_reads()
    story.expect_allowed()


@story(HeldForAnAnswer, end=[Ready])
def test_a_reaction_instead_of_a_reply_lifts_the_hold(story):
    story.agent_reacts(story.start.message, "👍")
    story.agent_reads()
    story.expect_allowed()


@story(AgentAtWork, end=[Ready])
@settings(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_one_reply_to_a_group_of_read_messages_lifts_the_hold(story):
    first = story.user_sends_message("is the footer done?")
    second = story.user_sends_message("and the header?")
    story.agent_reads_message(first)
    story.agent_reads_message(second)
    story.agent_reads()
    story.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=f"{first}, {second}")
    story.agent_replies(second, "both are done")
    story.agent_reads()
    story.expect_allowed()


@story(HeldForAnAnswer)
def test_a_stop_under_the_hold_goes_through(story):
    story.agent_stops()
    story.expect_allowed()
    story.agent_reads()
    story.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=story.start.message)


@story(TaskInHand, end=[Ready, Working])
@settings(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_the_hold_leaves_the_task_in_hand_as_it_was(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    story.agent_reads()
    story.expect_stack(Ready, Working, DemandBlock)
    story.agent_replies(message, "nearly")
    story.agent_reads()
    story.expect_allowed()
    story.expect_task(story.start.task_in_hand, state=TaskState.STARTED)


@story(PlanJustStarted, end=[Ready, FollowingPlan])
@settings(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_the_hold_over_a_plan_returns_to_the_plan(story):
    message = story.user_sends_message("how far is the plan?")
    story.agent_reads_message(message)
    story.agent_reads()
    story.expect_stack(Ready, FollowingPlan, DemandBlock)
    story.agent_replies(message, "one task in")
    story.agent_reads()
    story.expect_allowed()
    story.expect_task(story.start.task_in_hand, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)


@story(AgentAtWork, end=[Ready, DemandBlock])
def test_a_message_the_agent_never_read_never_holds_its_tools(story):
    story.user_sends_message("is the footer done?")
    story.agent_consumes(MessagesOptions.TOOL_BLOCK_LIMIT)
    story.agent_reads()
    story.expect_agent_not_told(MessagesNudges.UNANSWERED_TOOL_BLOCK)


@story(TaskWithPointsOpen, end=[Ready, ExternalWait])
def test_a_worker_is_never_held_for_the_agents_messages(story):
    worker = story.agent_dispatches_worker("Lady Lovelace", story.start.open_task)
    story.worker_clocks_in(worker)
    message = story.user_sends_message("is the parser done?")
    story.agent_reads_message(message)
    story.worker_tries(worker, "todo list")
    story.expect_command_passed()
