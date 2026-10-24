from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ProfilesNudges:
    """The nudges of the profiles feature."""

    WORKER_PROFILE_MISUSE = Nudge("profiles", "worker_profile_is_not_a_subagent", "{{name}} is a worker profile", "`journal worker dispatch \"<Name>\" --task <n> --profile {{name}}`", repeat=Timeout.seconds(0))
