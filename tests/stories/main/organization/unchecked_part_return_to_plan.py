from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_part_returned_unchecked import OrganizationPartReturnedUnchecked


@story(OrganizationPartReturnedUnchecked, subject=AgentRole.MAIN)
def test_the_plan_parts_list_names_an_unchecked_return(story):
    part, worker = story.tasks.second_part, story.agents.workers.second()
    listed = story.agent_runs_as_organization_seat(
        story.agents.main, "plan", f"organization parts {story.tasks.first}",
    )
    listed.expect_command_passed()
    listed.expect_command_text(
        f"task {part} started, plan, unchecked return from worker {worker.number}; "
        f"run `journal worker check {worker.number} <point>` first",
    )
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
