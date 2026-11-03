from tests.stories.fixtures.supervisor.supervisor_event_wake import SupervisorEventWake


class SupervisorEventWakeOff(SupervisorEventWake):
    """A supervisor grant has every event wake switched off."""

    event_wakeups = ()
    owner_route = "/journal/supervisor/records?period=today&plan_id={plan_id}&area=plans-and-tasks"
