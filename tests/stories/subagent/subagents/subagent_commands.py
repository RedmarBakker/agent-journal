from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_files_a_plan_that_never_becomes_the_main_agents_to_follow(story):
    result = story.agent_runs(story.agents.subject, "plan create 'the shop' --brief 'the shop sells'")
    result.expect_command_passed()
    plan = story.created_number("plan")
    result = story.agent_runs(story.agents.subject, f"plan add {plan} 'the cart' --brief '- the cart holds items'")
    result.expect_command_passed()
    story.expect_stack(story.agents.main, Ready)
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_reads_the_tasks_and_the_rules(story):
    result = story.agent_runs(story.agents.subject, "task list")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "rule list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_reads_the_chat_thread_without_marking_a_message_read(story):
    result = story.agent_runs(story.agents.subject, "message list")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "message recent")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "message read 1")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_may_not_create_a_task(story):
    result = story.agent_runs(story.agents.subject, "task create 'more work'")
    result.expect_command_refused()
    story.expect_task_count(0)
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_may_not_keep_a_memory(story):
    result = story.agent_runs(story.agents.subject, "memory add 'the parser lives in parser.py' --weight 5")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_may_not_send_a_worker(story):
    result = story.agent_runs(story.agents.subject, "worker dispatch 'Mr. Babbage' --task 1 --changes 'the parser' --profile journal-medior --model sonnet")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_verb_the_subagents_file_does_not_name_is_refused_naming_the_file(story):
    result = story.agent_runs(story.agents.subject, "panic pop")
    result.expect_command_text("a subagent may not run journal panic apply: ResearcherHelper")
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagent_reads_but_may_not_run_tests_builds_or_the_commandments(story):
    story.agent_runs_in_the_shell(story.agents.subject, "grep -rn parse src").expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "python3 -m pytest tests/test_parser.py")
    result.expect_refused(story.agents.subject, WorkersNudges.SUBAGENT_COMMAND_REFUSAL)
    result = story.agent_runs_in_the_shell(story.agents.subject, ".journal/plugins/code-commandments/bin/commandments-release judge --changes")
    result.expect_refused(story.agents.subject, WorkersNudges.SUBAGENT_COMMAND_REFUSAL)
    story.expect_stack(story.agents.subject, Void, Researching)
