import gc
import sys
import traceback
import time as timing
from journal.engine.support.assigner_index import AssignerIndex
from journal.engine.boot_notices import BootNotices
from journal.engine.clock import Clock
from journal.features.updates.updates_options import UpdatesOptions
from journal.repositories.setting_rows import SettingRows
from journal.engine.job_runner import JobRunner
from journal.engine.lifecycle import Lifecycle
from journal.engine.menu_watcher import MenuWatcher
from journal.features.plugins.support.service_start import ServiceStart
from journal.features.skills.support.skill_files import SkillFiles
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.plugins.support.plugin_skills import PluginSkills
from journal.engine.delivery import Delivery
from journal.engine.hook_answer import HookAnswer
from journal.features.workers.listeners.researcher_end import ResearcherEnd
from journal.features.workers.listeners.researcher_start import ResearcherStart
from journal.features.workers.listeners.researchers_closed import ResearchersClosed
from journal.engine.row_assignment import RowAssignment
from journal.events.rows.task_closed import TaskClosed
from journal.engine.state_machine import StateMachine
from journal.console.creations import Creations
from journal.features.listeners.record_changes import RecordChanges
from journal.features.listeners.unlink_deleted import UnlinkDeleted
from journal.events.models.model_event import ModelEvent
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.engine.row_event_delivery import RowEventDelivery
from journal.engine.nudge_registry import NudgeRegistry
from journal.events.models.created import Created
from journal.events.models.deleted import Deleted
from journal.events.bus import Bus
from journal.features.registry import Registry
from journal.events.blocking import Blocking
from journal.features.switches import Switches
from journal.support.listener_queue import ListenerQueue
from journal.config import Config
from journal.container import Container
from journal.repositories.scope import Scope
from journal.http.server import Server
from journal.support.instance_guard import InstanceGuard
from journal.events.announcer import Announcer
from journal.events.moments.server_replaced import ServerReplaced
from journal.version import VERSION
from journal.http.share_server import ShareServer
from journal.sync.team_account import TeamAccount
from journal.console.console import Console
from journal.support.time_source import TimeSource




class Runtime:
    """What the server process keeps running: the HTTP server and the share server beside it, the deferred worker and the job runner with the clock, the menu watcher and every feature's jobs, with the machine on the bus. It boots in phases: the server listens first and holds every request while everything loads, and only once booted do the requests go through and the workers, jobs and services start, and the launches of a server on older code it stopped are told so. State itself is in the database, so a restart loses nothing."""

    def __init__(self, container: Container, server: Server, deferred: ListenerQueue, clock: Clock, machine: StateMachine, bus: Bus, registry: Registry, scope: Scope, watcher: MenuWatcher, share_server: ShareServer, reserve: InstanceGuard, jobs: JobRunner, lifecycle: Lifecycle, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.container, self.server, self.deferred, self.clock, self.machine, self.bus, self.registry, self.scope = container, server, deferred, clock, machine, bus, registry, scope
        self.watcher, self.share_server, self.standby, self.jobs, self.lifecycle = watcher, share_server, reserve, jobs, lifecycle

    def register_nudges(self) -> None:
        nudges = self.container.get(NudgeRegistry)
        for feature in self.registry.features:
            for nudge in feature.nudges:
                nudges.register(nudge)

    def boot(self) -> None:
        self.register_nudges()
        self.machine.index_listeners()
        self.bus.add_answer_listener(AgentEvent, self.container.get(HookAnswer), Blocking.ANSWER)
        self.bus.add_answer_listener(RowEvent, self.container.get(RowEventDelivery), Blocking.NEXT_DECISION)
        for researcher_listener in (ResearcherStart, ResearcherEnd, ResearchersClosed):
            self.bus.add_answer_listener(researcher_listener.event_type(), self.container.get(researcher_listener), Blocking.NEXT_DECISION)
        self.bus.add_answer_listener(Created, Creations(), Blocking.ANSWER)
        self.bus.listen(ModelEvent, self.container.get(RecordChanges))
        self.bus.listen(Deleted, self.container.get(UnlinkDeleted))
        assigners = self.container.get(AssignerIndex)
        for feature in self.registry.features:
            for assigner in feature.assigners:
                assigners.register(self.container.get(assigner))
            for listener, reason in feature.answer_listeners:
                self.bus.add_answer_listener(listener.event_type(), Switches(feature, self.container.get(listener), self.registry, self.scope, reason), reason)
            for listener in feature.listeners:
                self.bus.listen(listener.event_type(), Switches(feature, self.container.get(listener), self.registry, self.scope))
            for seed in feature.seeds:
                self.seeded(seed)
        self.bus.add_answer_listener(TaskClosed, self.container.get(RowAssignment), Blocking.NEXT_DECISION)
        for reply in self.machine.compactions_ended():
            self.container.get(Delivery).applied(reply, 0.0)

    def seeded(self, seed: type) -> None:
        try:
            self.container.get(seed).run()
        except Exception as fault:
            print(traceback.format_exc(), file=sys.stderr, flush=True)
            self.container.get(BootNotices).add(f"{seed.__name__} raised at boot and was skipped: {type(fault).__name__}: {fault}")

    def start(self) -> None:
        self.lifecycle.booting()
        self.server.start()
        self.loaded()
        self.lifecycle.booted()
        self.started()

    def loaded(self) -> None:
        self.share_server.start()
        self.boot()
        self.container.get(SkillFiles).write_all()
        self.container.get(PluginSkills).refresh_all()
        self.container.get(ProfileFiles).write_all()
        self.container.get(Console).build_parsers()
        self.register_jobs()

    def started(self) -> None:
        self.deferred.start()
        self.jobs.start()
        self.container.get(ServiceStart).run()
        self.replacement_announced()
        notices = self.container.get(BootNotices)
        notices.write_boot_seconds(self.container.get(SettingRows).decimal(UpdatesOptions.BOOT_SECONDS))
        notices.announce()
        gc.freeze()

    def replacement_announced(self) -> None:
        if self.standby.replaced_version:
            self.container.get(Announcer).announce(ServerReplaced(previous=self.standby.replaced_version, version=VERSION, time=self.time_source.seconds()))

    def register_jobs(self) -> None:
        self.jobs.register(self.clock)
        self.jobs.register(self.watcher)
        for feature in self.registry.features:
            for job in feature.jobs:
                self.jobs.register(self.container.get(job))

    def run(self) -> None:
        counterpart = self.standby.other_address()
        if counterpart:
            print(f"a journal of this project answers at {counterpart}: waiting until it is gone", flush=True)
        self.standby.blocking_claim()
        self.start()
        while self.server._thread.is_alive():
            self.server._thread.join(1.0)
        self.stop()

    def stop(self) -> None:
        self.server.stop()
        self.share_server.stop()
        self.jobs.stop()
        self.deferred.stop()
        gc.unfreeze()
