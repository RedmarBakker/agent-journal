from journal.support.skill import Skill


class OrganizationSeatRouting:
    """The route instructions shared by every generated organization seat."""

    guidance = (
        "Read work sent to your seat with `journal organization inbox`. "
        "Route every handoff with `journal organization handoff <task> <target>`. "
        "This is the only route between seats; do not use `rig send` or `rig queue`."
    )
    skill = Skill("organization-seat-routing", "Route organization work through the journal handoff and inbox commands", f"""
# Organization seat routing

{guidance}

Use these targets:

- A Plan seat hands a task to a Domain seat with `domain:<id>`.
- A Domain seat hands work to a Role seat with `role:<domain>/<role>` and returns finished work to the Plan seat with `plan`.
- A Role seat returns its result to its Domain seat with `domain:<domain>`.

A Plan seat can inspect a task in its plan with `journal task show <task>`.
""")
