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


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_at_its_first_mark_weighs_its_memories_before_it_writes_again(story):
    story.agent_consumes_context(FIRST_MARK)
    story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=FIRST_MARK)
    story.expect_stack(Void, WorkingTask, WeighingMemories)
    story.agent_writes("parser.py")
    story.expect_refused(MemoryNudges.DECISION_EDIT_BLOCK)
    story.agent_runs("memory skip 'nothing of this job needs keeping'")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_and_the_main_agent_each_list_their_own_memories_alone(story):
    story.main_agent_runs(f"memory add 'the main agent keeps the release notes' --weight {MEMORY_WEIGHT}")
    story.agent_adds_memory("the parser reads tokens left to right", MEMORY_WEIGHT)
    story.agent_runs("memory list")
    story.expect_command_text("the parser reads")
    story.expect_command_text_without("release notes")
    story.main_agent_runs("memory list")
    story.expect_command_text("release notes")
    story.expect_command_text_without("the parser reads")
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_workers_compaction_fades_its_own_memory_and_leaves_the_main_agents(story):
    story.main_agent_runs(f"memory add 'the main agent keeps the release notes' --weight {MEMORY_WEIGHT}")
    theirs = story.created_number("memory")
    own = story.agent_adds_memory("the parser reads tokens left to right", MEMORY_WEIGHT)
    story.context_is_compacted()
    story.agent_runs("memory list")
    story.expect_command_line(f"{own}", f"weight  {MEMORY_WEIGHT - 1}")
    story.main_agent_runs("memory list")
    story.expect_command_line(f"{theirs}", f"weight  {MEMORY_WEIGHT}")
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_the_main_agents_decision_at_its_mark_leaves_the_worker_weighing_its_own(story):
    story.agent_adds_memory("the parser reads tokens", MEMORY_WEIGHT)
    story.agent_consumes_context(FIRST_MARK)
    story.expect_stack(Void, WorkingTask, WeighingMemories)
    story.main_context_reaches(FIRST_MARK)
    story.main_agent_reads()
    story.main_agent_runs("memory skip 'nothing new'")
    story.expect_stack(Void, WorkingTask, WeighingMemories)
    story.agent_runs("memory skip 'nothing to keep'")
    story.agent_writes("parser.py")
    story.expect_allowed()
    story.expect_stack(Void, WorkingTask)
