import time
from functools import partial

from journal.events.listener import Listener
from journal.events.worker_merge_event import WorkerMergeEvent
from journal.features.plugins.support.plugin_relay import PluginRelay
from journal.features.plugins.support.protocol import Protocol
from journal.features.plugins.support.merge_queue import MergeQueue
from journal.features.plugins.support.plugin_answer import PluginAnswer
from journal.features.workers.support.merge_statuses import MergeStatuses
from journal.models.plugin import Plugin
from journal.repositories.setting_rows import SettingRows
from journal.support.decision import Decision
from journal.support.listener_queue import ListenerQueue
from journal.features.plugins.plugins_options import PluginsOptions


# the least time a plugin is given to answer once a place came late in its window
PLACE_SECONDS_LEAST = 0.05

class PluginMergeRelay(Listener[WorkerMergeEvent]):
    """The plugins that receive a worker's merge: one that listens for worker_merging is asked before the branch is merged, inside its window capped by the merge window setting, which bounds both the wait for a place among the merges asked about at once and the answer, and its refusal blocks the merge with its reason; every other one receives it, and worker_merge_landed, after the reply."""

    def __init__(self, relay: PluginRelay, deferred: ListenerQueue, settings: SettingRows, queue: MergeQueue, statuses: MergeStatuses) -> None:
        self.relay, self.deferred, self.settings, self.queue, self.statuses = relay, deferred, settings, queue, statuses

    def handle(self, event: WorkerMergeEvent) -> Decision:
        ceiling_ms = event.window(self.settings.integer(PluginsOptions.PLUGIN_ANSWER_WINDOW))
        decision = Decision()
        for plugin in self.relay.listeners(event, event.environment_id):
            key = Protocol.published_name(event)
            if decision.allowed and plugin.manifest.has_window(key):
                window_ms = plugin.manifest.window_ms(key, ceiling_ms)
                answer = self.plugin_answer(plugin, event.with_window(window_ms), window_ms)
                decision = decision.merged(Decision.refuse(f"{plugin.name}: {answer.reason}") if answer.answer == "refuse" else Decision())
            else:
                self.deferred.add_bounded(partial(self.relay.postponed, plugin, event, event.environment_id), f"{plugin.name} relay {key}")
        return decision

    def plugin_answer(self, plugin: Plugin, event: WorkerMergeEvent, window_ms: int) -> PluginAnswer:
        began, window = time.monotonic(), window_ms / 1000
        if not self.queue.has_place():
            self.statuses.report(event.worker, "", f"waiting in the merge queue behind {self.queue.asked} merges")
        with self.queue.place(window) as placed:
            if not placed:
                self.relay.unanswered(plugin, event, event.environment_id, f"no place to ask it within the {window:g} seconds of the merge window, {self.queue.asked} merges were being asked about")
                return PluginAnswer()
            return self.relay.ask(plugin, event, event.environment_id, max(window - (time.monotonic() - began), PLACE_SECONDS_LEAST), partial(self.statuses.report, event.worker, plugin.name))
