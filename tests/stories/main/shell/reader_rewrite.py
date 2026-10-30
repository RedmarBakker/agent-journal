from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reader_written_anew_keeps_every_setting_a_flag_leaves_out_and_a_new_one_needs_what_it_selects(story):
    story.agent_runs(story.agents.subject, r"reader add unit-runs --pattern '[0-9]+ passed' --about 'the summary of a unit run' --label 'Running tests' --commands pytest")
    story.agent_runs(story.agents.subject, "reader add unit-runs --pattern '[0-9]+ (passed|failed)'")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, "reader list")
    story.expect_command_text("the summary of a unit run")
    story.agent_runs(story.agents.subject, "reader add fresh-one --pattern x")
    story.expect_command_refused()
    story.expect_command_text("--about")
    story.expect_stack(story.agents.subject, Ready)
