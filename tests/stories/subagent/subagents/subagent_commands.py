from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_files_a_plan_that_never_becomes_the_main_agents_to_follow(story):
    story.agent_runs("plan create 'the shop' --brief 'the shop sells'")
    story.expect_command_passed()
    plan = story.created_number("plan")
    story.agent_runs(f"plan add {plan} 'the cart' --brief '- the cart holds items'")
    story.expect_command_passed()
    story.expect_main_stack(Ready)
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_reads_the_tasks_and_the_rules(story):
    story.agent_runs("task list")
    story.expect_command_passed()
    story.agent_runs("rule list")
    story.expect_command_passed()
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_may_not_create_a_task(story):
    story.agent_runs("task create 'more work'")
    story.expect_command_refused()
    story.expect_task_count(0)
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_may_not_keep_a_memory(story):
    story.agent_runs("memory add 'the parser lives in parser.py' --weight 5")
    story.expect_command_refused()
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_may_not_send_a_worker(story):
    story.agent_runs("worker dispatch 'Mr. Babbage' --task 1 --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_verb_the_subagents_file_does_not_name_is_refused_naming_the_file(story):
    story.agent_runs("panic pop")
    story.expect_command_text("a subagent may not run journal panic apply: ResearcherHelper")
    story.expect_stack(Void, Researching)
