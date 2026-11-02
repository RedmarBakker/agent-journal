from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.phases import PHASE_TASK_LINK, Phases
from journal.repositories.plans import PHASE_LINK, PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_observations import enrolled, seeded, stored_run


class SupervisorEnvironmentObservation(SupervisorGrantFixture):
    """A supervisor grant watches one of two plans in its environment."""

    parent = NewSession

    def steps(self, story) -> None:
        self.restore_on(story)
        fixture = seeded(story.app, owner_id=71)
        grant, token, principal = enrolled(fixture)
        run = stored_run(story.app, grant, run_ref="environment-observation-story",
            epoch=principal.scope["installation_epoch"])
        actor = fixture["owner"]
        scope = story.app.container.get(Scope)
        plans = story.app.container.get(Plans)
        links = story.app.container.get(Links)
        with scope.environment(fixture["driver_environment"].row_id):
            unwatched = plans.save(Plan(
                environment_id=fixture["driver_environment"].row_id,
                title="unwatched plan", brief="keep another service healthy",
                state=PlanState.STARTED, mode=PlanMode.SOLO,
            ), actor)
            phase = story.app.container.get(Phases).save(Phase(
                environment_id=fixture["driver_environment"].row_id,
                title="unwatched phase", completion_rule="its work is complete",
            ), actor)
            task = story.app.container.get(Tasks).save(Task(
                environment_id=fixture["driver_environment"].row_id,
                title="unwatched task", brief="Inspect another service",
            ), actor)
            links.linked(Ref.build(phase), Ref.build(unwatched), PHASE_TASK_LINK, actor)
            links.linked(Ref.build(task), Ref.build(phase), PHASE_LINK, actor)
            links.linked(Ref.build(task), Ref.build(unwatched), PLAN_LINK, actor)
        self.supervisor_environment = fixture["owner_environment"].name
        self.supervisor_credential = token
        self.observed_plan = fixture["plan"].row_id
        self.run_request = {
            "protocol_version": 1,
            "run_id": run.data["run_ref"],
            "installation_epoch": run.data["installation_epoch"],
            "fence": run.data["fence"],
            "cursor": None,
        }
        story.plans.first = fixture["plan"].row_id
        story.plans.second = unwatched.row_id
        story.closers.append(lambda: fixture["authority"].secrets_store.drop(fixture["credentials"]))
        opened = story.user_opens_in(self.supervisor_environment, "/journal/plans")
        opened.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.subject)
