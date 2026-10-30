from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

WEIGHT = 6


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_weighing_a_memory_lower_is_refused_naming_its_weight_while_keeping_and_raising_pass(story):
    story.agent_runs(story.agents.subject, f"memory add 'the parser reads left to right' --weight {WEIGHT}")
    memory = story.created_number("memory")
    story.agent_runs(story.agents.subject, f"memory weigh {memory} {WEIGHT - 1}")
    story.expect_command_refused()
    story.agent_runs(story.agents.subject, f"memory weigh {memory} {WEIGHT}")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, f"memory weigh {memory} {WEIGHT + 1}")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, "memory list")
    story.expect_command_line(f"{memory}", f"weight  {WEIGHT + 1}")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_memory_that_is_mostly_true_is_corrected_in_place_and_keeps_its_weight(story):
    story.agent_runs(story.agents.subject, f"memory add 'the parser reads right to left' --weight {WEIGHT}")
    memory = story.created_number("memory")
    story.agent_runs(story.agents.subject, f"memory edit {memory} 'the parser reads left to right'")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, "memory list")
    story.expect_command_line(f"{memory}", f"weight  {WEIGHT}", "left to right")
    story.expect_command_text_without("right to left")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_memory_tied_to_a_task_stays_until_the_first_compaction_after_the_task_is_completed_and_a_compaction_lowers_the_others_by_one(story):
    task = story.agent_creates_task(story.agents.subject, "the parser")
    story.agent_runs(story.agents.subject, f"memory add 'the parser task needs the old grammar' --weight {WEIGHT} --for task:{task}")
    tied = story.created_number("memory")
    story.agent_runs(story.agents.subject, f"memory add 'the grammar file lives in docs' --weight {WEIGHT}")
    kept = story.created_number("memory")
    story.context_is_compacted()
    story.agent_runs(story.agents.subject, "memory list")
    story.expect_command_line(f"{tied}", f"weight  {WEIGHT - 1}")
    story.agent_runs(story.agents.subject, f"task complete {task} --how done")
    story.agent_runs(story.agents.subject, "memory list")
    story.expect_command_line(f"{tied}", "the parser task")
    story.context_is_compacted()
    story.agent_runs(story.agents.subject, "memory list")
    story.expect_command_text_without("the parser task")
    story.expect_command_line(f"{kept}", f"weight  {WEIGHT - 2}")
    story.expect_stack(story.agents.subject, Ready)
