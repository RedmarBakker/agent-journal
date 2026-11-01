from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent

@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_a_plan_without_delivery_history_shows_not_enough_history_and_no_numeric_forecast(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("id", story.plans.first)
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("status", "not enough history")
    result.expect_viewer_shows("delivered_outcomes", 0)
    result.expect_viewer_shows("minimum_comparable_outcomes", 10)
    result.expect_viewer_shows("observed_capacity_days", 0)
    result.expect_viewer_shows("minimum_capacity_days", 20)
    result.expect_viewer_shows("probability_this_sprint", None)
    result.expect_viewer_shows("p50", None)
    result.expect_viewer_shows("p85", None)
    result.expect_viewer_shows("unknown_sizes", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("unknown_domains", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("missing_evidence", [
        "approved scope", "comparable cohort", "comparable delivery history", "observed capacity", "planned domain", "story points"
    ])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_unknown_size_domain_policy_and_capacity_are_named_without_becoming_zero(story):
    task = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    task.expect_viewer_shows("size", None)
    task.expect_viewer_shows("domain", None)
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("unknown_sizes", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("unknown_domains", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("capacity", None)
    result.expect_viewer_shows("probability_this_sprint", None)
    result.expect_viewer_shows("status", "not enough history")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_sprint_without_a_next_period_has_no_invented_next_deadline(story):
    sprint = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    sprint.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint.viewer_answer['id']}/forecast")
    result.expect_viewer_shows("this_sprint", None)
    result.expect_viewer_shows("next_sprint", None)
    result.expect_viewer_shows("carry_over", None)
    result.expect_viewer_shows("next_status", "next cycle not scheduled")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_past_sprint_miss_is_reported_even_when_its_next_forecast_is_unknown(story):
    sprint = story.user_presses("/journal/sprints", {"starts_on": "2026-10-01", "timezone": "Europe/Amsterdam"})
    sprint.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint.viewer_answer['id']}/forecast")
    result.expect_viewer_shows("past_deadline", True)
    result.expect_viewer_shows("status", "not enough history")
    result.expect_viewer_shows("probability_next_sprint", None)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_plan_and_sprint_forecasts_read_the_same_shared_delivery_projection(story):
    sprint = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    sprint.expect_viewer_passed()
    sprint_id = sprint.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint_id}/plans", {"plan_id": story.plans.first}).expect_viewer_passed()
    plan = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    cycle = story.user_opens(f"/journal/sprints/{sprint_id}/forecast")
    cycle.expect_viewer_shows("status", plan.viewer_answer["status"])
    cycle.expect_viewer_shows("bands", plan.viewer_answer["bands"])
    cycle.expect_viewer_shows("method_version", plan.viewer_answer["method_version"])
    story.expect_task(story.tasks.first, state="open")
    story.expect_task(story.tasks.second, state="open")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_a_missing_domain_and_size_cohort_does_not_choose_a_history_pool(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("cohort_domain", None)
    result.expect_viewer_shows("cohort_size_unit", "story points")
    result.expect_viewer_shows("pooled_domains", [])
    result.expect_viewer_shows("probability_this_sprint", None)
    result.expect_viewer_shows("missing_evidence", [
        "approved scope", "comparable cohort", "comparable delivery history", "observed capacity", "planned domain", "story points"
    ])
    story.expect_task(story.tasks.first, state="open")
    story.expect_task(story.tasks.second, state="open")
    story.expect_stack(story.agents.subject, Ready)
