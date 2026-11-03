from journal.features.tasks.states.ready import Ready
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.worker_state import WorkerState
from journal.repositories.agents import Agents
from journal.repositories.links import Links
from journal.repositories.scope import Scope
from journal.repositories.tasks import CURRENT_TASK_LINK, Tasks
from journal.support.actor import Actor
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.working_worker import WorkingWorker


class ReleasedWorkerTaskInHand(StateFixture):
    """A task blocked after its worker was released retains a stale delegation flag and the main agent's current-task link."""

    parent = WorkingWorker
    stack = (Ready,)

    def steps(self, story) -> None:
        task = story.tasks.briefed
        story.user_blocks_task(task, "question 50").expect_viewer_passed()
        agents = story.app.container.get(Agents)
        agent = agents.session_agent(story.main_session())
        scope = story.app.container.get(Scope)
        with scope.environment(agent.environment_id):
            tasks = story.app.container.get(Tasks)
            current = tasks.find(task)
            tasks.save(current.with_(delegated=True), Actor.system())
            story.app.container.get(Links).save(
                Link(source=Ref.build(agent), target=Ref.build(current), link_type=CURRENT_TASK_LINK),
                Actor.system(),
            )

    def expected(self, story) -> None:
        story.expect_task(story.tasks.briefed, delegated=True)
        story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
        story.expect_stack(story.agents.main, Ready)
