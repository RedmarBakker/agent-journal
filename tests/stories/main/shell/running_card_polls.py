from journal.features.shell.support.output_view import OutputView
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MIGRATION = "./scripts/migrate.sh"
STEPS_READER = "reader add steps --pattern 'migrated' --progress '(\\d+)/(\\d+)' --about 'the migration steps'"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_viewers_poll_of_a_running_card_shows_the_stored_card_and_never_reads_the_run_itself(story):
    story.agent_runs(story.agents.subject, STEPS_READER)
    run = story.agent_has_a_background_run_printing(story.agents.subject, MIGRATION, "migrated 1/4")
    story.agent_runs(story.agents.subject, f"output watch {run} --reader steps")
    story.running_commands_are_read_again(1)
    card = story.card_number(OutputView.key(run))
    story.background_run_prints(run, "migrated 2/4")
    result = story.user_opens(f"/journal/cards/active?ids={card}")
    result.expect_viewer_part((str(card), "fraction"), 0.25)
    story.running_commands_are_read_again(1)
    result = story.user_opens(f"/journal/cards/active?ids={card}")
    result.expect_viewer_part((str(card), "fraction"), 0.5)
    story.background_run_ends(story.agents.subject, run)
    story.expect_stack(story.agents.subject, Ready)
