from journal.features.tasks.states.ready import Ready
from journal.features.voices.support.builtin_catalogue import BuiltinCatalogue
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage

FACES = [face for voice in BuiltinCatalogue.ALL for face in voice.emoji.split()]


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_every_built_in_voice_can_put_each_of_its_own_faces_on_a_message(story):
    for face in FACES:
        story.agent_reacts(story.start.message, face)
        story.expect_command_text(f"{face} on message {story.start.message}")
    story.expect_stack(Ready)
