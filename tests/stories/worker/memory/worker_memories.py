from journal.engine.states.void import Void
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker

FIRST_MARK = MemoryThresholds.CONTEXT[0]
MEMORY_WEIGHT = 5


@story(WorkingWorker, mode=BUILDER_MODE)
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
