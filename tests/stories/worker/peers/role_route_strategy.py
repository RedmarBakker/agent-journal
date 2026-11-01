from journal.engine.states.void import Void
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.role_peer_workers import RolePeerWorkers


@story(RolePeerWorkers, subject=AgentRole.WORKER)
@setting(OrganizationOptions.HUB_ROUTE_STRATEGY, "same_domain_peers")
def test_a_role_worker_can_send_a_job_to_an_idle_peer_in_its_domain(story):
    peer = story.agents.workers.second()
    result = story.agent_runs(story.agents.subject, f"worker send {peer} 'check the alpha change'")
    result.expect_command_passed()
    story.expect_worker(peer, state="dispatched")
    story.expect_task(story.tasks.first, title="alpha build")
    story.expect_task(story.tasks.second, title="alpha research")
    story.expect_worker(story.agents.workers.third(), role="reviewer", state="reported")
    story.expect_task(story.tasks.third, title="beta review")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(RolePeerWorkers, subject=AgentRole.WORKER)
@setting(OrganizationOptions.HUB_ROUTE_STRATEGY, "same_domain_peers")
def test_a_role_worker_cannot_send_a_job_to_a_peer_in_another_domain(story):
    peer = story.agents.workers.third()
    result = story.agent_runs(story.agents.subject, f"worker send {peer} 'check the beta review'")
    result.expect_command_refused()
    result.expect_command_text("Send it to your Domain agent, domain:alpha")
    story.expect_worker(peer, state="reported")
    story.expect_task(story.tasks.first, title="alpha build")
    story.expect_worker(story.agents.workers.second(), role="maker", state="reported")
    story.expect_task(story.tasks.second, title="alpha research")
    story.expect_task(story.tasks.third, title="beta review")
    story.expect_stack(story.agents.subject, Void, WorkingTask)
