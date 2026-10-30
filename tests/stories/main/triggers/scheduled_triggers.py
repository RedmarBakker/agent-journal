from journal.features.tasks.states.ready import Ready
from journal.features.triggers.triggers_nudges import TriggersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

CHECK = "check the import errors in Sentry"
MINUTE_SECONDS = 60


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_trigger_set_for_a_time_tells_the_agent_its_line_once_when_the_clock_passes_it(story):
    result = story.agent_runs(story.agents.subject, f"trigger schedule '{CHECK}' --at '{story.local_time_after(30)}' --do instruct")
    result.expect_command_passed()
    result = story.clock_ticks(10 * MINUTE_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TriggersNudges.INSTRUCT)
    result = story.clock_ticks(25 * MINUTE_SECONDS)
    result.expect_agent_told(story.agents.subject, TriggersNudges.INSTRUCT, title=CHECK)
    result = story.clock_ticks(20 * MINUTE_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TriggersNudges.INSTRUCT)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_trigger_every_so_many_minutes_tells_its_line_each_time_and_stops_after_its_times(story):
    story.agent_runs(story.agents.subject, f"trigger schedule '{CHECK}' --every 20 --times 2")
    result = story.clock_ticks(20 * MINUTE_SECONDS)
    result.expect_agent_told(story.agents.subject, TriggersNudges.NUDGE, title=CHECK)
    result = story.clock_ticks(20 * MINUTE_SECONDS)
    result.expect_agent_told(story.agents.subject, TriggersNudges.NUDGE, title=CHECK)
    result = story.clock_ticks(20 * MINUTE_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TriggersNudges.NUDGE)
    result = story.agent_runs(story.agents.subject, "trigger list")
    result.expect_command_text_without(CHECK)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_trigger_on_a_cron_line_tells_its_line_at_each_time_it_names_until_its_end(story):
    story.agent_runs(story.agents.subject, f"trigger schedule '{CHECK}' --cron '*/30 * * * *' --until '{story.local_time_after(45)}'")
    result = story.agent_runs(story.agents.subject, "trigger list")
    result.expect_command_text("next at")
    result = story.clock_ticks(30 * MINUTE_SECONDS)
    result.expect_agent_told(story.agents.subject, TriggersNudges.NUDGE, title=CHECK)
    result = story.clock_ticks(30 * MINUTE_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TriggersNudges.NUDGE)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_trigger_for_a_time_already_past_or_with_no_time_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"trigger schedule '{CHECK}' --at '{story.local_time_after(-60)}'")
    result.expect_command_refused()
    result.expect_command_text("already past")
    result = story.agent_runs(story.agents.subject, f"trigger schedule '{CHECK}'")
    result.expect_command_refused()
    result.expect_command_text("--at, --every or --cron")
    story.expect_stack(story.agents.subject, Ready)
