from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_the_user_does_not_let_release_waits_for_the_user_and_may_not_change_its_own_toggles(story):
    story.agent_runs_in_the_shell(story.agents.subject, "git tag v9.9.9")
    story.expect_refused(story.agents.subject, WorkersNudges.RELEASE_REFUSED)
    for name in ("orchestrator_writes_plans", "orchestrator_approves_plans", "orchestrator_releases"):
        story.agent_runs(story.agents.subject, f"settings set workers.{name} on")
        story.expect_command_text("the user's to set")
    story.expect_stack(story.agents.subject, Orchestrating)


@story(WorkingAgent, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_RELEASES, True)
def test_an_orchestrator_the_user_lets_release_tags_a_release(story):
    story.agent_runs_in_the_shell(story.agents.subject, "git tag v9.9.9")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Orchestrating)
