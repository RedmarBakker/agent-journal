from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import SupervisorScheduledWake


class SupervisorEventWake(SupervisorScheduledWake):
    """A grant enables every supervisor event wake kind."""

    event_wakeups = (
        "failed_check", "stalled_task", "stale_worker",
        "message_to_supervisor", "question_to_supervisor",
    )
    owner_route = "/journal/supervisor/records?period=today&plan_id={plan_id}&area=checks"
