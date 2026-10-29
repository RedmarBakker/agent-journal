from journal.features.organization.support.approval_action import ApprovalAction

COMMANDS = {
    ApprovalAction.PRODUCTION_DEPLOYMENT: ("gh workflow run", "make deploy", "kubectl apply", "terraform apply"),
    ApprovalAction.DESTRUCTIVE_DATA_CHANGE: ("DROP TABLE", "DROP DATABASE", "TRUNCATE", "rm -rf"),
}


class ApprovalActions:
    """The approval-required actions a shell command is: the ones whose commands are plain enough to tell by their words; an action no command here names is for the Role to ask about itself."""

    @staticmethod
    def of(command: str) -> tuple[ApprovalAction, ...]:
        return tuple(action for action, words in COMMANDS.items() if any(word in command for word in words))
