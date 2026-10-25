from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class UpdatesNudges:
    RELEASE_MESSAGES = Nudge("updates", "release_messages", "{{count}} unread release messages", "`journal update messages`, and do what they ask", repeat=Timeout.seconds(0))
    LAUNCH_TAKEOVER = Nudge("updates", "launch_carried_over", "the journal now runs version {{version}}: a newer launch replaced the journal server on {{previous}} that your launch had", repeat=Timeout.seconds(0), is_remark=True)
