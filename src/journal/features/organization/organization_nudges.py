from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class OrganizationNudges:
    """The lines of the organization feature."""

    ROLE_WRITES_NOTHING = Nudge("organization", "role_has_no_write_tool", "your Role {{role}} has no write tool: change no file", repeat=Timeout.seconds(0))
    ACTION_WAITS_FOR_USER = Nudge("organization", "action_waits_for_the_user", "{{action}} waits for the user: ask with `journal question ask \"<may I?>\"`, act once the answer allows it", repeat=Timeout.seconds(0))
    ACTING_AS_ROLE = Nudge("organization", "you_act_as_the_role", "you act as {{role}} for this step; `journal role done` when it ends. {{guidance|cap=3000}}", repeat=Timeout.seconds(0), longest_characters=3090, longest_reason="it contains the Role's and its domain's guidance")
    ROLE_TOOL_REFUSED = Nudge("organization", "the_role_has_no_such_tool", "as {{role}} you do not use {{tool}}: your tools are {{tools}}", repeat=Timeout.seconds(0))
    ONE_ROLE_AT_A_TIME = Nudge("organization", "one_role_at_a_time", "you act as {{role}} already: `journal role done` first", repeat=Timeout.seconds(0))
    ROLE_REPORTED = Nudge("organization", "role_reported_up_the_hub", "{{report|cap=200}}: help it on, or pass it up the hub", repeat=Timeout.seconds(0), longest_characters=235, longest_reason="it carries the Role's own report")
    ROLE_TASK_RETURN = Nudge("organization", "role_task_returns_by_clocking_out", "Role work returns with `journal proof <point> \"<file:line and test>\"`, then `journal clock-out \"<report>\"`", repeat=Timeout.seconds(0))
    PLAN_TASK_AWAITS_HANDOFF = Nudge("organization", "plan_task_waiting_for_handoff", "plan task {{task}} waits for handoff to domain:{{domain}}; run `journal organization handoff {{task}} domain:{{domain}}`", repeat=Timeout.seconds(0))
    UNREAD_HANDOFF = Nudge("organization", "organization_handoff_waiting_in_inbox", "you have an unread handoff; run `journal organization inbox`", repeat=Timeout.seconds(0))
    ROLE_WORK_AWAITS_CHECK = Nudge(
        "organization", "role_work_waiting_for_check", "task {{task}} from worker {{worker}} waits for your check",
        "`journal worker check {{worker}} <point>`; then `journal organization handoff {{task}} plan`",
        repeat=Timeout.seconds(0), longest_characters=160,
        longest_reason="it names the waiting task and both commands to check and return it",
    )
