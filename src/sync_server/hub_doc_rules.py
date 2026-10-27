from sync_server.accounts import Accounts
from sync_server.change_log import ChangeLog
from sync_server.logged_change import LoggedChange
from sync_server.rejected_field import RejectedField
from sync_server.row_type import RowType
from sync_server.stored_row import StoredRow

DOCS = "docs"
ENVIRONMENTS = "environments"
HUB = "hub"
READ_ONLY = "read_only"
TEXT_FIELDS = ("title", "abstract", "body")
RULE_FIELDS = ("edit_mode", "owner", "environment_id")


class HubDocRules:
    """The rules of a document in the hub environment, the only rows the team server reads for what they mean: whoever owns it or is an admin changes it; anyone else changes the text of one free to edit, and nothing of one read-only, and never who may edit it. A pushed change that breaks them has those fields rejected with the values that stand, which the sender puts back in its copy."""

    def __init__(self, log: ChangeLog, accounts: Accounts) -> None:
        self.log, self.accounts = log, accounts

    def refused(self, change: LoggedChange, current: StoredRow | None) -> tuple[RejectedField, ...]:
        if change.row_table != DOCS or not change.is_update() or current is None or not self.is_in_hub(current):
            return ()
        if change.account_id == current.fields.get("owner") or self.accounts.find(change.account_id).is_admin():
            return ()
        guarded = (*TEXT_FIELDS, *RULE_FIELDS) if current.fields.get("edit_mode") == READ_ONLY else RULE_FIELDS
        return tuple(RejectedField(DOCS, change.row, name, current.fields[name], current.changed_at.get(name, 0.0), str(current.writers.get(name, ""))) for name in change.fields if name in guarded and name in current.fields)

    def is_in_hub(self, doc: StoredRow) -> bool:
        environment = self.log.row(ENVIRONMENTS, int(doc.fields.get("environment_id", 0)))
        return environment is not None and RowType.of(environment.fields, "environment_type") == HUB
