from typing import ClassVar

from journal.console.command import Command
from journal.features.supervisor.capability_catalogue import capability_entry
from journal.helpers.main_role import MainRole
from journal.models.alias import Alias
from journal.models.supervisor_grant import SupervisorGrant
from journal.support.agent_role import AgentRole
from journal.support.caller import Caller


class SupervisorRole(MainRole):
    """The supervisor's commands are the reads and switched-on actions in its current grant."""

    role: ClassVar[AgentRole] = AgentRole.SUPERVISOR
    READ_VERBS: ClassVar[frozenset[str]] = frozenset({"show", "list", "read", "overview", "health"})

    @classmethod
    def runs_alias(cls, alias: Alias) -> bool:
        return False

    @classmethod
    def runs(cls, command: type[Command], verb: str, caller: Caller | None = None, args=None) -> bool:
        return caller is None or not cls.refusal_reason(command, verb, caller, args)

    @classmethod
    def refusal(cls, command: type[Command], args, caller: Caller) -> str:
        reason = cls.refusal_reason(command, args.verb, caller, args)
        return f"a supervisor may not run journal {command.noun} {args.verb}: {reason}"

    @classmethod
    def refusal_reason(cls, command: type[Command], verb: str, caller: Caller, args) -> str:
        grant = caller.supervisor_grant
        if grant is None:
            return "its current grant is unavailable"
        if verb in cls.READ_VERBS or command.noun == "search" and verb == "find":
            return ""
        rule = grant.rule_for(f"{command.noun} {verb}", cls.row_id(command, args))
        if rule is not None:
            if rule.effect == "never":
                return "the owner refuses this verb on the named row"
            return "the owner requires this verb to be proposed"
        capabilities = dict((name, (enabled, mode)) for name, enabled, mode in grant.capabilities)
        capability = f"{command.noun} {verb}"
        catalogue_entry = capability_entry(command.noun, verb)
        if catalogue_entry is None:
            return "the capability is switched off"
        area, tier = catalogue_entry
        if tier == "read":
            return ""
        if tier == "never":
            return "the capability is never allowed"
        setting = capabilities.get(capability)
        if setting is None and tier == "tier 3":
            setting = (True, "propose")
        if setting is None or not setting[0]:
            return "the capability is switched off"
        area_key = area.lower().replace(",", "").replace(" ", "-")
        area_setting = capabilities.get(f"area:{area_key}")
        if area_setting is not None and not area_setting[0]:
            return "the capability is switched off"
        if setting[1] != "act":
            return "the capability is set to propose"
        if command.noun == "plan" and verb in {"priorities", "tell"}:
            return cls.plan_scope_refusal(grant, args)
        return ""

    @staticmethod
    def row_id(command: type[Command], args) -> int | None:
        argument = "plan" if command.noun == "plan" and hasattr(args, "plan") else "n"
        value = getattr(args, argument, None)
        return value if type(value) is int else None

    @staticmethod
    def plan_scope_refusal(grant: SupervisorGrant, args) -> str:
        if grant.watched_plans == "all":
            return ""
        plan_id = getattr(args, "plan", None) or getattr(args, "n", None)
        if plan_id is None:
            return "name a watched plan with --plan"
        if plan_id not in grant.watched_plans:
            return f"plan {plan_id} is an unwatched plan"
        return ""
