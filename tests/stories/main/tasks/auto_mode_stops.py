from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.held_stops import HeldStops
from tests.stories.fixtures.main.looped_stops import LoopedStops
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.started_task import StartedTask


@story(HeldStops, subject=AgentRole.MAIN)
def test_held_stops_count_from_nothing_again_once_the_agent_works_between_them(story):
    story.agent_reads(story.agents.subject)
    for _ in range(PANIC_REFUSAL_COUNT - 1):
        result = story.agent_stops(story.agents.subject)
        result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(LoopedStops, subject=AgentRole.MAIN)
def test_after_a_dead_loop_let_a_stop_through_the_agents_next_work_holds_its_stops_again_from_nothing(story):
    story.agent_stops(story.agents.subject)
    story.agent_reads(story.agents.subject)
    for _ in range(PANIC_REFUSAL_COUNT - 1):
        result = story.agent_stops(story.agents.subject)
        result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(HeldStops, subject=AgentRole.MAIN)
def test_held_stops_count_from_nothing_again_after_the_users_message(story):
    story.agent_is_prompted(story.agents.subject, "go on with the footer")
    for _ in range(PANIC_REFUSAL_COUNT - 1):
        result = story.agent_stops(story.agents.subject)
        result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(ReadMessage, subject=AgentRole.MAIN)
def test_a_stop_held_for_closing_words_after_a_reply_does_not_count_towards_a_dead_loop(story):
    task = story.agent_takes_a_task(story.agents.subject, "the header")
    story.agent_is_prompted(story.agents.subject, "is the footer done?")
    reply = story.agent_replies_with_number(story.agents.subject, story.messages.first, "the footer is done")
    story.agent_closes_its_turn(story.agents.subject, "next I start the header")
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_carries(MessagesNudges.REPLY_CLOSING_WORDS, reply=reply)
    for _ in range(PANIC_REFUSAL_COUNT - 1):
        result = story.agent_stops_again(story.agents.subject)
        result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(task, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_in_auto_mode_an_agent_that_says_it_is_stuck_may_stop_with_its_task_in_hand(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal stuck 'the build needs a key only the user has'")
    result.expect_allowed()
    result = story.agent_runs(story.agents.subject, "stuck 'the build needs a key only the user has'")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready, Working, Impasse)
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, Impasse)


@story(StartedTask, subject=AgentRole.MAIN)
def test_in_auto_mode_an_agent_waiting_on_something_may_stop_with_its_task_in_hand(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until 'test -f build.done'")
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)
