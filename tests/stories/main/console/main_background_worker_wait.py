from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

SUBAGENT = "sub1"


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_main_background_worker_wait_is_not_taken_for_a_researcher(story):
    worker = story.agents.workers.first()
    story.agent_sends_subagent(story.agents.subject, RESEARCHER, "look at the worker queue")
    story.subagent_starts(SUBAGENT, RESEARCHER)
    story.subagent_runs_in_the_shell(SUBAGENT, f"journal worker wait {worker}")

    result = story.agent_runs_in_its_own_background(story.agents.subject, f"journal worker wait {worker} && journal worker list")
    result.expect_allowed()

    result = story.command_from_a_shell(f"worker wait {worker}", {}, {"agent": True, "provider": story.provider, "session": story.main_session()})
    result.expect_command_passed()
    result.expect_command_text("already clocked out")
    story.expect_stack(story.agents.subject, Ready)
