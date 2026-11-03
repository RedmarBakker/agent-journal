from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.supervisor_costs import SupervisorCosts


def environment(story):
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    return story.app.container.get(Environments).find(plan.environment_id).name


@story(SupervisorCosts, subject=AgentRole.MAIN)
def test_an_owner_reads_measured_costs_across_periods_plans_areas_and_days(story):
    result = story.user_opens_in(environment(story), "/journal/supervisor/costs")
    result.expect_viewer_passed()
    result.expect_viewer_part(("periods", "today", "unknown_runs"), 1)
    result.expect_viewer_part(("periods", "week", "known_usd"), "0.60")
    result.expect_viewer_part(("periods", "week", "unknown_runs"), 1)
    result.expect_viewer_part(("periods", "month", "known_usd"), "1.10")
    result.expect_viewer_part(("averages", "per_wakeup", "usd"), "0.20")
    result.expect_viewer_part(("averages", "per_action", "usd"), "0.15")
    result.expect_viewer_part(("averages", "per_useful_result", "usd"), "0.20")
    result.expect_viewer_count("per_plan", 2)
    result.expect_viewer_rows_holding("per_plan", "plan_id", story.plans.second)
    result.expect_viewer_count("per_area", 2)
    result.expect_viewer_part(("quiet_savings", "quiet_wakeups"), 2)
    result.expect_viewer_part(("quiet_savings", "estimated_usd"), "0.40")
    result.expect_viewer_count("wakeups_per_day", 7)
    result.expect_viewer_part(("wakeups_per_day", 5, "date"), "2025-01-07")
    result.expect_viewer_part(("wakeups_per_day", 5, "total"), 0)
    result.expect_viewer_part(("wakeups_per_day", 6, "date"), "2025-01-08")
    result.expect_viewer_part(("wakeups_per_day", 6, "total"), 4)
    result.expect_viewer_count("daily_trend", 30)
    result.expect_viewer_part(("daily_trend", 29, "known_usd"), None)
    story.expect_stack(story.agents.main, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_an_owner_sees_no_cost_recorded_before_the_first_wake_up(story):
    result = story.user_opens_in("main", "/journal/supervisor/costs")
    result.expect_viewer_passed()
    result.expect_viewer_part(("periods", "today", "known_usd"), "0.00")
    result.expect_viewer_part(("periods", "today", "unknown_runs"), 0)
    result.expect_viewer_part(("averages", "per_wakeup", "usd"), None)
    result.expect_viewer_count("per_plan", 0)
    result.expect_viewer_count("wakeups_per_day", 7)
    result.expect_viewer_count("daily_trend", 30)
    story.expect_stack(story.agents.main, Ready)


