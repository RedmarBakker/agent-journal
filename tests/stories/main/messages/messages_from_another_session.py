from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SENDER = "code-commandments-12"


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_every_hook_is_answered_while_a_message_from_another_session_crosses_in_the_transcript_and_both_ways_reach_the_chat(story):
    story.another_session_sends(story.agents.subject, SENDER, "the fix is on main")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result = story.agent_writes(story.agents.subject, "b.py")
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "ls")
    result.expect_allowed()
    story.expect_chat_holds("the fix is on main")
    story.agent_messages_subagent(story.agents.subject, SENDER, "noted")
    story.expect_chat_holds("noted")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_another_agents_question_is_named_at_the_stop_until_the_agent_sends_it_an_answer(story):
    story.another_session_sends(story.agents.subject, SENDER, "the fix is on main.\nDoes your suite pass on it?")
    story.agent_reads(story.agents.subject)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, MessagesNudges.PEER_QUESTION, sender=SENDER)
    story.agent_messages_subagent(story.agents.subject, SENDER, "it passes")
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.PEER_QUESTION)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_message_from_another_agent_that_asks_nothing_owes_no_answer(story):
    story.another_session_sends(story.agents.subject, SENDER, "the fix is on main")
    story.agent_reads(story.agents.subject)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.PEER_QUESTION)
    story.expect_stack(story.agents.subject, Ready)
