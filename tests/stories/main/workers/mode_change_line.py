from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.support.work_mode_briefs import WorkModeBriefs
from journal.features.workers.workers_options import BUILDER_MODE, SOLO_MODE, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.solo_agent import SoloAgent


@story(SoloAgent, mode=SOLO_MODE, subject=AgentRole.MAIN)
def test_switching_to_builder_sends_the_one_mode_line_and_mode_show_prints_the_builders_brief(story):
    story.user_sets(WorkersOptions.MODE, BUILDER_MODE)
    story.expect_agent_told(story.agents.subject, PlansNudges.BUILDER_MODE)
    story.agent_runs(story.agents.subject, "mode show")
    story.expect_command_passed()
    story.expect_command_text(WorkModeBriefs.brief(BUILDER_MODE))
    story.expect_stack(story.agents.subject, Ready)
