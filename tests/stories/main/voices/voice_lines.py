from journal.engine.states.ended import Ended
from journal.features.tasks.states.ready import Ready
from journal.features.voices.voices_nudges import VoicesNudges
from journal.features.voices.voices_options import VoicesOptions
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_session import EndedSession
from tests.stories.fixtures.main.working_agent import WorkingAgent



@story(EndedSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_voice_is_told_at_a_session_start_with_the_title_and_name_the_user_set(story):
    story.user_sets(VoicesOptions.TITLE, "Captain")
    story.user_sets(VoicesOptions.NAME, "Example")
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, VoicesNudges.VOICE_INSTRUCTION)
    story.expect_answer_text('Address me as "Captain Example"')
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_voice_chosen_by_the_user_is_typed_to_the_agent_whole(story):
    story.user_posted("/journal/voices/choose", {"name": "squire"})
    story.expect_typed_nudge(VoicesNudges.VOICE_CHANGE)
    story.expect_typed_text('Address me as "my liege"')
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_change_of_the_title_types_the_voice_once(story):
    story.user_sets(VoicesOptions.TITLE, "Captain")
    story.expect_typed_nudge(VoicesNudges.VOICE_CHANGE)
    story.expect_stack(story.agents.subject, Ready)
