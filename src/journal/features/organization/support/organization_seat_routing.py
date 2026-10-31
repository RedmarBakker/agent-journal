from journal.support.skill import Skill


class OrganizationSeatRouting:
    """The route instructions shared by every generated organization seat."""

    guidance = (
        "Prefer the Read tool for files. Use awk, sed -n, head, tail, grep, wc, or cat only to read files in this mission. "
        "Use Edit for file changes only when this seat is allowed to write. "
        "Read work sent to your seat with `journal organization inbox`. "
        "Use `journal organization handoff <task> <target>` only when your seat is responsible for passing work onward. "
        "Run each journal command on its own. Do not combine it with curl, cd, a pipe, semicolon, &&, or another shell command. "
        "If needed, read the local /journal/health endpoint with a separate curl command. "
        "This is the only route between seats; do not use `rig send` or `rig queue`."
    )
    handoff_prompt = "Read your new handoff with `journal organization inbox`."
    domain_guidance = (
        "As the Domain seat, read your inbox with `journal organization inbox`, then hand each task to one of your Roles with "
        "`journal organization handoff <task> role:<domain>/<role>`. If your inbox has no handoff, wait for a journal handoff "
        "and do not ask the operator for task details."
    )
    role_guidance = (
        "As a writing Role seat, read your inbox with `journal organization inbox`, then clock in on your assigned task with "
        "`journal clock-in`. Prove each task point with `journal proof <point> \"<file:line, and the test that shows it>\"`, then return work with "
        "`journal clock-out \"<report>\"`. Clocking out returns your work to the Domain agent for checking. Do not hand off your task."
    )
    skill = Skill("organization-seat-routing", "Route organization work between seats; load it when a seat receives work or hands it off", f"""
# Organization seat routing

{guidance}

Use these targets:

- A Plan seat hands a task to a Domain seat with `domain:<id>`.
- A Domain seat hands work to a Role seat with `role:<domain>/<role>` and returns finished work to the Plan seat with `plan`.
- A writing Role seat proves each task point and clocks out; the clock-out returns its work to the Domain seat for checking.
- {domain_guidance}
- {role_guidance}

A Plan seat can inspect a task in its plan with `journal task show <task>`.
""")
