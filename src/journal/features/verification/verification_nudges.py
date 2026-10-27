from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class VerificationNudges:
    VERIFIER_REFUSAL = Nudge("verification", "verifier_gives_only_its_verdict", "you are a verifier: answer only with `journal verdict yes \"<reason>\"` or `journal verdict no \"<reason>\"`", "", repeat=Timeout.seconds(0))
