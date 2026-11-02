from journal.features.supervisor.support.admissions import DEFAULT_LEASE_SECONDS
from journal.support.agent_role import AgentRole
from supervisor_bridge.contracts import RUN_REFERENCE_KEYS
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_daily_cost import SupervisorDailyCost
from tests.stories.fixtures.supervisor.supervisor_daily_cost_below_cap import SupervisorDailyCostBelowCap
from tests.stories.fixtures.supervisor.supervisor_daily_cost_pending import SupervisorDailyCostPending


def admit_event(story, wakeup_id):
    return story.supervisor_posts("/_supervisor/v1/admit", {
        "protocol_version": 1,
        "source": "hint",
        "observation_cursor": None,
        "wakeup_id": wakeup_id,
        "kind": "checks.updated",
        "event_kind": "failed_check",
        "event_id": f"event-{wakeup_id}",
    })


def settle_maximal_usage(story, wake):
    run = wake.viewer_answer["run"]
    input_tokens = story.fixture.max_input_tokens_per_turn
    output_tokens = story.fixture.max_output_tokens_per_turn
    return story.supervisor_posts("/_supervisor/v1/usage", {
        "protocol_version": 1,
        "run_ref": {key: run[key] for key in RUN_REFERENCE_KEYS},
        "usage": {
            "input_tokens": 0,
            "output_tokens": output_tokens,
            "cache_creation_input_tokens": input_tokens,
            "cache_read_input_tokens": 0,
            "total_input_tokens": input_tokens,
            "provider_requests": 1,
            "provider_retries": 0,
        },
    })


def daily_records(story):
    return story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/supervisor/records?period=today&plan_id={story.plans.first}",
    )


def wakeup_counts(story):
    return story.user_opens_in(
        story.fixture.supervisor_owner_environment,
        f"/journal/plans/{story.plans.first}/supervisor/wakeups",
    )


@story(SupervisorDailyCost, subject=AgentRole.SUPERVISOR)
def test_wakes_after_settled_cost_reaches_the_daily_cap_wait_for_the_next_day(story):
    first = admit_event(story, "daily-cost-first")
    first.expect_viewer_passed()
    first.expect_viewer_part(("status",), "admitted")

    settled = settle_maximal_usage(story, first)
    settled.expect_viewer_passed()
    settled.expect_viewer_part(("status",), "settled")
    settled.expect_viewer_part(("usage_status",), "known")

    for wakeup_id in ("daily-cost-capped-one", "daily-cost-capped-two"):
        capped = admit_event(story, wakeup_id)
        capped.expect_viewer_passed()
        capped.expect_viewer_part(("status",), "skipped")
        capped.expect_viewer_part(("reason",), "budget_exhausted")

    records = daily_records(story)
    records.expect_viewer_passed()
    records.expect_viewer_part(("current", "runs"), 1)

    wakeups = wakeup_counts(story)
    wakeups.expect_viewer_passed()
    wakeups.expect_viewer_part(("counts", "Skipped (budget used up)"), 2)

    story.time_travel(minutes=15)
    next_day = admit_event(story, "daily-cost-next-day")
    next_day.expect_viewer_passed()
    next_day.expect_viewer_part(("status",), "admitted")
    story.expect_stack(story.agents.subject)


@story(SupervisorDailyCostBelowCap, subject=AgentRole.SUPERVISOR)
def test_a_settled_cost_below_the_daily_cap_leaves_room_for_another_wake(story):
    first = admit_event(story, "below-cap-first")
    first.expect_viewer_passed()
    first.expect_viewer_part(("status",), "admitted")

    settled = settle_maximal_usage(story, first)
    settled.expect_viewer_passed()
    settled.expect_viewer_part(("usage_status",), "known")

    story.time_travel(seconds=DEFAULT_LEASE_SECONDS + 1)
    next_wake = admit_event(story, "below-cap-second")
    next_wake.expect_viewer_passed()
    next_wake.expect_viewer_part(("status",), "admitted")
    story.expect_stack(story.agents.subject)


@story(SupervisorDailyCostPending, subject=AgentRole.SUPERVISOR)
def test_a_run_with_pending_cost_is_unknown_and_never_counts_as_zero(story):
    first = admit_event(story, "pending-cost-first")
    first.expect_viewer_passed()
    first.expect_viewer_part(("status",), "admitted")

    story.time_travel(seconds=DEFAULT_LEASE_SECONDS + 1)
    next_wake = admit_event(story, "pending-cost-next")
    next_wake.expect_viewer_passed()
    next_wake.expect_viewer_part(("status",), "skipped")
    next_wake.expect_viewer_part(("reason",), "unknown_cost")

    wakeups = wakeup_counts(story)
    wakeups.expect_viewer_passed()
    wakeups.expect_viewer_part(("counts", "Skipped (budget used up)"), 1)
    story.expect_stack(story.agents.subject)
