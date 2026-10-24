from journal.engine.nudge import Nudge


class UpdatesNudges:
    RELEASE_MESSAGES = Nudge("updates", "release_messages", "{{count}} unread release messages", "`journal update messages`, and do what they ask", repeat_interval=0)
