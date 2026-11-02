from typing import Protocol, runtime_checkable

from journal.console.command import Command
from journal.support.agent_role import AgentRole
from journal.support.caller import Caller


@runtime_checkable
class VerbRules(Protocol):
    """What the console asks about who runs which verb: the agent roles, whether a role runs a command's verb, and the helper file that names a helper's verbs."""

    def roles(self) -> tuple[AgentRole, ...]: ...

    def runs_verb(self, command: type[Command], verb: str, role: AgentRole, caller: Caller | None = None, args=None) -> bool: ...

    def refusal(self, command: type[Command], args, caller: Caller) -> str: ...

    def helper_file(self, role: AgentRole) -> str: ...

    def helper_verbs(self, role: AgentRole) -> tuple[str, ...]: ...
