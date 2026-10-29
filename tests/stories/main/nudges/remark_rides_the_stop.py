from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.context_mark_task import ContextMarkTask
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent

EM_DASHES = "The build — the one from last night — is green."


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_waiting_when_the_agent_stops_holds_that_stop_once_and_the_next_stop_goes_through(story):
    story.agent_closes_its_turn(story.agents.subject, "I ran journal task start 3 because the user wants it.")
    story.agent_stops(story.agents.subject)
    story.expect_refused_by_anything()
    story.expect_last_answer_carries(EtiquetteNudges.SHOP_TALK_WARNING)
    story.expect_last_answer_carries(EtiquetteNudges.SECOND_PERSON)
    story.agent_stops_again(story.agents.subject)
    story.expect_allowed()
    story.expect_last_answer_without(EtiquetteNudges.SHOP_TALK_WARNING)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_rides_a_stop_refused_for_the_task_in_hand_beside_the_refusal(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_task(story.tasks.started, state="started")
    story.expect_stack(story.agents.subject, Ready, Working)


@story(BuildWait, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_rides_a_stop_made_while_the_agent_waits(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_rides_a_stop_made_while_a_sequence_runs(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_row("sequences", story.sequences.first, {})
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(ContextMarkTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_rides_the_stop_held_at_a_context_mark_beside_its_hold(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, MemoryNudges.UNDECIDED_STOP)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)
