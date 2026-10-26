from journal.features.seed import Seed
from journal.features.shell.support.command_mark_policy import CommandMarkPolicy
from journal.features.shell.support.git_commands import GitCommands
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.messages import Messages
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class StrayCommandMarkCleanup(Seed):
    """At boot, every command mark whose run was not a real background process goes, so a deploy clears the marks older rules wrote: a git or GitHub line, failed or not, a run never moved to the background, a quick read, and a command that never ran past five seconds; a mark whose run is no longer kept goes when its line was git."""

    def __init__(self, messages: Messages, outputs: CommandOutputs, mark_policy: CommandMarkPolicy, environments: Environments, scope: Scope) -> None:
        self.messages, self.outputs, self.mark_policy, self.environments, self.scope = messages, outputs, mark_policy, environments, scope

    def run(self) -> None:
        for environment in self.environments.all():
            with self.scope.environment(environment.row_id):
                self.cleared()

    def cleared(self) -> None:
        for card in self.messages.newest_shown(CardKind.COMMANDS):
            outputs = self.outputs.matching(id=card.data.get("output", 0))
            if self.mark_policy.is_stray_mark(outputs[0]) if outputs else GitCommands.is_git_line(card.data.get("line", "")):
                self.messages.delete(card, Actor.system())
