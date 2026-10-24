from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class UpdatesNudges:
    RELEASE_MESSAGES = Nudge("updates", "release_messages", "{{count}} unread release messages", "`journal update messages`, and do what they ask", repeat=Timeout.seconds(0))
