from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_reading_a_message_names_its_file_and_how_to_caption_it_and_then_its_caption(story):
    message = story.user_sends_message("see the picture")
    story.user_attaches_file(message, "shot one.png", b"PNG")
    story.agent_runs(f"message read {message}")
    story.expect_command_text("shot one.png")
    story.expect_command_text(f'`journal message tag {message} "shot one.png"')
    story.expect_command_text_without("something to do? file it")
    story.agent_runs(f"message tag {message} 'shot one.png' 'the footer overlapping the form'")
    story.agent_runs(f"message read {message}")
    story.expect_command_text("the footer overlapping the form")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_reading_a_message_the_user_reacted_to_names_the_reaction(story):
    message = story.user_sends_message("see the picture")
    story.user_reacts(message, "👍")
    story.agent_runs(f"message read {message}")
    story.expect_command_text("reacts")
    story.expect_stack(Ready)
