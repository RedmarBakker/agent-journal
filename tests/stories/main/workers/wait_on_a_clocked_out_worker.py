from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_wait_on_a_worker_that_already_clocked_out_is_answered_at_once_with_the_task_to_check(story):
    result = story.agent_runs(story.agents.subject, f"worker wait {story.agents.workers.first()}")
    result.expect_command_text(f"worker {story.agents.workers.first()}, Lady Lovelace, already clocked out: task {story.tasks.briefed} is ready to check")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_second_clock_out_after_a_point_came_back_short_is_told_as_the_first_and_counts_as_ready_again(story):
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1")
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 2 --short 'the alias names are missing'")
    story.agent_proves(story.agents.workers.first(), 2, "parser.py:31, the alias names are in")
    result = story.agent_clocks_out(story.agents.workers.first(), "the alias names are in")
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    result = story.agent_runs(story.agents.subject, f"worker wait {story.agents.workers.first()}")
    result.expect_command_text(f"task {story.tasks.briefed} is ready to check")
    story.expect_stack(story.agents.subject, Ready)
