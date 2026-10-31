from journal.support.skill import Skill


class OrganizationSeatRouting:
    """The route instructions shared by every generated organization seat."""

    guidance = (
        "Read work sent to your seat with `journal organization inbox`. "
        "Route every handoff with `journal organization handoff <task> <target>`. "
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
        "`journal clock-in`."
    )
    skill = Skill("organization-seat-routing", "Route organization work between seats; load it when a seat receives work or hands it off", f"""
# Organization seat routing

{guidance}

Use these targets:

- A Plan seat hands a task to a Domain seat with `domain:<id>`.
- A Domain seat hands work to a Role seat with `role:<domain>/<role>` and returns finished work to the Plan seat with `plan`.
- A Role seat returns its result to its Domain seat with `domain:<domain>`.
- {domain_guidance}
- {role_guidance}

A Plan seat can inspect a task in its plan with `journal task show <task>`.
""")
