from journal.support.card_outcome import CardOutcome
import shlex

from journal.console.console import Console
from journal.support.caller import Caller
from journal.events.announcer import Announcer
from journal.events.moments.plugin_card_requested import PluginCardRequested
from journal.features.plugins.support.plugin_steps import PluginSteps
from journal.features.plugins.support.plugin_text import PluginText
from journal.support.actor import Actor
from journal.models.entry import Entry
from journal.models.plugin import Plugin
from journal.features.plugins.support.plugin_answer import PluginAnswer
from journal.features.plugins.support.plugin_card import PluginCard
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.features.skills.support.requirements import Requirements
from journal.features.skills.support.skill_files import SkillFiles

COMMAND = "plugin_command"
WARNING = "plugin_warning"


# the tones a plugin names its cards in, as the outcome the viewer colours
TONE_OUTCOMES = {"good": CardOutcome.PASSED, "warn": CardOutcome.WARNED, "bad": CardOutcome.FAILED, "danger": CardOutcome.FAILED, "running": CardOutcome.RUNNING}


class PluginAnswers:
    """What a plugin's answer asks beyond the hook's reply: its cards in the chat, a moment card each, or a process card, PluginProcessCard, for one with a key, replacing the earlier of that key where it stands if the user has not written since, else at the bottom of the chat, its journal commands run as the plugin, a step deeper, and the skills of its own it requires owed by the agent that has not read them; an id it does not publish, like a key the journal does not know, is a warning written once."""

    def __init__(self, announcer: Announcer, console: Console, entries: Entries, steps: PluginSteps, text: PluginText, files: SkillFiles, requirements: Requirements, agents: Agents) -> None:
        self.announcer, self.console, self.entries, self.steps, self.text = announcer, console, entries, steps, text
        self.files, self.requirements, self.agents = files, requirements, agents
        self.warnings: set[tuple[str, str]] = set()

    def apply(self, plugin: Plugin, answer: PluginAnswer, environment: str, environment_id: int, session: str) -> None:
        for card in answer.cards:
            self.show(plugin, card, environment_id)
        with self.steps.deeper():
            for line in answer.commands:
                self.run(plugin, line, environment, environment_id)
        if answer.require_skills:
            self.required(plugin, tuple(dict.fromkeys(answer.require_skills)), session, environment_id)

    def required(self, plugin: Plugin, names: tuple[str, ...], session: str, environment_id: int) -> None:
        published = {skill.name: skill for skill in self.files.published() if skill.plugin == plugin.name}
        unknown = [name for name in names if name not in published]
        if unknown:
            self.warn(plugin, environment_id, f"it requires skills it does not publish, ignored: {', '.join(unknown)}")
        skills = [published[name] for name in names if name in published]
        for agent in self.agents.active_session_agents(session):
            self.requirements.obligation(agent, self.requirements.obligations(agent, skills))

    def warn(self, plugin: Plugin, environment_id: int, warning: str) -> None:
        if (plugin.name, warning) in self.warnings:
            return
        self.warnings.add((plugin.name, warning))
        self.entries.save(Entry(environment_id=environment_id, entry_type=WARNING, actor=Actor.plugin(plugin.name), data={"plugin": plugin.name, "warning": warning}), Actor.plugin(plugin.name))

    def show(self, plugin: Plugin, card: PluginCard, environment_id: int) -> None:
        type_name = plugin.manifest.card_kind(card.card_type)
        label = self.text.plain(card.label or type_name.label)
        data = {"kind": "plugin", "plugin": plugin.name, "card": card.card_type, "outcome": str(TONE_OUTCOMES.get(card.tone or type_name.tone, CardOutcome.NONE)), "collapsed": type_name.collapsed}
        self.announcer.announce(PluginCardRequested(environment_id=environment_id, plugin=plugin.name, label=label, data=data, detail=self.text.plain(card.detail), card_key=card.key))

    def run(self, plugin: Plugin, line: str, environment: str, environment_id: int) -> None:
        argv = shlex.split(line)
        if argv[:1] != ["journal"]:
            self.record(plugin, line, environment_id, 1, "a plugin runs journal commands only")
            return
        outcome = self.console.run(argv[1:], Caller.plugin(environment or "main", plugin.name))
        self.record(plugin, line, environment_id, outcome.code, outcome.error.strip()[-300:])

    def record(self, plugin: Plugin, line: str, environment_id: int, code: int, err: str) -> None:
        self.entries.save(Entry(environment_id=environment_id, entry_type=COMMAND, actor=Actor.plugin(plugin.name), data={"plugin": plugin.name, "command": line, "code": code, "err": err}), Actor.plugin(plugin.name))
