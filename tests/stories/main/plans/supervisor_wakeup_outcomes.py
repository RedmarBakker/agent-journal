from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.in_process import posted
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_observations import enrolled, seeded


def wakeup_result(story, kind, result, skip_reason, count_name):
    fixture = seeded(story.app)
    story.monkeypatch.setattr(type(fixture["authority"].agents), "is_running", lambda _self, _environment: True)
    grant, token, _ = enrolled(fixture)
    story.closers.append(lambda: fixture["authority"].secrets_store.drop(fixture["credentials"]))
    body = {
        "protocol_version": 1,
        "wakeup_id": "wakeup-1",
        "kind": kind,
        "result": result,
        "skip_reason": skip_reason,
    }
    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/wakeups",
        body,
        {"X-Journal-Supervisor-Token": token},
    )
    outcome = f"{result} ({skip_reason})" if skip_reason else result
    story.observed(f"the supervisor records a {outcome} wake-up", None, None)
    story.last_step.expect_viewer_passed()
    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/wakeups",
        body,
        {"X-Journal-Supervisor-Token": token},
    )
    story.observed("the supervisor retries its wake-up receipt", None, None)
    story.last_step.expect_viewer_passed()
    story.last_step.expect_viewer_part(("duplicate",), True)
    result_step = story.user_opens_in(
        fixture["owner_environment"].name,
        f"/journal/plans/{fixture['plan'].row_id}/supervisor/wakeups",
    )
    result_step.expect_viewer_passed()
    result_step.expect_viewer_part(("counts", count_name), 1)
    story.expect_stack(story.agents.subject, Ready)


def empty_admission_wakeup(story):
    fixture = seeded(story.app)
    story.monkeypatch.setattr(type(fixture["authority"].agents), "is_running", lambda _self, _environment: True)
    _, token, _ = enrolled(fixture)
    story.closers.append(lambda: fixture["authority"].secrets_store.drop(fixture["credentials"]))
    request = {
        "protocol_version": 1,
        "source": "timer",
        "observation_cursor": None,
        "wakeup_id": "empty-wakeup-1",
        "kind": "scheduled",
    }
    for _ in range(2):
        story.viewer_status, story.viewer_answer = posted(
            story.app,
            "/_supervisor/v1/admit",
            request,
            {"X-Journal-Supervisor-Token": token},
        )
        story.observed("the bridge reports a wake-up with no actionable evidence", None, None)
        story.last_step.expect_viewer_passed()
        story.last_step.expect_viewer_part(("status",), "skipped")
    result_step = story.user_opens_in(
        fixture["owner_environment"].name,
        f"/journal/plans/{fixture['plan'].row_id}/supervisor/wakeups",
    )
    result_step.expect_viewer_passed()
    result_step.expect_viewer_part(("counts", "Nothing to do"), 1)
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_an_acted_scheduled_wakeup_once(story):
    wakeup_result(story, "scheduled", "Acted", "", "Acted")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_proposed_event_wakeup_once(story):
    wakeup_result(story, "checks.updated", "Proposed", "", "Proposed")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_wakeup_with_nothing_to_do_once(story):
    empty_admission_wakeup(story)


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_quiet_wakeup_once(story):
    wakeup_result(story, "tasks.created", "Skipped as quiet", "quiet", "Skipped as quiet")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_busy_wakeup_once(story):
    wakeup_result(story, "tasks.updated", "Skipped", "busy", "Skipped (busy)")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_wakeup_with_stale_evidence_once(story):
    wakeup_result(story, "checks.created", "Skipped", "evidence stale", "Skipped (evidence stale)")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_wakeup_after_the_budget_is_used_once(story):
    wakeup_result(story, "phases.updated", "Skipped", "budget used up", "Skipped (budget used up)")


@story(NewSession, subject=AgentRole.MAIN)
def test_the_owner_counts_a_wakeup_handed_to_them_once(story):
    wakeup_result(story, "scheduled", "Handed to you", "needs owner", "Handed to you")
