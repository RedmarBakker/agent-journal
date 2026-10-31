from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.plan_with_finished_development_example import PlanWithFinishedDevelopmentExample
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan


@setting(EstimatesOptions.MODE, "report")
@story(PlanWithFinishedDevelopmentExample, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_builder_sees_same_cohort_examples_with_their_original_sizes_and_actual_durations(story):
    result = story.agent_runs(story.agents.main,
                              f"plan add {story.plans.second} 'next change' --brief 'deploy the next revision' --domain development")

    result.expect_command_passed()
    forecast = story.user_opens(f"/journal/plans/{story.plans.second}/forecast")
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "cohort"), {
        "domain": "development", "size_scale_version": "c77b87f4bb0d3eb9ec8702833cc0f7e882b8a1c09f1d593d9a25fef3939b1de1",
        "criteria_version": "9e5b9c3201baa4bb", "environment_id": 1,
        "cohort_version": "plan4-outcome-cohort-v1", "model": None, "tier": None,
    })
    outcomes = story.user_opens(f"/journal/plans/{story.plans.first}/outcomes")
    outcomes.expect_viewer_part(("tasks", 0, "outcomes"), [])
    result.expect_command_text("1 similar finished task")
    result.expect_command_text(f"Task {story.tasks.first}")
    result.expect_command_text("original estimate 3 points")
    result.expect_command_text("work took 1.0 hours")
    result.expect_command_text("delivery took 1.0 hours after work finished")
    result.expect_command_text("Ranges come from past delivered tasks; the learned ranges are advice only.")
    result.expect_command_text_without("points per hour")
    result.expect_command_text_without("authorized cohort")
    result.expect_command_text_without("sizing-bias score")
    result.expect_command_text_without("held-out actuals")
    task = story.created_number("task")
    story.expect_task(task, state="open", size=None)
    forecast = story.user_opens(f"/journal/plans/{story.plans.second}/forecast")
    forecast.expect_viewer_part(("duration_ranges", "history", "completed_observations"), 2)
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "comparable_examples", 0, "task_id"), story.tasks.first)
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "comparable_examples", 0, "plan_id"), story.plans.first)
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "comparable_examples", 0, "original_size_points"), 3)
    forecast.expect_viewer_part(("duration_calibration", "status"), "not_enough_history")
    story.expect_stack(story.agents.main, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_cold_composition_shows_no_personalized_bias_and_keeps_the_empirical_baseline(story):
    result = story.agent_runs(story.agents.main,
                              f"plan add {story.plans.first} 'another change' --brief 'deploy another revision' --domain development --size 5 --phase 1 --after {story.tasks.first} --reason 'the change follows the existing release task'")

    result.expect_command_passed()
    result.expect_command_text("No similar finished tasks yet.")
    result.expect_command_text("Not enough finished tasks to compare work time estimates (0 of 5).")
    result.expect_command_text("Ranges come from past delivered tasks; the learned ranges are advice only.")
    result.expect_command_text_without("points per hour")
    result.expect_command_text_without("authorized cohort")
    result.expect_command_text_without("sizing-bias score")
    result.expect_command_text_without("held-out actuals")
    story.expect_task(story.tasks.first, state="open", size=3)
    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_part(("duration_ranges", "method_version"), "bayesian-log-linear-duration-v1")
    forecast.expect_viewer_part(("duration_ranges", "status"), "not_enough_history")
    forecast.expect_viewer_part(("duration_calibration", "status"), "not_enough_history")
    story.expect_stack(story.agents.main, Ready)
