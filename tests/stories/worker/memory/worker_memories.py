from journal.engine.states.void import Void
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker

FIRST_MARK = MemoryThresholds.CONTEXT[0]
MEMORY_WEIGHT = 5


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_at_its_first_mark_weighs_its_memories_before_it_writes_again(story):
    result = story.agent_consumes_context(story.agents.subject, FIRST_MARK)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=FIRST_MARK)
    story.expect_stack(story.agents.subject, Void, WorkingTask, WeighingMemories)
    result = story.agent_writes(story.agents.subject, "parser.py")
    result.expect_refused(story.agents.subject, MemoryNudges.DECISION_EDIT_BLOCK)
    result = story.agent_runs(story.agents.subject, "memory skip 'nothing of this job needs keeping'")
    result.expect_command_passed()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_and_the_main_agent_each_list_their_own_memories_alone(story):
    story.agent_runs(story.agents.main, f"memory add 'the main agent keeps the release notes' --weight {MEMORY_WEIGHT}")
    story.agent_adds_memory(story.agents.subject, "the parser reads tokens left to right", MEMORY_WEIGHT)
    result = story.agent_runs(story.agents.subject, "memory list")
    result.expect_command_text("the parser reads")
    result.expect_command_text_without("release notes")
    result = story.agent_runs(story.agents.main, "memory list")
    result.expect_command_text("release notes")
    result.expect_command_text_without("the parser reads")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_workers_compaction_fades_its_own_memory_and_leaves_the_main_agents(story):
    story.agent_runs(story.agents.main, f"memory add 'the main agent keeps the release notes' --weight {MEMORY_WEIGHT}")
    theirs = story.created_number("memory")
    own = story.agent_adds_memory(story.agents.subject, "the parser reads tokens left to right", MEMORY_WEIGHT)
    story.context_is_compacted()
    result = story.agent_runs(story.agents.subject, "memory list")
    result.expect_command_line(f"{own}", f"weight  {MEMORY_WEIGHT - 1}")
    result = story.agent_runs(story.agents.main, "memory list")
    result.expect_command_line(f"{theirs}", f"weight  {MEMORY_WEIGHT}")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_the_main_agents_decision_at_its_mark_leaves_the_worker_weighing_its_own(story):
    story.agent_adds_memory(story.agents.subject, "the parser reads tokens", MEMORY_WEIGHT)
    story.agent_consumes_context(story.agents.subject, FIRST_MARK)
    story.expect_stack(story.agents.subject, Void, WorkingTask, WeighingMemories)
    story.main_context_reaches(FIRST_MARK)
    story.agent_reads(story.agents.main)
    story.agent_runs(story.agents.main, "memory skip 'nothing new'")
    story.expect_stack(story.agents.subject, Void, WorkingTask, WeighingMemories)
    story.agent_runs(story.agents.subject, "memory skip 'nothing to keep'")
    result = story.agent_writes(story.agents.subject, "parser.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_sent_its_next_job_is_shown_its_own_memories_at_clock_in_and_never_the_main_agents(story):
    story.agent_runs(story.agents.main, f"memory add 'the main agent keeps the release notes' --weight {MEMORY_WEIGHT}")
    story.agent_runs(story.agents.subject, f"memory add 'the parser reads tokens left to right' --weight {MEMORY_WEIGHT}")
    own = story.created_number("memory")
    story.agent_proves(story.agents.subject, 1, "parser.py:12, test_reads passes")
    story.agent_proves(story.agents.subject, 2, "parser.py:30, test_names passes")
    story.agent_clocks_out(story.agents.subject, "the parser is done")
    story.worker_run_ends_with_its_session(story.agents.subject, "the parser is done")
    story.agent_runs(story.agents.main, f"worker send {story.agents.subject} 'now the error messages'")
    story.agent_resumes_the_session(story.agents.subject)
    story.agent_clocks_in(story.agents.subject)
    result = story.agent_has_run_printing(story.agents.subject, "journal clock-in", "")
    result.expect_agent_told(story.agents.subject, MemoryNudges.WORKER_MEMORIES, memories=f"{own} (weight {MEMORY_WEIGHT}) the parser reads tokens left to right")
    story.expect_answer_text("the parser reads")
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
