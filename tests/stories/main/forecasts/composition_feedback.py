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
                              f"plan add {story.plans.second} 'next change' --brief 'deploy the next revision' --domain development --size 5")

    result.expect_command_passed()
    result.expect_command_text("1 comparable delivered example")
    result.expect_command_text(f"task {story.tasks.first}")
    result.expect_command_text("original size 3 story points")
    result.expect_command_text("actual execution 1.0 hours")
    result.expect_command_text("actual delivery delay 1.0 hours")
    result.expect_command_text("Empirical baseline remains selected")
    result.expect_command_text_without("points per hour")
    story.expect_task(story.tasks.second, state="open", size=5)
    forecast = story.user_opens(f"/journal/plans/{story.plans.second}/forecast")
    forecast.expect_viewer_part(("duration_ranges", "history", "completed_observations"), 2)
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "comparable_examples", 0, "task_id"), story.tasks.first)
    forecast.expect_viewer_part(("duration_ranges", "tasks", 0, "comparable_examples", 0, "original_size_points"), 3)
    forecast.expect_viewer_part(("duration_calibration", "status"), "not_enough_history")
    story.expect_stack(story.agents.main, Ready)


@story(ReportSizedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_cold_composition_shows_no_personalized_bias_and_keeps_the_empirical_baseline(story):
    result = story.agent_runs(story.agents.main,
                              f"plan add {story.plans.first} 'another change' --brief 'deploy another revision' --domain development --size 5 --phase 1 --after {story.tasks.first} --reason 'the change follows the existing release task'")

    result.expect_command_passed()
    result.expect_command_text("No comparable delivered examples")
    result.expect_command_text("No aggregate sizing-bias score")
    result.expect_command_text("Empirical baseline remains selected")
    result.expect_command_text_without("points per hour")
    story.expect_task(story.tasks.first, state="open", size=3)
    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_part(("duration_calibration", "status"), "not_enough_history")
    story.expect_stack(story.agents.main, Ready)
