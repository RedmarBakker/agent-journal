from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.unchecked_work_orchestrator import UncheckedWorkOrchestrator


@story(UncheckedWorkOrchestrator, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, True)
def test_with_fitness_warnings_on_unchecked_work_is_named_at_the_next_tool_use_and_not_again_within_its_repeat(story):
    story.agent_reads(story.agents.subject)
    story.expect_allowed()
    story.expect_agent_told(story.agents.subject, WorkersNudges.ORCHESTRATOR_WAIT_LINE)
    story.agent_is_quiet_for(story.agents.subject, minutes=2)
    story.agent_reads(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.ORCHESTRATOR_WAIT_LINE)
    story.expect_stack(story.agents.subject, Orchestrating)


@story(UncheckedWorkOrchestrator, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, False)
def test_with_fitness_warnings_off_the_agent_is_sent_no_fitness_line(story):
    story.agent_reads(story.agents.subject)
    story.expect_allowed()
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.ORCHESTRATOR_WAIT_LINE)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.ORCHESTRATOR_HANDOUT_LINE)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.ORCHESTRATOR_REPORT_LINE)
    story.expect_stack(story.agents.subject, Orchestrating)


@story(UncheckedWorkOrchestrator, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(FitnessOptions.WARNINGS, False)
def test_with_fitness_warnings_off_no_fitness_measure_makes_a_write_wait(story):
    story.agent_writes(story.agents.subject, "footer.py")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Orchestrating)
