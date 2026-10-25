import contextvars
import queue
import threading
from dataclasses import replace
from typing import Iterator

from journal.console.command import SUBAGENT_KINDS, WORKER_KINDS
from journal.features.aliases.support.worker_alias_line import WorkerAliasLine
from journal.models.alias import Alias
from journal.console.console import Console
from journal.features.aliases.support.alias_lines import AliasLines
from journal.support.caller import Caller
from journal.support.caller_variables import CallerVariables
from journal.hooks.support.agent_identity import REFUSAL as IDENTITY_REFUSAL, AgentIdentity
from journal.providers.providers import Providers
from journal.support.plugin_tokens import PluginTokens
from journal.http.support.subagent_commands import SubagentCommands
from journal.console.support.outcome import Outcome
from journal.http.support.cli_post import CliPost
from journal.http.support.request import Request
from journal.http.support.stream_response import StreamResponse
from journal.features.shell.support.shell_runner import EXIT
from journal.support.response import Response
from journal.engine.support.launch_files import LaunchFiles
from journal.features.shell.support.background_commands import BackgroundCommands
from journal.sync.team_accounts import TeamAccounts

ACTOR_HEADER = "x-journal-actor"
THREAD_HEADER = "x-journal-thread"
EXEC = "__journal_exec"


class CliController:
    """The shim posts an argv here; the server runs it on the console it already has loaded and answers with the outcome, or with the line an alias stands for, which the shim runs itself. A command from a shell whose launch id is not its environment's is not accepted as the running agent's."""

    def __init__(self, console: Console, tokens: PluginTokens, subagents: SubagentCommands, launches: LaunchFiles, providers: Providers, aliases: AliasLines, identity: AgentIdentity, accounts: TeamAccounts, background: BackgroundCommands, worker_lines: WorkerAliasLine) -> None:
        self.accounts, self.background, self.worker_lines = accounts, background, worker_lines
        self.console, self.tokens, self.subagents, self.launches, self.providers, self.aliases = console, tokens, subagents, launches, providers, aliases
        self.identity = identity

    def run(self, request: Request) -> Response:
        variables = CallerVariables.parsed(request.body, self.providers.default().name)
        if not self.is_known(variables):
            return Response.json(self.token_refusal(variables), 403)
        return Response.json(self.outcome(variables, request.body["argv"], request))

    def run_posted(self, request: Request) -> StreamResponse:
        posted = CliPost.parsed(request.body["raw"])
        variables = replace(self.providers.caller_variables(posted.environment), environment=request.environment)
        alias = self.aliases.called(posted.argv)
        if alias is not None and self.is_known(variables):
            return self.alias_answer(alias, posted.argv, self.caller(variables, posted.argv, request))
        if self.is_known(variables) and self.background.is_background_command(posted.argv):
            return StreamResponse("text/plain", self.streamed(variables, posted.argv, request))
        outcome = self.outcome(variables, posted.argv, request) if self.is_known(variables) else self.token_refusal(variables)
        return StreamResponse("text/plain", iter([self.ending(outcome.text + outcome.error, outcome.code)]))

    @staticmethod
    def ending(text: str, code: int) -> bytes:
        return f"{text}{'' if not text or text.endswith(chr(10)) else chr(10)}{EXIT} {code}\n".encode()

    # a background command's printed lines go out as they are printed, into the output its shell line writes, its errors and exit line once it ends
    def streamed(self, variables: CallerVariables, argv: list[str], request: Request) -> Iterator[bytes]:
        lines: queue.Queue = queue.Queue()
        outcomes: list[Outcome] = []
        caller, context = self.caller(variables, argv, request), contextvars.copy_context()
        threading.Thread(target=context.run, args=(self.performed, argv, caller, lines, outcomes), name="cli-stream", daemon=True).start()
        streamed_text = ""
        while (text := lines.get()) is not None:
            streamed_text += text
            yield text.encode()
        outcome = outcomes[0]
        remainder = outcome.text[len(streamed_text):] + outcome.error
        yield self.ending(remainder or ("\n" if streamed_text and not streamed_text.endswith("\n") else ""), outcome.code)

    def performed(self, argv: list[str], caller: Caller, lines: queue.Queue, outcomes: list[Outcome]) -> None:
        try:
            outcomes.append(self.console.run_streamed(argv, caller, lines))
        finally:
            lines.put(None)

    def alias_answer(self, alias: Alias, argv: list[str], caller: Caller) -> StreamResponse:
        if caller.kind in WORKER_KINDS | SUBAGENT_KINDS and not (alias.worker_access and caller.kind in WORKER_KINDS):
            return StreamResponse("text/plain", iter([f"a {caller.kind} may not run the alias journal {argv[0]}: an alias is the main agent's own shell line\n{EXIT} 1\n".encode()]))
        return StreamResponse("text/plain", iter([f"{EXEC} {alias.terminal_line(self.worker_lines.argv(argv, caller)[1:])}\n{EXIT} 0\n".encode()]))

    def is_known(self, variables: CallerVariables) -> bool:
        plugin_proof = variables.plugin is None or self.tokens.matches(variables.plugin, variables.token)
        return plugin_proof and self.identity.is_proven(variables)

    def token_refusal(self, variables: CallerVariables) -> Outcome:
        if variables.plugin is not None and not self.tokens.matches(variables.plugin, variables.token):
            return Outcome.refused(f"the journal does not know this token for plugin {variables.plugin}\n")
        return Outcome.refused(IDENTITY_REFUSAL)

    def outcome(self, variables: CallerVariables, argv: list[str], request: Request) -> Outcome:
        return self.console.run(argv, self.caller(variables, argv, request))

    def caller(self, variables: CallerVariables, argv: list[str], request: Request) -> Caller:
        caller = (variables if self.launches.is_launch(variables.environment, variables.launch) else replace(variables, agent_shell=False)).caller(self.accounts.person_in(variables.environment))
        if self.subagents.runs(caller, argv, request.headers.get(ACTOR_HEADER), request.headers.get(THREAD_HEADER)):
            return caller.subagent_caller()
        return caller
