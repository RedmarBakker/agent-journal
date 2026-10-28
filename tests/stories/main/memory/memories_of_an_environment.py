from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

WEIGHT = 5


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_two_environments_memories_never_mix_and_one_from_another_cannot_be_weighed_here(story):
    other = story.another_environment("other")
    story.agent_adds_memory("the main project ships on fridays", WEIGHT)
    story.session_starts_in(other, "s-other")
    story.agent_in_runs(other, "s-other", "memory add 'the other project ships on mondays' --weight 5")
    theirs = story.created_number("memory")
    story.agent_runs("memory list")
    story.expect_command_text("fridays")
    story.expect_command_text_without("mondays")
    story.agent_runs(f"memory weigh {theirs} 3")
    story.expect_command_refused()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_subagents_compaction_fades_no_memory_and_the_main_agents_fades_its_own(story):
    memory = story.agent_adds_memory("the main project ships on fridays", WEIGHT)
    story.subagent_compaction_begins("sub-1")
    story.agent_runs("memory list")
    story.expect_command_line(f"{memory}", f"weight  {WEIGHT}")
    story.compaction_begins()
    story.compacted_session_starts()
    story.agent_runs("memory list")
    story.expect_command_line(f"{memory}", f"weight  {WEIGHT - 1}")
    story.expect_stack(Ready)
