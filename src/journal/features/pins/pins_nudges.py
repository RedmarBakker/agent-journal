from journal.engine.nudge import Nudge


class PinsNudges:
    LINK_PIN_REQUEST = Nudge("pins", "pin_the_link", "{{url}} is not pinned", "pin it if the user will come back to it: `journal notice create \"<what it is>\" --link \"{{url}}\" --label \"<Open ...>\"`", repeat_interval=0)
    UNPINNED_CLAIM = Nudge("pins", "pin_claimed_unmade", "you told the user a link is pinned, but no pin was made in the last minute", "pin it now with `journal notice create \"<what it is>\" --link \"<url>\" --label \"<Open ...>\"`, or tell the user where to find it instead", repeat_interval=0)
