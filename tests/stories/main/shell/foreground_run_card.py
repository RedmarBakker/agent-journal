from journal.features.shell.support.output_view import OutputView
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_watched_foreground_run_whose_card_showed_turns_its_card_to_how_it_ended(story):
    output = story.agent_has_a_watched_foreground_run(story.agents.subject, "go test ./...")
    story.foreground_run_ends(story.agents.subject, output)
    card = story.card_number(OutputView.key(output))
    story.expect_card_data(card, final=True)
    story.expect_stack(story.agents.subject, Ready)
