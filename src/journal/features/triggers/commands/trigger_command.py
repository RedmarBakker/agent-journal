from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import Command
from journal.support.caller import Caller
from journal.models.trigger import Trigger
from journal.models.trigger_action import TriggerAction
from journal.repositories.triggers import Triggers
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class TriggerCommand(Command):
    noun = "trigger"

    def __init__(self, triggers: Triggers, time_source: TimeSource) -> None:
        self.triggers, self.time_source = triggers, time_source

    def arguments(self, verbs) -> None:
        new_trigger = self.verb(verbs, "create", "watch for words")
        new_trigger.add_argument("phrases", help="comma-separated")
        new_trigger.add_argument("text", help="the line the journal sends to the agent")
        new_trigger.add_argument("--do", choices=[action.value for action in TriggerAction], default=TriggerAction.NUDGE.value)
        timed = self.verb(verbs, "schedule", "send a line to the agent at a time: once, every so many minutes, or on a cron line")
        timed.add_argument("text", help="the line the journal sends to the agent")
        timed.add_argument("--at", default="", help="the local time of its first line, 'YYYY-MM-DD HH:MM'; without it, the first time --every or --cron gives")
        timed.add_argument("--every", type=int, default=0, metavar="MINUTES", help="send the line again after this many minutes")
        timed.add_argument("--cron", default="", help="send the line at each local time a five-field cron line matches, such as '0 9 * * 1-5'")
        timed.add_argument("--until", default="", help="the local time after which it fires no more, 'YYYY-MM-DD HH:MM'")
        timed.add_argument("--times", type=int, default=0, help="how many times it fires at most")
        timed.add_argument("--do", choices=[TriggerAction.NUDGE.value, TriggerAction.INSTRUCT.value], default=TriggerAction.NUDGE.value)
        self.verb(verbs, "list", "every trigger")
        self.verb(verbs, "strike", "stop watching").add_argument("n", type=int)

    def create(self, args: Namespace, caller: Caller) -> int:
        phrases = tuple(w.strip() for w in args.phrases.split(",") if w.strip())
        trigger = self.triggers.save(Trigger(phrases=phrases, action=TriggerAction(args.do), text=args.text), caller.actor)
        print(f"trigger {trigger.id}: {', '.join(phrases)} -> {trigger.action}")
        return 0

    def schedule(self, args: Namespace, caller: Caller) -> int:
        current_time = self.time_source.moment()
        draft = Trigger(action=TriggerAction(args.do), text=args.text, is_scheduled=True, interval_minutes=args.every, cron_line=args.cron or None, end_at=self.local_time(args.until) if args.until else None, fire_limit=args.times)
        first = self.local_time(args.at) if args.at else draft.following_time(current_time)
        if first is None:
            raise Rejection("a scheduled trigger needs --at, --every or --cron")
        if first <= current_time:
            raise Rejection(f"{args.at} is already past: give a time to come")
        trigger = self.triggers.save(draft.with_(next_at=first), caller.actor)
        print(f"trigger {trigger.id}: {trigger.action}, next at {self.shown_time(first)}")
        return 0

    @staticmethod
    def local_time(text: str) -> datetime:
        try:
            return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M").astimezone().astimezone(timezone.utc)
        except ValueError:
            raise Rejection(f"a time is 'YYYY-MM-DD HH:MM' in local time, not {text!r}") from None

    @staticmethod
    def shown_time(moment: datetime) -> str:
        return moment.astimezone().strftime("%Y-%m-%d %H:%M")

    def list(self, args: Namespace, caller: Caller) -> int:
        for trigger in self.triggers.listed():
            print(f"{trigger.id:>4}  {trigger.action:<8} {self.schedule_text(trigger)}: {trigger.text}")
        return 0

    def schedule_text(self, trigger: Trigger) -> str:
        return f"next at {self.shown_time(trigger.next_at)}" if trigger.next_at is not None else ", ".join(trigger.phrases)

    def strike(self, args: Namespace, caller: Caller) -> int:
        self.triggers.delete(self.triggers.find(args.n), caller.actor)
        print(f"trigger {args.n} struck")
        return 0
