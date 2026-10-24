import shutil
import subprocess
from argparse import Namespace

from journal.console.command import Command
from journal.console.support.panic_report import PanicReport
from journal.engine.delivery import Delivery
from journal.engine.state_machine import StateMachine
from journal.support.rejection import Rejection
from journal.repositories.reports import Reports
from journal.repositories.scope import Scope
from journal.engine.states_catalogue import StatesCatalogue
from journal.support.caller import Caller

POP = "pop"
ISSUE_REPOSITORY = "jessegall/agent-journal"
ISSUE_ADDRESS = f"https://github.com/{ISSUE_REPOSITORY}/issues/new"
GH_TIMEOUT_SECONDS = 60
IDLE = "idle"


class PanicCommand(Command):
    """journal panic <state> [name=value ...]: the one way to change the stack from outside the engine, always allowed to the main agent and the user, never to a worker or a subagent. A state name pushes that state, pop pops the top, idle empties the stack down to the bottom; the stack is printed afterwards. journal panic report writes what held the agent's stops as a report, and journal panic issue files that report on the agent-journal repository."""

    noun = "panic"
    default_verb = "apply"

    def __init__(self, machine: StateMachine, states: StatesCatalogue, scope: Scope, delivery: Delivery, report: PanicReport, reports: Reports) -> None:
        self.machine, self.states, self.scope, self.delivery, self.panic_report, self.reports = machine, states, scope, delivery, report, reports

    def arguments(self, verbs) -> None:
        time = self.verb(verbs, "apply", "push a state by name, pop the top, or idle to empty the stack")
        time.add_argument("state")
        time.add_argument("values", nargs="*", help="the state's values as name=value")
        self.verb(verbs, "report", "write a report of what held your stops, to read before it is filed as an issue")
        issue = self.verb(verbs, "issue", "file a panic report as an issue on the agent-journal repository with gh, or print it with the address to open one")
        issue.add_argument("n", type=int, help="the report's number")

    def apply(self, args: Namespace, caller: Caller) -> int:
        text = " ".join(["journal panic", args.state, *args.values])
        reply = self.changed(args, caller, text)
        self.delivery.applied(reply, 0.0)
        agent = reply.agent
        print(f"the stack, bottom to top: {', '.join(state.state_text() for state in self.machine.states.stack(agent).states)}")
        return 0

    def changed(self, args: Namespace, caller: Caller, text: str):
        if args.state == POP:
            return self.machine.pop(caller.agent_session, self.scope.id, caller.actor, text)
        if args.state == IDLE:
            return self.machine.reset(caller.agent_session, self.scope.id, caller.actor, text)
        if not self.states.known(args.state):
            raise Rejection(f"no state is named {args.state}; the states are {', '.join(self.states.names())}")
        return self.machine.push(caller.agent_session, self.scope.id, self.states.restored(args.state, self.field_values(args.values)), caller.actor, text)

    @staticmethod
    def field_values(pairs: list[str]) -> dict:
        values = {}
        for pair in pairs:
            name, _, value = pair.partition("=")
            values[name] = int(value) if value.isdigit() else value
        return values

    def report(self, args: Namespace, caller: Caller) -> int:
        report = self.panic_report.report(caller)
        print(f"report {report.id} written: read it with journal report show {report.id} --all, take out anything private, then journal panic issue {report.id} files it on {ISSUE_REPOSITORY}")
        return 0

    def issue(self, args: Namespace, caller: Caller) -> int:
        report = self.reports.find(args.n)
        if shutil.which("gh") is None:
            print(f"gh is not installed: open {ISSUE_ADDRESS} and paste this\n\n# {report.title}\n\n{report.body}")
            return 0
        filed = subprocess.run(["gh", "issue", "create", "-R", ISSUE_REPOSITORY, "--title", report.title, "--body", report.body], capture_output=True, text=True, timeout=GH_TIMEOUT_SECONDS)
        print(filed.stdout.strip() or filed.stderr.strip())
        return filed.returncode
