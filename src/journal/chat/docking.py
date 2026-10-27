import re

from journal.models.message import Message
from journal.models.model import Model
from journal.repositories.checks import Checks
from journal.repositories.docs import Docs
from journal.repositories.dumps import Dumps
from journal.repositories.memories import Memories
from journal.repositories.messages import Messages
from journal.repositories.notices import Notices
from journal.repositories.plans import Plans
from journal.repositories.questions import Questions
from journal.repositories.reminders import Reminders
from journal.repositories.reports import Reports
from journal.repositories.repository import Repository
from journal.repositories.rules import Rules
from journal.repositories.sequences import Sequences
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.repositories.triggers import Triggers
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.chat.process_cards import AUTO_DOCKED, DOCKED, UNDOCK_TIME_KEY
from journal.chat.row_process_card import RowProcessCard
from journal.events.announcer import Announcer
from journal.events.moments.row_docked import RowDocked
from journal.models.support.ref import Ref
from journal.support.rejection import Rejection
from journal.models.support.row_card import RowCard
from journal.repositories.scope import Scope

# a link that names a row of the journal, table:number
ROW_LINK = re.compile(r"^[a-z_]+:\d+$")



class Docking:
    """The rows pinned above the chat: each is a keyed system message whose data records that it is docked and the row's card, the card already made for the row if there is one, else a card written for it; undocking leaves the message in place with docked set to false."""

    def __init__(self, tasks: Tasks, plans: Plans, docs: Docs, reports: Reports, memories: Memories, rules: Rules, reminders: Reminders, questions: Questions, sequences: Sequences,
                 templates: Templates, workers: Workers, triggers: Triggers, checks: Checks, dumps: Dumps, notices: Notices, messages: Messages, announcer: Announcer, scope: Scope) -> None:
        self.messages, self.announcer, self.scope = messages, announcer, scope
        self.kinds: dict[str, Repository] = {kind.model.noun(): kind for kind in (tasks, plans, docs, reports, memories, rules, reminders, questions, sequences, templates, workers, triggers, checks, dumps, notices)}
        self.tables: dict[str, Repository] = {kind.model.table(): kind for kind in self.kinds.values()}

    def nouns(self) -> tuple[str, ...]:
        return tuple(self.kinds)

    def is_row_link(self, link: str) -> bool:
        return ROW_LINK.match(link) is not None and link.partition(":")[0] in self.tables

    def dock_line(self, link: str) -> str:
        ref = Ref.parse(link)
        noun = self.tables[ref.type].model.noun()
        return f"{link} is a row of the journal: dock it at the bottom of the chat with journal {noun} dock {ref.id}; pin it above the chat only when the user asked for a pin, with --user-asked"

    def dock(self, noun: str, n: int, actor: Actor) -> Message:
        return self.dock_row(self.kinds[noun].find(n), actor)

    def table_row(self, table: str, n: int) -> Model:
        if table not in self.tables:
            raise Rejection(f"a row of {table} cannot be docked")
        return self.tables[table].find(n)

    def undock(self, noun: str, n: int, actor: Actor) -> Message:
        return self.undock_row(self.kinds[noun].find(n), actor)

    def undock_row(self, row: Model, actor: Actor) -> Message:
        card = self.card(row)
        if card is None or not card.data.get(DOCKED):
            raise Rejection(f"{row.heading()} is not docked")
        return self.release(card, actor)

    def dock_row(self, row: Model, actor: Actor) -> Message:
        return self.pin(self.card(row) or self.new_card(row, actor), row, actor)

    def pin(self, message: Message, row: Model, actor: Actor) -> Message:
        return self.saved_with(message, {**RowCard.build(row).as_data(), DOCKED: True}, actor)

    def pin_message(self, message: Message, actor: Actor) -> Message:
        return self.saved_with(message, {DOCKED: True, AUTO_DOCKED: False, UNDOCK_TIME_KEY: None}, actor)

    def release(self, message: Message, actor: Actor) -> Message:
        return self.saved_with(message, {DOCKED: False, AUTO_DOCKED: False}, actor)

    def saved_with(self, message: Message, data: dict, actor: Actor) -> Message:
        return self.messages.save(message.with_merged("data", data), actor)

    def card(self, row: Model) -> Message | None:
        cards = self.messages.with_key(RowProcessCard.key(row))
        return cards[0] if cards else None

    def new_card(self, row: Model, actor: Actor) -> Message:
        self.announcer.announce(RowDocked(environment_id=self.scope.id, row=Ref.build(row), actor=actor))
        return self.card(row)
