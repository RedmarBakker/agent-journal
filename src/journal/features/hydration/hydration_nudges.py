from journal.engine.nudge import Nudge


class HydrationNudges:
    READ_CHAT = Nudge("hydration", "read_the_hydrated_chat", "this environment's chat was filled from the earlier conversation {{session}}, which this session carries on", "read it with journal message recent, then record what it holds that is still true or still open as facts, reminders and tasks")
