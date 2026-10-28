from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession

FIRING = "f-1"


@story(NewSession, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_hook_sent_twice_is_answered_the_same_and_moves_nothing_the_second_time(story):
    story.agent_writes_in_one_firing("footer.py", FIRING)
    story.expect_refused(BriefingNudges.OVERVIEW_REQUEST)
    story.agent_writes_in_one_firing("footer.py", FIRING)
    story.expect_refused_by_anything()
    story.expect_refusal_text(BriefingNudges.OVERVIEW_REQUEST.title)
    story.expect_agent_told_nothing()
    story.expect_one_entry_of_firing(FIRING)
    story.expect_stack(Ready)
