from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE as COMMAND_CATALOGUE


AREA_DEFINITIONS = (
    ("plans-and-tasks", "Plans and tasks", (
        ("task create", "Create a task", 1), ("task rename", "Rename a task", 1),
        ("task edit", "Edit a task", 1), ("task brief", "Update a task brief", 1),
        ("task size", "Set a task size", 1), ("task scope-size", "Set a task scope size", 1),
        ("task propose-size", "Propose a task size", 1), ("task priorities", "Set task priorities", 1),
        ("task log", "Log task work", 1), ("plan create", "Create a plan", 1),
        ("plan add", "Add to a plan", 1), ("plan brief", "Update a plan brief", 1),
        ("plan rephase", "Rephase a plan", 1), ("plan phase", "Change a plan phase", 1),
        ("plan todos", "Edit plan todos", 1), ("plan priorities", "Change plan priorities", 1),
        ("plan card", "Update a plan card", 1), ("plan report", "Update a plan report", 1),
        ("plan testing", "Change plan testing", 1), ("template create", "Create a template", 1),
        ("template schedule", "Schedule a template", 1), ("task start", "Start a task", 2),
        ("task complete", "Complete a task", 2), ("task cancel", "Cancel a task", 2),
        ("task pause", "Pause a task", 2), ("task transfer", "Move a task to another worker", 2),
        ("plan remove", "Remove a plan", 2), ("plan ready", "Mark a plan ready", 2),
        ("plan review", "Review a plan", 2), ("plan pause", "Pause a plan", 2),
        ("plan return", "Return a plan", 2), ("plan mode", "Change a plan mode", 2),
        ("plan tell", "Tell a plan", 2), ("plan complete-phase", "Complete a plan phase", 2),
        ("plan approve", "Approve a plan", 3), ("plan start", "Start a plan", 3),
        ("plan cancel", "Cancel a plan", 3), ("plan cancel-phase", "Cancel a plan phase", 3),
        ("plan allow-tests", "Allow a plan to run tests", 3), ("plan merge", "Merge a plan", 3),
    ), ("task create", "task size", "plan priorities", "task start", "task transfer"), ""),
    ("dependencies-and-blocks", "Dependencies and blocks", (
        ("task depends", "Set task prerequisites", 1), ("await begin", "Wait for a task or event", 1),
        ("await clear", "Clear a wait", 1), ("task block", "Block a task", 2),
        ("task unblock", "Unblock a task", 2), ("plan block", "Block a plan", 2),
        ("plan unblock", "Unblock a plan", 2), ("stuck declare", "Declare a task stuck", 2),
        ("question ask", "Ask a question", 2), ("question answer", "Answer a question", 3),
    ), ("task depends", "await clear", "task block", "stuck declare"), ""),
    ("checks", "Checks", (
        ("check create", "Create a check", 1), ("check edit", "Edit a check", 1),
        ("check run", "Run a check", 1), ("check stop", "Stop a check", 1),
        ("tests budget", "Set a test budget", 1), ("tests command", "Change test commands", 2),
        ("tests load", "Read worker test commands", 2), ("check remove", "Remove a check", 3),
    ), ("check create", "check edit", "check run", "tests command"), ""),
    ("sequences", "Sequences", (
        ("sequence create", "Create a sequence", 1), ("sequence edit", "Edit a sequence", 1),
        ("sequence run", "Run a sequence", 2), ("sequence follow", "Follow a sequence", 2),
        ("sequence next", "Advance a sequence", 2), ("sequence pause", "Pause a sequence", 2),
        ("sequence delegate", "Delegate a sequence", 2), ("sequence abandon", "Abandon a sequence", 2),
    ), ("sequence create", "sequence edit", "sequence run", "sequence pause"), ""),
    ("rules-and-reminders", "Rules and reminders", (
        ("reminder create", "Create a reminder", 1), ("reminder strike", "Strike a reminder", 1),
        ("notice create", "Create a notice", 2), ("notice close", "Close a notice", 2),
        ("rule create", "Create a rule", 3), ("rule strike", "Strike a rule", 3),
    ), ("reminder create", "reminder strike", "notice create", "notice close"),
        "Making or striking a rule is tier 3: see Needs your decision."),
    ("triggers", "Triggers", (
        ("trigger create", "Create a trigger", 2), ("trigger schedule", "Schedule a trigger", 2),
        ("trigger strike", "Strike a trigger", 2),
    ), ("trigger create", "trigger schedule", "trigger strike"), ""),
    ("workers-and-reviewers", "Workers and reviewers", (
        ("worker send", "Send a job to a worker", 2), ("worker notify", "Notify a worker", 2),
        ("worker report", "Ask for a worker report", 2), ("worker wait", "Wait for a worker", 2),
        ("worker queue", "Queue a worker job", 2), ("worker release", "Release a worker", 2),
        ("worker drain", "Drain a worker", 2), ("worker rebase", "Rebase a worker", 2),
        ("worker check", "Accept a worker proof", 2), ("reviewer add", "Add a reviewer", 2),
        ("reviewer retire", "Retire a reviewer", 2), ("subagent retire", "Retire a subagent", 2),
        ("agents pause", "Pause agents", 2), ("agents resume", "Resume agents", 2),
        ("worker dispatch", "Start a worker", 3), ("worker merge", "Merge a worker's work", 3),
        ("worker discard", "Discard a worker's work", 3), ("worktree remove", "Remove a worktree", 3),
    ), ("worker notify", "worker report", "worker send", "worker release", "agents pause"),
        "Starting, merging or discarding a worker is tier 3."),
    ("messages-and-organization", "Messages and organization", (
        ("message tag", "Tag a message", 1), ("message amend-links", "Change message links", 1),
        ("message react", "React to a message", 1), ("message send", "Send a message", 2),
        ("message edit", "Edit a message", 2), ("organization handoff", "Hand work to a Domain agent", 2),
        ("organization reload", "Reload organization roles", 2),
    ), ("message tag", "message react", "message send", "organization handoff"), ""),
    ("documents-reports-and-collections", "Documents, reports and collections", (
        ("doc create", "Create a document", 1), ("doc update", "Update a document", 1),
        ("doc ready", "Mark a document ready", 1), ("doc keep", "Keep a document", 1),
        ("doc settle", "Settle a document", 1), ("report create", "Create a report", 1),
        ("report update", "Update a report", 1), ("report ready", "Mark a report ready", 1),
        ("report note", "Add a report note", 1), ("report drop", "Drop a report", 1),
        ("report item", "Add a report item", 1), ("report recap", "Recap a report", 1),
        ("collection create", "Create a collection", 1), ("collection add", "Add to a collection", 1),
        ("collection remove", "Remove from a collection", 1), ("collection rename", "Rename a collection", 1),
        ("collection delete", "Delete a collection", 3), ("doc import", "Import a document", 3),
    ), ("doc create", "doc update", "report create", "report update"), ""),
    ("settings-and-modes", "Settings and modes", (
        ("mode", "Change an agent's work mode", 2), ("settings set", "Change journal settings", 3),
        ("environment create", "Create an environment", 3), ("environment delete", "Delete an environment", 3),
        ("panic apply", "Apply a panic command", 3), ("developer reset", "Reset developer data", 3),
    ), ("mode",), "Changing settings is tier 3: see Needs your decision."),
    ("plugins-mcp-and-updates", "Plugins, MCP and updates", (
        ("plugin install", "Install a plugin", 3), ("plugin propose", "Propose a plugin", 3),
        ("plugin upgrade", "Upgrade a plugin", 3), ("plugin enable", "Enable a plugin", 3),
        ("plugin disable", "Disable a plugin", 3), ("plugin configure", "Configure a plugin", 3),
        ("plugin remove", "Remove a plugin", 3), ("dashboard set", "Set a dashboard", 3),
        ("dashboard unset", "Unset a dashboard", 3), ("dashboard clear", "Clear a dashboard", 3),
        ("mcp install", "Install an MCP server", 3), ("mcp key", "Change an MCP key", 3),
        ("mcp remove", "Remove an MCP server", 3), ("update apply", "Apply an update", 3),
        ("update install", "Install an update", 3),
    ), (), "Every verb in this area is tier 3: see Needs your decision."),
    ("secrets", "Secrets", (
        ("secret create", "Create a secret", 3), ("secret request", "Request a secret", 3),
        ("secret update", "Update a secret", 3), ("secret fill", "Fill a secret", 3),
        ("secret store", "Store a secret", 3), ("secret run", "Run with a secret", 3),
        ("secret propose", "Propose a secret change", 3), ("secret login", "Log in with a secret", 3),
        ("secret folder", "Change a secret folder", 3), ("secret delete", "Delete a secret", 3),
        ("secret restore", "Restore a secret", 3),
    ), (), "Every verb in this area is tier 3. Secret values are never readable."),
    ("git-and-sharing", "Git and sharing", (
        ("share create", "Create a share", 3), ("share stop", "Stop a share", 3),
        ("team connect", "Connect a team", 3), ("team publish", "Publish a team item", 3),
        ("team invite", "Invite to a team", 3), ("team revoke", "Revoke a team invitation", 3),
        ("team withdraw", "Withdraw a team item", 3), ("team delete", "Delete a team item", 3),
        ("library connect", "Connect a library", 3), ("library publish", "Publish to a library", 3),
        ("library invite", "Invite to a library", 3), ("library revoke", "Revoke a library invitation", 3),
        ("library withdraw", "Withdraw a library item", 3), ("library delete", "Delete a library item", 3),
    ), (), "Every verb in this area is tier 3: see Needs your decision."),
)

