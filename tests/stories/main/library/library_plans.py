from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan

PLAN_NAME = "the-site"


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_published_to_the_library_imports_as_a_draft_with_its_phases_and_task_titles_every_task_open_and_the_original_as_it_was(story):
    story.user_connects_to_a_team()
    result = story.user_types(f"library publish plan {story.plans.first} --note 'the site in two phases'")
    result.expect_command_passed()
    result = story.user_types(f"library import plan {PLAN_NAME}")
    result.expect_command_passed()
    copy = story.created_number("plan")
    result = story.user_types(f"plan show {copy}")
    result.expect_command_text("draft")
    result.expect_command_text("Layout")
    result.expect_command_text("Content")
    result.expect_command_text("the grid")
    result.expect_command_text("the about page")
    result.expect_command_text_without("started")
    result = story.user_types(f"library update plan {PLAN_NAME}")
    result.expect_command_refused()
    story.expect_task(story.tasks.first_phase, state=TaskState.STARTED)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
