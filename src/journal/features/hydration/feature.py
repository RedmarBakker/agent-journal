from journal.engine.nudge import Nudge
from journal.features.feature import Feature
from journal.features.hydration.hydration_conduct import HydrationConduct
from journal.features.hydration.listeners.reading_request_record import ReadingRequestRecord
from journal.features.hydration.support.hydration_data import HydrationData
from journal.features.hydration.support.hydration_data_reader import HydrationDataReader


class Hydration(Feature[HydrationData]):
    """A new environment's chat filled from a conversation an agent program stored for this project, carried on by the environment's first launch."""

    name = "hydration"
    title = "Hydration"
    help = "A new environment can start from a Claude Code or Codex conversation kept on this machine: its prompts and replies fill the chat at their own times, its tool calls folded into short lines, and the first launch carries the conversation on. The first agent there is asked once to read that chat and record the facts and open work it holds."
    data = (HydrationDataReader,)
    conduct = (HydrationConduct,)
    listeners = (ReadingRequestRecord,)

    READ_CHAT = Nudge(name, "read_the_hydrated_chat", "this environment's chat was filled from the earlier conversation {{session}}, which this session carries on", "read it with journal message recent, then record what it holds that is still true or still open as facts, reminders and tasks")
    nudges = (READ_CHAT,)
