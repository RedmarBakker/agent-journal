from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_each_task_names_the_plan_it_is_in_so_the_tasks_list_leaves_it_to_its_plan(story):
    loose = story.agent_creates_task("loose")
    plan = story.agent_creates_plan("the release", "ship it")
    planned = story.agent_adds_plan_task(plan, "planned")
    story.expect_task(loose, plan_id=None)
    story.expect_task(planned, plan_id=plan)
    story.expect_stack(Ready, FollowingSequence)
