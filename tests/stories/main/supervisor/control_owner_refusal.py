from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_other_owner_feedback import SupervisorOtherOwnerFeedback


@story(SupervisorOtherOwnerFeedback, subject=AgentRole.MAIN)
def test_a_person_who_does_not_own_the_grant_is_refused_control(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    environment = story.app.container.get(Environments).find(plan.environment_id).name
    result = story.user_opens_in(environment, "/journal/supervisor/control")
    result.expect_viewer_refused("Only the owner can change the supervisor.")
    story.expect_stack(story.agents.subject, Ready)
