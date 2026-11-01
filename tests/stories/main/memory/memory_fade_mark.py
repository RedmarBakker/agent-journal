from journal.engine.states.compacting import Compacting
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_compaction_mark_counts_the_removed_memories_in_its_total(story):
    for words in ("the parser reads left to right", "the printer runs after the parser", "the header is a draft"):
        story.agent_runs(story.agents.subject, f"memory add '{words}' --weight 5")
    story.agent_runs(story.agents.subject, f"memory remove {story.created_number('memory')}")
    story.compaction_begins()
    story.expect_recent_message_text("Memories faded by one: 2 of 3 still shown")
    story.expect_stack(story.agents.subject, Ready, Compacting)
