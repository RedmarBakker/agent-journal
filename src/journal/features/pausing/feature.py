from journal.features.feature import Feature
from journal.features.pausing.states.user_pause import UserPause
from journal.features.pausing.pausing_conduct import PausingConduct
from journal.features.pausing.pausing_nudges import PausingNudges


class PausingFeature(Feature):
    NAME = "pausing"

    name = NAME
    title = "Pausing the agent"
    fixed = True
    help = "The pause button on the top bar holds the agent: it finishes the step it is on, then waits until you resume it or write to it."
    states = (UserPause,)
    conduct = (PausingConduct,)
    nudges = (PausingNudges.PAUSED, PausingNudges.RESUMED)
