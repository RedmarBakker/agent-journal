import json

from journal.db.connection import Connection
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.faults.support.story_transitions import StoryTransitions
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.supervisor_link import SupervisorLink
from tests.agent_hooks import pinned_clock, typing_capture
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_supervisor import StorySupervisor
from tests.stories.builder.step_result import StepResult
from tests.suite_app import SuiteApp


class DeveloperSteps:
    """The runtime, supervisor and recorded path conditions a developer brings to a story."""

    def story_run_walked(self, *kinds: str) -> StepResult:
        walked_path = StoryTransitions.walked_path(self.app.config)
        walked_path.parent.mkdir(parents=True, exist_ok=True)
        walked_path.write_text(json.dumps(list(kinds)))
        return self.observed(f"the last story run walked {len(kinds)} kinds", None, None)

    def journal_restarts(self) -> StepResult:
        self.settle()
        previous = self.app
        restarted = SuiteApp(previous.config)
        restarted.original_worker_start = previous.original_worker_start
        restarted.story_clock_origin = previous.story_clock_origin
        if self.openrig is not None:
            runtime = restarted.container.get(SeatRuntime)
            self.monkeypatch.setattr(runtime, "execute", self.openrig.execute)
            self.monkeypatch.setattr(runtime, "health_request", self.openrig.health_request, raising=False)
        restarted.runtime().boot()
        restarted.runtime().deferred.start()
        self.app = self.log.app = restarted
        pinned_clock(restarted, self.monkeypatch)
        typing_capture(restarted, self.monkeypatch, self.typed)

        def close() -> None:
            restarted.runtime().deferred.stop()
            restarted.container.get(Connection).close()

        self.closers.append(close)
        return self.observed("the journal boots again from its persisted rows", None, None)

    def organization_seat_has_no_native_session(self, plan: int, identity: str) -> StepResult:
        runtime = self.app.container.get(SeatRuntime)
        member = runtime.organization_member(self.plan_rig_name(plan), identity, self.provider)
        self.simulated_seats().sessions[member.target].pop("sessionId")
        return self.observed(f"the {identity} seat has a process but no native session ID", None, None)

    def agent_supervisor_accepts_lines(self, agent: StoryAgent) -> StepResult:
        row = self.app.container.get(Agents).session_agent(self.session_of(agent))
        environment = self.app.container.get(Environments).find(row.environment_id).name
        self.protocol_supervisor = StorySupervisor(self.app.config.home, environment, self.typed)
        self.closers.append(self.protocol_supervisor.close)
        self.monkeypatch.setattr(SupervisorLink, "_send", self.supervisor_send)
        return self.observed(f"the {agent.role} supervisor accepts terminal lines", None, None)

    def agent_supervisor_refuses_lines(self, agent: StoryAgent) -> StepResult:
        self.protocol_supervisor.refuse()
        return self.observed(f"the {agent.role} supervisor refuses terminal lines", None, None)

    def agent_supervisor_is_ready(self, agent: StoryAgent) -> StepResult:
        self.protocol_supervisor.accept()
        return self.observed(f"the {agent.role} supervisor is ready again", None, None)
