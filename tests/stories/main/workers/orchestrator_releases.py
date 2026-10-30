from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_tags_a_release_only_once_the_user_lets_it_and_may_not_change_its_own_toggles(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "git tag v9.9.9")
    result.expect_refused(story.agents.subject, WorkersNudges.RELEASE_REFUSED)
    for name in ("orchestrator_writes_plans", "orchestrator_approves_plans", "orchestrator_releases"):
        result = story.agent_runs(story.agents.subject, f"settings set workers.{name} on")
        result.expect_command_text("the user's to set")
    story.user_sets(WorkersOptions.ORCHESTRATOR_RELEASES, True)
    result = story.agent_runs_in_the_shell(story.agents.subject, "git tag v9.9.9")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Orchestrating)
