from journal.features.faults.faults_nudges import FaultsNudges
from journal.features.faults.faults_options import FaultsOptions
from journal.features.faults.support.slow_request_tally import GATHERED
from journal.features.faults.support.slow_requests import CHECK_INTERVAL_SECONDS
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MESSAGES_ROUTE = "/journal/messages"


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FaultsOptions.DEVELOPER, True)
@setting(FaultsOptions.REPORT, True)
@setting(FaultsOptions.REQUEST, 1)
def test_reads_of_fresh_rows_over_their_points_budget_are_reported_to_the_agent_once_enough_gathered(story):
    for number in range(GATHERED):
        story.user_sends_message(f"note {number} on the footer")
        story.user_opens(MESSAGES_ROUTE)
    story.time_travel(seconds=CHECK_INTERVAL_SECONDS)
    story.user_opens(MESSAGES_ROUTE)
    story.expect_agent_told(FaultsNudges.SLOW_REQUESTS, route=f"GET {MESSAGES_ROUTE}")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FaultsOptions.DEVELOPER, True)
@setting(FaultsOptions.REPORT, False)
def test_with_the_report_off_nothing_is_told_while_the_requests_are_still_listed(story):
    for _ in range(GATHERED):
        story.user_opens(MESSAGES_ROUTE)
    story.time_travel(seconds=CHECK_INTERVAL_SECONDS)
    story.user_opens(MESSAGES_ROUTE)
    story.expect_agent_not_told(FaultsNudges.SLOW_REQUESTS)
    story.agent_runs("developer slowest")
    story.expect_command_text(MESSAGES_ROUTE)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FaultsOptions.DEVELOPER, True)
@setting(FaultsOptions.REPORT, True)
@setting(FaultsOptions.REQUEST, 0)
def test_a_points_budget_of_none_reports_no_request(story):
    for _ in range(GATHERED):
        story.user_opens(MESSAGES_ROUTE)
    story.time_travel(seconds=CHECK_INTERVAL_SECONDS)
    story.user_opens(MESSAGES_ROUTE)
    story.expect_agent_not_told(FaultsNudges.SLOW_REQUESTS)
    story.expect_stack(Ready)
