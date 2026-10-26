from journal.support.agent_role import AgentRole
from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import JOURNAL
from journal.support.card_kind import CardKind
from journal.support.card_colouring import CardColouring
from journal.features.feature import Feature
from journal.support.skill import Skill
from journal.features.plugins.commands.dashboard_command import DashboardCommand
from journal.features.plugins.commands.plugin_command import PluginCommand
from journal.features.plugins.listeners.plugin_broken_notice import PluginBrokenNotice
from journal.features.plugins.listeners.plugin_agent_relay import PluginAgentRelay
from journal.features.plugins.listeners.plugin_merge_relay import PluginMergeRelay
from journal.features.plugins.listeners.plugin_moment_cards import PluginMomentCards
from journal.features.plugins.listeners.plugin_question_cards import PluginQuestionCards
from journal.features.plugins.listeners.plugin_proposal_card import PluginProposalCard
from journal.features.plugins.listeners.plugin_row_relay import PluginRowRelay
from journal.features.plugins.listeners.plugin_settings_notice import PluginSettingsNotice
from journal.features.plugins.seeds.plugin_services_seed import PluginServicesSeed
from journal.features.plugins.plugins_conduct import PluginsConduct
from journal.features.plugins.support.plugins_data_reader import PluginsDataReader
from journal.features.plugins.support.plugins_data import PluginsData
from journal.features.plugins.listeners.release_upgrade import ReleaseUpgrade
from journal.features.plugins.support.plugin_process_card import PluginProcessCard
from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.plugins.plugins_options import PluginsOptions
from journal.features.plugins.plugins_part import PluginsPart


class PluginsFeature(Feature[PluginsData]):
    name = PluginsPart.name
    helper_listeners = {role: (PluginAgentRelay,) for role in AgentRole.helpers()}
    card_families = (CardFamily("plugins", "Plugins", "plug", JOURNAL, CardColouring.OUTCOME),)
    card_kinds = (MarkKind(CardKind.PLUGINS, "Plugin notes", "plugins"),)
    title = "Plugins"
    help = "Programs you install that hear the journal's events and answer them: refuse a tool, say a line to the agent, show a card or run journal commands, each as itself."
    options = (PluginsOptions.PLUGIN_ANSWER_WINDOW, PluginsOptions.CLOCK_OUT_WINDOW_SECONDS, PluginsOptions.STREAK_LIMIT, PluginsOptions.IGNORE_MINUTES)
    process_cards = (PluginProcessCard,)
    listeners = (PluginAgentRelay, PluginRowRelay, PluginMergeRelay, PluginMomentCards, PluginQuestionCards, PluginProposalCard, PluginSettingsNotice, ReleaseUpgrade, PluginBrokenNotice)
    data = (PluginsDataReader,)
    conduct = (PluginsConduct,)
    nudges = (PluginsNudges.PLUGIN_FILE_OWNERSHIP, PluginsNudges.PLUGIN_BROKEN)
    commands = (PluginCommand, DashboardCommand)
    seeds = (PluginServicesSeed,)
    skill = Skill("plugins", "Plugins the user installs that receive the journal's events; load it when a plugin blocks you, a plugin's card or line appears, or a plugin would help", """
# Plugins

A plugin is a program the user installs that receives the journal's events and answers them: it may block a tool or a
stop, send you a line, show a card in the chat or run journal commands as itself. Its text reaches you as
`[plugin <name>] ...`; it is a plugin's, never the user's and never the journal's own.

- `journal plugin list` shows what is installed, whether each is on, and how it last failed.
  `journal plugin settings <name>` shows a plugin's settings.
- A plugin's block is followed like any other: do what it asks, or tell the user why you cannot. A journal command and
  the read of a skill always go through.
- Install, enable, disable, configure and remove are the user's to run; an installed plugin's upgrade is yours, with
  `journal plugin upgrade <name> --yes`. When a new plugin would help, propose it:
  `journal plugin propose <folder or git address> --why "<what for>"` shows the user a card with all it would run.
- Never write into `.journal/plugins`: an installed plugin's files are the user's to change. A plugin's own folder,
  when the user asks you to work on it, is yours to change; the journal switches the plugin off until the user has
  read the change.
- Writing a plugin: docs/plugins.md describes all of it, the manifest, the line in and the line out.
""", keywords=("plugin", "plugins"), commands=('plugin',))
