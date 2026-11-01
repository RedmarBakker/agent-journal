import hashlib
import json
import posixpath
import re

from journal.features.organization.support.approval_action import ApprovalAction
from journal.support.chain import Chain
from journal.support.tool_call import ToolCall

COMMANDS = {
    ApprovalAction.PRODUCTION_DEPLOYMENT: ("production_deployment", "gh workflow run", "make deploy", "kubectl apply", "terraform apply", "deploy production", "release production"),
    ApprovalAction.DESTRUCTIVE_DATA_CHANGE: ("destructive_data_change", "drop table", "drop database", "truncate", "rm -rf"),
    ApprovalAction.FINANCIAL_TRANSACTION: ("financial_transaction", "send payment", "create payment", "wire transfer", "bank transfer", "issue refund", "capture payment", "payout"),
    ApprovalAction.INVOICE_CORRECTION: ("invoice_correction", "correct invoice", "amend invoice", "void invoice", "credit note", "invoice correction"),
    ApprovalAction.CONTRACT_CHANGE: ("contract_change", "amend contract", "update contract", "sign contract", "terminate contract", "contract change"),
    ApprovalAction.PRIVACY_DECISION: ("privacy_decision", "delete personal data", "export personal data", "change consent", "revoke consent", "privacy request"),
    ApprovalAction.LEGAL_DECISION: ("legal_decision", "legal hold", "accept settlement", "sign settlement", "settle lawsuit", "legal filing"),
    ApprovalAction.SECURITY_DECISION: ("security_decision", "grant access", "revoke access", "rotate key", "reset credentials", "change security policy"),
    ApprovalAction.DATA_BREACH_DECISION: ("data_breach_decision", "data breach", "breach notification", "notify regulator", "notify customers"),
    ApprovalAction.PEOPLE_ACTION: ("people_action", "hire employee", "fire employee", "terminate employee", "disciplinary action", "employee termination"),
    ApprovalAction.EMPLOYMENT_TERMS_ACTION: ("employment_terms_action", "change salary", "salary update", "change employment terms", "change benefits", "change working hours"),
    ApprovalAction.CUSTOMER_LIABILITY_COMMITMENT: ("customer_liability_commitment", "customer liability", "accept liability", "indemnify customer", "commit to compensate"),
    ApprovalAction.VEHICLE_TRACKER_DRIVER_IMPACT: ("vehicle_tracker_driver_impact", "vehicle tracker", "disable tracker", "change tracker settings", "immobilize vehicle", "immobilise vehicle", "driver impact"),
}


class ApprovalActions:
    """Approval-required actions named by a command, tool name or tool input."""

    @staticmethod
    def of(command: str | ToolCall) -> tuple[ApprovalAction, ...]:
        if isinstance(command, ToolCall):
            if command.is_journal_line:
                return ()
            texts = (command.command, command.tool, command.input_text, *(part.text for part in command.parts))
        else:
            if Chain.is_journal_line(command):
                return ()
            texts = (command,)
        text = "\n".join(texts).lower()
        return tuple(action for action, names in COMMANDS.items() if any(ApprovalActions.matches(text, name) for name in names))

    @staticmethod
    def matches(text: str, phrase: str) -> bool:
        words = r"\s+".join(re.escape(word) for word in phrase.split())
        return re.search(rf"\b{words}\b", text) is not None

    @staticmethod
    def identity(call: ToolCall) -> tuple[str, str]:
        """Return a stable fingerprint and the complete normalized request shown to the user."""
        command = call.command.replace("\r\n", "\n").replace("\r", "\n").strip()
        targets = sorted({posixpath.normpath(path.replace("\\", "/")) for path in call.edited_paths if path.strip()})
        arguments = {**call.input, "command": command} if command and isinstance(call.input.get("command"), str) else call.input
        request = {"tool": call.tool.strip(), "command": command, "arguments": arguments, "targets": targets}
        canonical = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        details = json.dumps(request, ensure_ascii=False, sort_keys=True, indent=2, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), details
