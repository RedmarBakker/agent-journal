from tests.stories.fixtures.supervisor.supervisor_event_wake import SupervisorEventWake


class SupervisorEventWakeOff(SupervisorEventWake):
    """A supervisor grant has every event wake switched off."""

    event_wakeups = ()
