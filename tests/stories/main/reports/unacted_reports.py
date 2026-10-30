from journal.features.reports.reports_nudges import ReportsNudges
from journal.features.reports.reports_options import ReportsOptions
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

REPEAT_MINUTES = 41


@story(WorkingAgent, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_a_report_never_acted_on_is_named_to_the_orchestrator_again_until_it_is_settled(story):
    reports = []
    for title in ("What the login check found", "The payment notes", "The cache survey"):
        story.agent_runs(story.agents.subject, f"report create '{title}' --abstract 'What it says, in one line' --body 'Something.'")
        reports.append(story.created_number("report"))
    unread, planned, tasked = reports
    story.agent_creates_briefed_task(story.agents.subject, "release", f"built on report {planned}")
    story.agent_creates_briefed_task(story.agents.subject, "speed it up", f"start from report {tasked}")
    story.time_travel(minutes=story.setting(ReportsOptions.UNACTED_MINUTES) + 1)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, ReportsNudges.UNACTED, row_type="report", n=unread)
    result.expect_agent_not_told(story.agents.subject, ReportsNudges.UNACTED, row_type="report", n=planned)
    result.expect_agent_not_told(story.agents.subject, ReportsNudges.UNACTED, row_type="report", n=tasked)
    story.time_travel(minutes=REPEAT_MINUTES)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, ReportsNudges.UNACTED, row_type="report", n=unread)
    story.agent_runs(story.agents.subject, f"report settle {unread} --why 'the faults it found are fixed'")
    story.expect_row("reports", unread, {"settled_reason": "the faults it found are fixed"})
    story.time_travel(minutes=REPEAT_MINUTES)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, ReportsNudges.UNACTED, row_type="report", n=unread)
    story.expect_stack(story.agents.subject, Orchestrating)
