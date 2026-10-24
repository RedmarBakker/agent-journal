from journal.features.feature import Feature
from journal.features.triggers.commands.trigger_command import TriggerCommand
from journal.features.triggers.listeners.watch_prompt import WatchPrompt
from journal.features.triggers.listeners.watch_message import WatchMessage
from journal.features.triggers.listeners.watch_tool import WatchTool
from journal.features.triggers.listeners.trigger_card import TriggerCard
from journal.features.triggers.triggers_conduct import TriggersConduct
from journal.features.triggers.support.triggers_data_reader import TriggersDataReader
from journal.features.triggers.support.triggers_data import TriggersData
from journal.features.triggers.triggers_part import TriggersPart
from journal.features.triggers.triggers_nudges import TriggersNudges


class Triggers(Feature[TriggersData]):
    name = TriggersPart.name
    title = "Triggers"
    help = "Words you choose, and what the journal does when one comes up."
    commands = (TriggerCommand,)
    listeners = (WatchPrompt, WatchTool, WatchMessage, TriggerCard)
    data = (TriggersDataReader,)
    conduct = (TriggersConduct,)

    nudges = (TriggersNudges.NUDGE, TriggersNudges.INSTRUCT, TriggersNudges.DENIED)
