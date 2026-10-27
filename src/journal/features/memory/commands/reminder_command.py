from argparse import Namespace
from datetime import datetime, timezone

from journal.features.memory.commands.record_command import RecordCommand
from journal.features.memory.support.memory_context import MemoryContext
from journal.engine.clock import Clock
from journal.models.reminder import Reminder
from journal.repositories.agents import Agents
from journal.repositories.reminders import Reminders
from journal.support.caller import Caller
from journal.support.rejection import Rejection



class ReminderCommand(RecordCommand):
    """Reminders: what to keep doing here, and with --at one set for a moment, informed once then and struck."""

    noun = "reminder"

    def __init__(self, reminders: Reminders, context: MemoryContext, agents: Agents, clock: Clock) -> None:
        super().__init__(context)
        self.repository, self.agents, self.clock = reminders, agents, clock

    def creation_arguments(self, creation) -> None:
        creation.add_argument("--at", default="", help="a local date and time, such as 2026-10-24 09:30: quiet until then, told once then, and struck")
        creation.add_argument("--every-minutes", type=int, default=0, help="send it again every so many minutes while it holds")
        creation.add_argument("--every-tool-uses", type=int, default=0, help="send it again every so many tool uses while it holds")

    def new(self, args: Namespace) -> Reminder:
        if args.every_minutes and args.every_tool_uses:
            raise Rejection("a reminder repeats every so many minutes or every so many tool uses, not both")
        if min(args.every_minutes, args.every_tool_uses) < 0:
            raise Rejection("an interval is a whole number above nought")
        return Reminder(text=args.text, keywords=self.keywords(args), due_at=self.moment(args.at) if args.at else None, every_minutes=args.every_minutes, every_tool_uses=args.every_tool_uses)

    def for_caller(self, row: Reminder, caller: Caller) -> Reminder:
        return row.sent(self.clock.time(), self.agents.session_agent(caller.session).tool_uses if caller.session else 0)

    def listed(self, row: Reminder) -> str:
        return f"{row.text} (at {row.due_at.astimezone().strftime(Reminder.MOMENT)})" if row.due_at else row.text

    @staticmethod
    def moment(text: str) -> datetime:
        try:
            local = datetime.strptime(text.strip(), Reminder.MOMENT)
        except ValueError as wrong:
            raise Rejection(f"--at takes a local date and time such as 2026-10-24 09:30, not {text}") from wrong
        return min(local.replace(fold=fold).astimezone(timezone.utc) for fold in (0, 1))
