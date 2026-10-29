from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class OrganizationNudges:
    """The lines of the organization feature."""

    ROLE_WRITES_NOTHING = Nudge("organization", "role_has_no_write_tool", "your Role {{role}} has no write tool: change no file", repeat=Timeout.seconds(0))
    ACTION_WAITS_FOR_USER = Nudge("organization", "action_waits_for_the_user", "{{action}} always waits for the user: ask with `journal question ask`, and do it only once the answer allows it", repeat=Timeout.seconds(0))
