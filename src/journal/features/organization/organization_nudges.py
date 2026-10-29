from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class OrganizationNudges:
    """The lines of the organization feature."""

    ROLE_WRITES_NOTHING = Nudge("organization", "role_has_no_write_tool", "your Role {{role}} has no write tool: change no file", repeat=Timeout.seconds(0))
    ACTION_WAITS_FOR_USER = Nudge("organization", "action_waits_for_the_user", "{{action}} always waits for the user: ask with `journal question ask`, and do it only once the answer allows it", repeat=Timeout.seconds(0))
    ACTING_AS_ROLE = Nudge("organization", "you_act_as_the_role", "you act as {{role}} for this step; `journal role done` when it ends. {{guidance|cap=3000}}", repeat=Timeout.seconds(0), longest_characters=3100, longest_reason="it contains the Role's and its domain's guidance")
    ROLE_TOOL_REFUSED = Nudge("organization", "the_role_has_no_such_tool", "as {{role}} you do not use {{tool}}: your tools are {{tools}}", repeat=Timeout.seconds(0))
    ONE_ROLE_AT_A_TIME = Nudge("organization", "one_role_at_a_time", "you act as {{role}} already: `journal role done` first", repeat=Timeout.seconds(0))
