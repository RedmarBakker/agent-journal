from journal.engine.nudge import Nudge


class HydrationNudges:
    READ_CHAT = Nudge("hydration", "read_the_hydrated_chat", "chat filled from {{session}}", "read `journal message recent`; save what still applies as memories or tasks")
