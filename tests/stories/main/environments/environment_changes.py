from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_deleting_an_environment_takes_everything_recorded_in_it_and_leaves_the_others(story):
    spike = story.another_environment("spike")
    story.user_creates_plan_in(spike, "a spike")
    kept = story.agent_creates_task(story.agents.subject, "kept")
    result = story.agent_runs(story.agents.subject, f"environment delete {spike}")
    result.expect_command_text("deleted environment")
    result = story.agent_runs(story.agents.subject, "environment list")
    result.expect_command_text_without(spike)
    story.expect_task(kept, state=TaskState.OPEN)
    result = story.agent_runs(story.agents.subject, f"environment delete {spike}")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_environment_renamed_carries_its_rows_and_never_takes_a_name_in_use(story):
    spike = story.another_environment("spike")
    story.user_creates_plan_in(spike, "a spike")
    result = story.agent_runs(story.agents.subject, f"environment rename {spike} main")
    result.expect_command_text("exists already")
    result = story.agent_runs(story.agents.subject, f"environment rename {spike} probe")
    result.expect_command_passed()
    story.expect_plan_titles_in("probe", "a spike")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_environment_is_never_renamed_while_an_agent_works_there(story):
    spike = story.another_environment("spike")
    story.session_starts_in(spike, "s-spike")
    result = story.agent_runs(story.agents.subject, f"environment rename {spike} probe")
    result.expect_command_text(f"an agent works in {spike}")
    story.expect_stack(story.agents.subject, Ready)
