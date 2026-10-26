from pathlib import Path
from typing import ClassVar

from journal.chat.process_card import ProcessCard
from journal.console.command import Command
from journal.engine.conduct import Conduct
from journal.engine.base_state import BaseState
from journal.engine.job import Job
from journal.engine.support.modes import Modes
from journal.models.agent_role import AgentRole
from journal.events.data_source import DataSource
from journal.events.listener import Listener
from journal.engine.nudge import Nudge
from journal.support.option import Option
from journal.features.seed import Seed
from journal.features.support.service import Service
from journal.support.skill import Skill
from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.host_writer import HostWriter
from journal.engine.demand import Demand


class Feature[D](DataSource[D]):
    """One switchable subject. It brings its states, its work modes if it has them, its conduct and the conduct and listeners it gives each helper role whose file turns it on whole, its nudges, its state-free listeners, its jobs, its live chat marks, the writes it makes when another journal asks this one as host, and its commands; nothing else knows a feature exists. D is the class of the part it reads into the feature data an event carries."""

    name: ClassVar[str]
    title: ClassVar[str] = ""
    help: ClassVar[str] = ""
    fixed: ClassVar[bool] = False
    states: ClassVar[tuple[type[BaseState], ...]] = ()
    nudges: ClassVar[tuple[Nudge, ...]] = ()
    demands: ClassVar[tuple[Demand, ...]] = ()
    options: ClassVar[tuple[Option, ...]] = ()
    listeners: ClassVar[tuple[type[Listener], ...]] = ()
    data: ClassVar[tuple[type, ...]] = ()
    conduct: ClassVar[tuple[type[Conduct], ...]] = ()
    helper_conduct: ClassVar[dict[AgentRole, tuple[type[Conduct], ...]]] = {}
    helper_listeners: ClassVar[dict[AgentRole, tuple[type[Listener], ...]]] = {}
    commands: ClassVar[tuple[type[Command], ...]] = ()
    seeds: ClassVar[tuple[type[Seed], ...]] = ()
    jobs: ClassVar[tuple[type[Job], ...]] = ()
    process_cards: ClassVar[tuple[type[ProcessCard], ...]] = ()
    host_writers: ClassVar[tuple[type[HostWriter], ...]] = ()
    skill: ClassVar[Skill | None] = None
    card_families: ClassVar[tuple[CardFamily, ...]] = ()
    card_kinds: ClassVar[tuple[MarkKind, ...]] = ()
    services: ClassVar[tuple[Service, ...]] = ()
    default: ClassVar[bool] = True
    modes: ClassVar[Modes | None] = None

    @classmethod
    def applies(cls, root: Path) -> bool:
        return True

    @classmethod
    def part_name(cls, reader: type) -> str:
        return getattr(reader, "source", cls).name

    @classmethod
    def part_names(cls) -> frozenset[str]:
        return frozenset(cls.part_name(reader) for reader in cls.data)
