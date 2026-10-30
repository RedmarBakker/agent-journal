from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_from_a_lab_report_links_to_the_report(story):
    report = story.user_writes_a_report("Lab finding", "A measured route change", "Metric and scenario evidence.")

    result = story.agent_runs(story.agents.subject, f"task create 'Trial the measured route change' --brief 'Keep the setting off by default.' --report {report}")
    result.expect_command_passed()
    task = story.task_number()
    result.expect_command_text(f"task {task} open")
    story.expect_task_made_by(story.agents.subject, task)
    story.expect_report_about_task(report, task)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_with_a_missing_report_is_refused_without_creating_a_task(story):
    result = story.agent_runs(story.agents.subject, "task create 'Orphan finding' --report 999")

    result.expect_command_refused()
    story.expect_row_count("tasks", 0)
    story.expect_stack(story.agents.subject, Ready)
