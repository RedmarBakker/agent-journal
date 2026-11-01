from journal.features.tasks.states.ready import Ready
from journal.features.triggers.triggers_nudges import TriggersNudges
from journal.models.trigger_action import TriggerAction
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_trigger_that_instructs_tells_the_agent_its_text_when_the_prompt_names_one_of_its_words(story):
    story.user_creates_trigger(["deploy", "release"], "check the changelog first", TriggerAction.INSTRUCT.value)
    result = story.agent_is_prompted(story.agents.subject, "let's deploy it")
    result.expect_agent_told(story.agents.subject, TriggersNudges.INSTRUCT, title="check the changelog first")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_trigger_that_denies_refuses_a_tool_use_that_names_its_words(story):
    story.user_creates_trigger(["rm -rf"], "no recursive deletes here", TriggerAction.DENY.value)
    result = story.agent_runs_in_the_shell(story.agents.subject, "rm -rf build")
    result.expect_refused(story.agents.subject, TriggersNudges.DENIED, title="no recursive deletes here")
    story.expect_stack(story.agents.subject, Ready)
