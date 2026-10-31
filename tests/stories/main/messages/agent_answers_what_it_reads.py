from journal.engine.states.demand_block import DemandBlock
from journal.features.messages.messages_nudges import MESSAGE_REPLY, MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.unanswered_message import UnansweredMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.ANSWER_REQUEST_LIMIT, 2)
def test_a_message_read_and_not_answered_is_asked_about_before_tools_wait(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(story.agents.subject, message)
    story.agent_consumes(story.agents.subject, MessagesOptions.ANSWER_REQUEST_LIMIT)
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_told(story.agents.subject, MessagesNudges.UNANSWERED_COUNTDOWN, messages=message)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.TOOL_BLOCK_LIMIT, 2)
def test_every_tool_waits_after_the_set_uses_until_the_agent_replies(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(story.agents.subject, message)
    story.agent_consumes(story.agents.subject, MessagesOptions.TOOL_BLOCK_LIMIT)
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=message)
    story.expect_stack(story.agents.subject, Ready, DemandBlock)
    result = story.agent_replies(story.agents.subject, message, "it is")
    result.expect_agent_told(story.agents.subject, MessagesNudges.REPLY_REPEAT_WARNING, n=message)
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(UnansweredMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reaction_instead_of_a_reply_lifts_the_hold(story):
    story.agent_reacts(story.agents.subject, story.messages.first, "👍")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_one_reply_to_a_group_of_messages_read_together_lifts_the_hold(story):
    first = story.user_sends_message("is the footer done?")
    second = story.user_sends_message("and the header?")
    story.agent_runs(story.agents.subject, "message unread")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=f"{first}, {second}")
    story.agent_replies(story.agents.subject, second, "both are done")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(UnansweredMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_stop_under_the_hold_goes_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=story.messages.first)
    story.expect_stack(story.agents.subject, Ready, DemandBlock)


@story(UnansweredMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_command_reply_satisfies_the_unanswered_message_before_stop(story):
    story.agent_is_prompted(story.agents.subject, "answer the message")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=story.messages.first)
    result.expect_agent_told_words(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, MESSAGE_REPLY)
    reply = story.agent_replies_with_number(story.agents.subject, story.messages.first, "the footer is done")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_message(reply, author="agent", reply_target=story.messages.first)
    story.expect_newest_agent_message("the footer is done")
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_the_hold_leaves_the_task_in_hand_as_it_was(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(story.agents.subject, message)
    story.agent_reads(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready, Working, DemandBlock)
    story.agent_replies(story.agents.subject, message, "nearly")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
def test_the_hold_over_a_plan_returns_to_the_plan(story):
    message = story.user_sends_message("how far is the plan?")
    story.agent_reads_message(story.agents.subject, message)
    story.agent_reads(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan, DemandBlock)
    story.agent_replies(story.agents.subject, message, "one task in")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_the_agent_never_read_never_holds_its_tools(story):
    story.user_sends_message("is the footer done?")
    story.agent_consumes(story.agents.subject, MessagesOptions.TOOL_BLOCK_LIMIT)
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK)
    story.expect_stack(story.agents.subject, Ready, DemandBlock)


@story(BriefedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_is_never_held_for_the_agents_messages(story):
    worker = story.agent_dispatches_worker(story.agents.subject, "Lady Lovelace", story.tasks.briefed)
    story.agent_clocks_in(story.agents.workers.get(worker))
    message = story.user_sends_message("is the parser done?")
    story.agent_reads_message(story.agents.subject, message)
    result = story.agent_runs(story.agents.workers.get(worker), "todo list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(MessagesOptions.TOOL_BLOCK_LIMIT, 1)
def test_a_reply_to_a_later_message_leaves_the_first_one_owed(story):
    first = story.user_sends_message("is the footer done?")
    story.agent_reads_message(story.agents.subject, first)
    story.agent_consumes(story.agents.subject, MessagesOptions.TOOL_BLOCK_LIMIT)
    later = story.user_sends_message("and the header?")
    story.agent_reads_message(story.agents.subject, later)
    story.agent_replies(story.agents.subject, later, "the header is next")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=first)
    story.expect_stack(story.agents.subject, Ready, DemandBlock)
