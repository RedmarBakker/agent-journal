from journal.engine.nudge import Nudge
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.approval_actions import ApprovalActions
from journal.features.organization.support.role import Role
from journal.support.tool_call import ToolCall


class RolePolicy:
    """What a Role refuses of a tool call, for a worker dispatched to it and a solo Plan agent acting as it alike: a write when it has no write tool, and an action it lists as approval-required until the user has been asked; None when it allows the call."""

    def refusal(self, role: Role, call: ToolCall) -> Nudge | None:
        if call.edited_paths and not role.allows_edits():
            return OrganizationNudges.ROLE_WRITES_NOTHING.create(role=role.id)
        waiting = [action for part in call.parts for action in ApprovalActions.of(part.text) if role.needs_approval(action)]
        return OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=waiting[0]) if waiting else None
