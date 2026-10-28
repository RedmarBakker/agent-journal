from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_report_about_rows_apart_by_commas_or_by_spaces_links_each(story):
    first, second = story.user_creates_plan("one", "b"), story.user_creates_plan("two", "b")
    story.agent_runs(f"report create Both --abstract 'What it says' --body words --about plans:{first},plans:{second}")
    story.expect_command_text(f"about plans:{first}, plans:{second}")
    story.agent_runs(f"report create 'Both again' --abstract 'What it says' --body words --about plans:{first} plans:{second}")
    story.expect_command_text(f"about plans:{first}, plans:{second}")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_report_about_a_row_it_cannot_read_is_refused_by_name(story):
    plan = story.user_creates_plan("one", "b")
    story.agent_runs(f"report create Wrong --abstract 'What it says' --body words --about 'plans:{plan},the second plan'")
    story.expect_command_refused()
    story.expect_command_text("not a row: the second plan")
    story.expect_stack(Ready)
