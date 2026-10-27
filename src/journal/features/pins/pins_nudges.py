from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PinsNudges:
    LINK_PIN_REQUEST = Nudge("pins", "pin_the_link", "pin {{url}} if the user will return to it: `journal notice create \"<what>\" --link \"{{url}}\"`", "", repeat=Timeout.seconds(0))
    UNPINNED_CLAIM = Nudge("pins", "pin_claimed_unmade", "no link was pinned", "pin it with `journal notice create \"<what it is>\" --link \"<url>\" --label \"<Open ...>\"`", repeat=Timeout.seconds(0))
