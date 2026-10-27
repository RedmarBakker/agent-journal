import json
from argparse import Namespace

from journal.console.command import Command
from journal.features.memory.support.memory_context import MemoryContext
from journal.features.memory.support.row_condition import RowCondition
from journal.models.memory_trigger import MemoryTrigger
from journal.support.rejection import Rejection
from journal.support.caller import Caller
from journal.repositories.repository import Repository


class RecordCommand(Command):
    """What rule and reminder share: create, list, read and strike."""

    repository: Repository

    def __init__(self, context: MemoryContext) -> None:
        self.context = context

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", f"record a {self.noun}")
        creation.add_argument("text")
        creation.add_argument("--reason", default="")
        creation.add_argument("--keywords", default="", help="words that bring it back when you write one, comma-separated")
        creation.add_argument("--on", default="", choices=[trigger.value for trigger in MemoryTrigger], help="a moment that brings it back too")
        creation.add_argument("--when", default="", help='a condition the moment must meet, as JSON: {"count": "tasks", "where": {"state": ["open", "started"]}, "is": 0}')
        creation.add_argument("--once", action="store_true", help="struck once it has been brought back by its moment")
        self.creation_arguments(creation)
        self.verb(verbs, "list", f"every {self.noun} here")
        self.verb(verbs, "read", f"a {self.noun} whole, which puts it in your context window").add_argument("n", type=int)
        self.verb(verbs, "strike", f"a {self.noun} that no longer holds").add_argument("n", type=int)

    def creation_arguments(self, creation) -> None:
        return None

    def create(self, args: Namespace, caller: Caller) -> int:
        row = self.repository.save(self.with_trigger(self.for_caller(self.new(args), caller), args), caller.actor)
        print(f"{self.noun} {row.id}: {row.text}")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        rows = self.repository.all()
        for row in rows:
            print(f"{row.id:>4}  {self.listed(row)}")
        return 0

    def read(self, args: Namespace, caller: Caller) -> int:
        row = self.context.admit(self.repository.find(args.n), caller.actor)
        print(f"{self.noun} {row.id}: {row.text}")
        return 0

    def strike(self, args: Namespace, caller: Caller) -> int:
        self.repository.delete(self.repository.find(args.n), caller.actor)
        print(f"{self.noun} {args.n} struck")
        return 0

    def listed(self, row) -> str:
        return row.text

    def for_caller(self, row, caller: Caller):
        return row

    @staticmethod
    def with_trigger(row, args: Namespace):
        if (args.when or args.once) and not args.on:
            raise Rejection("--when and --once go with --on, the moment that brings it back")
        if not args.on:
            return row
        return row.with_(trigger=args.on, condition=RecordCommand.condition(args.when), is_single_use=args.once)

    @staticmethod
    def condition(text: str) -> dict:
        if not text:
            return {}
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as fault:
            raise Rejection(f"--when is not JSON: {fault}") from fault
        RowCondition.read(payload)
        return payload

    def new(self, args: Namespace):
        return self.repository.model(text=args.text, keywords=self.keywords(args))

    @staticmethod
    def keywords(args: Namespace) -> tuple[str, ...]:
        return tuple(word.strip().lower() for word in args.keywords.split(",") if word.strip())
