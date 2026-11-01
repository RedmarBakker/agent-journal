from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_a_worker_sent_one_plan_task_is_told_to_queue_the_other_open_tasks(story):
    story.tasks.third = story.user_adds_plan_task(story.plans.first, "third")
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.STARTED, delegated=False)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal worker dispatch 'Lady Lovelace' --task {story.tasks.second} --changes 'the files of its task' --profile journal-medior")
    result.expect_agent_told(story.agents.subject, WorkersNudges.QUEUE_RELATED, task=story.tasks.second, listed=str(story.tasks.third))
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
