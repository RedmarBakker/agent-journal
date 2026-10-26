from journal.config import Config
from journal.container import Container
from journal.repositories.scope import Scope
from journal.console.console import Console
from journal.console.standard_commands import StandardCommands
from journal.db.connection import Connection
from journal.support.masks import Masks
from journal.db.migrations import MIGRATIONS
from journal.db.migration_failures import MigrationFailures
from journal.db.migrator import Migrator
from journal.helpers.helpers import Helpers
from journal.db.indexes import Indexes
from journal.support.large_reads import LargeReads
from journal.support.query_times import QueryTimes
from journal.support.stage_times import StageTimes
from journal.repositories.declared_indexes import INDEXES
from journal.db.schema import Schema
from journal.engine.support.feature_registry import FeatureRegistry
from journal.engine.support.agent_event_audience import AgentEventAudience
from journal.console.support.verb_rules import VerbRules
from journal.helpers.helper_listeners import HelperListeners
from journal.events.bus import Bus
from journal.runtime import Runtime
from journal.sync.team_writes import TeamWrites
from journal.features.registry import Registry
from journal.features.standard import Standard
from journal.engine.support.data_readers import DataReaders
from journal.chat.process_card_poll import ProcessCardPoll
from journal.chat.row_process_card import RowProcessCard
from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.http.router import Router
from journal.http.routes.routes import Routes
from journal.http.server import Server
from journal.http.static_files import StaticFiles
from pathlib import Path
from journal.models.all_models import AllModels
from journal.engine.support.demands_part import DemandsPart
from journal.engine.support.demands_reader import DemandsReader
from journal.engine.support.stop_refusals_part import StopRefusalsPart
from journal.engine.support.stop_refusals_reader import StopRefusalsReader


class App:
    """Opens the database once and hands everything else its dependencies."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.container = Container()
        self.container.instance(Container, self.container)
        self.container.instance(Config, config)
        self.container.instance(Bus, Bus())
        self.container.bind(Connection, self.connection)
        self.container.bind(Schema, lambda: Schema(self.container.get(Connection), AllModels.MODELS))
        self.container.bind(Router, lambda: Routes(self.container).mount(self.container.call(Router)))
        self.container.bind(Console, self._console)
        self.container.bind(StaticFiles, lambda: StaticFiles(Path(__file__).resolve().parents[1] / "web" / "dist"))
        self.container.bind(Registry, lambda: Registry(Standard.FEATURES, self.container.get(SettingRows), StandardCommands.COMMANDS, Helpers.ALL))
        self.container.bind(FeatureRegistry, lambda: self.container.get(Registry))
        self.container.bind(AgentEventAudience, lambda: self.container.get(HelperListeners))
        self.container.bind(VerbRules, lambda: self.container.get(Registry))
        self.container.bind(DataReaders, lambda: DataReaders({DemandsPart.name: self.container.get(DemandsReader), StopRefusalsPart.name: self.container.get(StopRefusalsReader), **{feature.part_name(reader): self.container.get(reader) for feature in Standard.FEATURES for reader in feature.data}}, self.container.get(Scope), self.container.get(StageTimes), self.container.get(FeatureRegistry)))
        self.container.bind(ProcessCardPoll, lambda: ProcessCardPoll(self.container.get(Messages), {RowProcessCard.name: self.container.get(RowProcessCard), **{card.name: self.container.get(card) for feature in Standard.FEATURES for card in feature.process_cards}}))

    def connection(self) -> Connection:
        self.config.home.mkdir(parents=True, exist_ok=True)
        connection = Connection(self.config.database, self.container.get(Masks), self.container.get(StageTimes), self.container.get(QueryTimes), self.container.get(LargeReads))
        schema = Schema(connection, AllModels.MODELS)
        migrator = Migrator(connection, schema, MIGRATIONS, self.container.get(MigrationFailures))
        if schema.create():
            migrator.record_all()
        migrator.run()
        Indexes(connection, INDEXES).refresh()
        return connection

    def server(self) -> Server:
        return self.container.get(Server)

    def console(self) -> Console:
        return self.container.get(Console)

    def console_without_server(self) -> Console:
        self.container.get(TeamWrites).listen()
        return self.console()

    def _console(self) -> Console:
        console = self.container.call(Console)
        for command in StandardCommands.COMMANDS:
            console.add(command)
        for feature in self.container.get(Registry).features:
            for command in feature.commands:
                console.add(command)
        return console

    def runtime(self) -> Runtime:
        return self.container.get(Runtime)
