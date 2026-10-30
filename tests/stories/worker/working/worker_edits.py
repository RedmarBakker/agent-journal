from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_workers_edit_is_recorded_on_its_own_edits_pane(story):
    story.agent_has_edited(story.agents.subject, "parser.py")
    result = story.user_opens(f"/journal/agents/{story.agent_id(story.agents.subject)}/edits")
    result.expect_viewer_rows("edits", "path", ["parser.py"])
    story.expect_stack(story.agents.subject, Void, WorkingTask)
