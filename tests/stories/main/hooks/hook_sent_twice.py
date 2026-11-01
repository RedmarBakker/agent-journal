from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession

FIRING = "f-1"


@story(NewSession, subject=AgentRole.MAIN)
def test_a_hook_sent_twice_is_answered_the_same_and_moves_nothing_the_second_time(story):
    result = story.agent_writes_in_one_firing(story.agents.subject, "footer.py", FIRING)
    result.expect_refused(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    result = story.agent_writes_in_one_firing(story.agents.subject, "footer.py", FIRING)
    result.expect_refused_by_anything()
    result.expect_refusal_text(BriefingNudges.OVERVIEW_REQUEST.title)
    result.expect_agent_told_nothing(story.agents.subject)
    story.expect_one_entry_of_firing(FIRING)
    story.expect_stack(story.agents.subject, Ready)
