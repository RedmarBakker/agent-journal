from journal.providers.providers import Providers
from journal.repositories.aliases import Aliases
from journal.support.command_classifier import CommandClassifier
from journal.support.hook import Hook
from journal.support.tool_call import ToolCall


class ToolCalls:
    """A hook's tool call as its provider decodes it, with the project's aliases, so a part that calls an alias is read as the shell command it stands for, each part classified by the command table."""

    def __init__(self, providers: Providers, aliases: Aliases, classifier: CommandClassifier) -> None:
        self.providers, self.aliases, self.classifier = providers, aliases, classifier

    def build(self, hook: Hook) -> ToolCall:
        return self.providers.lookup(hook.provider).call(hook.tool, hook.input, self.aliases.names(), self.classifier)
