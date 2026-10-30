from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_added_with_its_phase_lands_in_that_phase_at_once(story):
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'the contact page' --brief 'the page shows the address' --phase 2")
    result.expect_command_passed()
    result.expect_command_text("phase 2")
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_lines_in_order("phase 2", "the about page", "the contact page")
    story.expect_task(story.tasks.first_phase, state=TaskState.STARTED)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_added_to_a_phase_the_plan_lacks_is_refused_and_not_made(story):
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'the contact page' --phase 9")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_text_without("the contact page")
    story.expect_task(story.tasks.first_phase, state=TaskState.STARTED)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