AREA_KEYS = tuple(area[0] for area in AREA_DEFINITIONS)
CAPABILITY_CATALOGUE = {
    f"{noun} {verb}": (area.lower().replace(",", "").replace(" ", "-"),
                        int(tier.removeprefix("tier ")) if tier.startswith("tier ") else tier)
    for area, nouns in COMMAND_CATALOGUE.items()
    for noun, verbs in nouns.items()
    for verb, tier in verbs.items()
}
CAPABILITY_LABELS = {
    capability: label
    for _key, _title, verbs, _displayed, _note in AREA_DEFINITIONS
    for capability, label, _tier in verbs
}
DECISION_CAPABILITIES = tuple(
    {
        "capability": f"{noun} {verb}",
        "title": CAPABILITY_LABELS.get(f"{noun} {verb}", f"{verb.replace('-', ' ').title()} {noun}"),
        "area": area,
        "tier": 3,
    }
    for area, nouns in COMMAND_CATALOGUE.items()
    for noun, verbs in nouns.items()
    for verb, tier in verbs.items() if tier == "tier 3"
)


def control_areas(capabilities: dict) -> list[dict]:
    settings = {key: value for key, value in capabilities.items()}
    areas = []
    for key, title, verbs, displayed, note in AREA_DEFINITIONS:
        rows = [
            {"capability": capability, "title": label, "tier": CAPABILITY_CATALOGUE[capability][1],
             "enabled": settings.get(capability, {}).get("on", False),
             "mode": settings.get(capability, {}).get("mode", "act")}
            for capability, label, _tier in verbs
            if capability in displayed and capability in CAPABILITY_CATALOGUE
        ]
        master = settings.get(f"area:{key}")
        enabled = master["on"] if master else any(
            settings.get(capability, {}).get("on", False) for capability, _label, _tier in verbs
        )
        areas.append({
            "key": key,
            "title": title,
            "enabled": enabled,
            "capabilities": [capability for capability, _label, _tier in verbs
                             if capability in CAPABILITY_CATALOGUE],
            "verbs": rows,
            "note": note,
        })
    return areas


def control_decisions(capabilities: dict) -> list[dict]:
    return [
        {**decision, **capabilities.get(decision["capability"], {"on": True, "mode": "propose"})}
        for decision in DECISION_CAPABILITIES
    ]
