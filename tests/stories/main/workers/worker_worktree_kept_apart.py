from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER
from tests.stories.fixtures.worker.worktree_worker import WorktreeWorker

SUBAGENT = "a1"


@story(WorktreeWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agent_stays_out_of_a_workers_worktree_and_is_told_how_to_work_there_while_a_subagent_is_not_held(story):
    worker = story.agents.workers.first()
    inside = story.app.config.home / "worktrees" / f"{worker}-Lady-Lovelace" / "parser.py"
    story.agent_writes(story.agents.subject, str(inside))
    story.expect_refusal_text("that file is in worker")
    story.expect_refusal_text(f"journal worker send {worker}")
    story.subagent_starts(SUBAGENT, RESEARCHER)
    story.subagent_writes(SUBAGENT, str(inside))
    story.expect_allowed()
    story.agent_writes(story.agents.subject, str(story.app.config.root / "elsewhere.py"))
    story.expect_allowed()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready)
