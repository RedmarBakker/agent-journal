import json

from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

NONE_LEFT = json.dumps({"count": "tasks", "where": {"state": ["open", "started", "blocked"]}, "is": 0})


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reminder_on_a_moment_waits_for_its_condition_and_a_single_use_one_is_struck_once_told(story):
    story.user_types(f"reminder create 'release 4.48.0' --on task_completed --when '{NONE_LEFT}' --once")
    reminder = story.created_number("reminder")
    story.user_types("rule create 'Always write the changelog per task' --on task_completed --reason 'every task names its change'")
    rule = story.created_number("rule")
    parser, printer = story.agent_creates_task(story.agents.subject, "the parser"), story.agent_creates_task(story.agents.subject, "the printer")
    result = story.agent_runs(story.agents.subject, f"task complete {parser} --how done")
    result.expect_agent_told(story.agents.subject, MemoryNudges.MEMORY_TRIGGERED, noun="rule", n=rule)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.MEMORY_TRIGGERED, noun="reminder", n=reminder)
    result = story.agent_runs(story.agents.subject, f"task complete {printer} --how done")
    result.expect_agent_told(story.agents.subject, MemoryNudges.MEMORY_TRIGGERED, noun="reminder", n=reminder)
    result = story.agent_runs(story.agents.subject, "reminder list")
    result.expect_command_text_without("release 4.48.0")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reminder_set_for_a_moment_is_quiet_before_it_and_told_once_after_it_then_struck(story):
    story.user_types(f"reminder create 'water the plants' --at '{story.local_moment(minutes=120)}'")
    story.user_types(f"reminder create 'call the plumber' --at '{story.local_moment(minutes=-5)}'")
    result = story.user_types("reminder create x --at tomorrow")
    result.expect_command_text("--at takes a local date and time")
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_told(story.agents.subject, MemoryNudges.REMINDER_DUE, text="call the plumber")
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.REMINDER_DUE, text="water the plants")
    result = story.agent_runs(story.agents.subject, "reminder list")
    result.expect_command_text_without("call the plumber")
    result.expect_command_text("water the plants")
    story.expect_stack(story.agents.subject, Ready)
