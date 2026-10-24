from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PinsNudges:
    LINK_PIN_REQUEST = Nudge("pins", "pin_the_link", "{{url}} is not pinned", "pin it if the user will come back to it: `journal notice create \"<what it is>\" --link \"{{url}}\" --label \"<Open ...>\"`", repeat=Timeout.seconds(0))
    UNPINNED_CLAIM = Nudge("pins", "pin_claimed_unmade", "you told the user a link is pinned, but no pin was made in the last minute", "pin it now with `journal notice create \"<what it is>\" --link \"<url>\" --label \"<Open ...>\"`, or tell the user where to find it instead", repeat=Timeout.seconds(0))
