from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from journal.support.card_type import CardType
from journal.features.health.listeners.supervisor_loss_notice import LOSS_LABEL
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_supervisor_gone_without_closing_its_inbox_is_named_once_in_the_chat(story):
    story.the_supervisor_stopped_without_closing_its_inbox(story.agents.subject)
    story.clock_ticks(5)
    story.clock_ticks(5)
    story.expect_chat_marks(CardType.FAULTS, LOSS_LABEL)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_session_with_no_supervisor_announced_is_never_told_of_one(story):
    story.clock_ticks(5)
    story.expect_chat_marks(CardType.FAULTS)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_supervisor_lost_again_after_it_closed_is_named_again(story):
    story.the_supervisor_stopped_without_closing_its_inbox(story.agents.subject)
    story.clock_ticks(5)
    story.the_supervisor_closed_its_inbox(story.agents.subject)
    story.clock_ticks(5)
    story.the_supervisor_stopped_without_closing_its_inbox(story.agents.subject)
    story.clock_ticks(5)
    story.expect_chat_marks(CardType.FAULTS, LOSS_LABEL, LOSS_LABEL)
    story.expect_stack(story.agents.subject, Ready)
