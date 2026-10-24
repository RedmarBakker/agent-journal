from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class VerificationNudges:
    VERIFIER_REFUSAL = Nudge("verification", "verifier_gives_only_its_verdict", "you are a verifier: you only give your verdict, `journal verdict yes|no \"<reason>\"`", "every other tool and every file edit is refused; the evidence is all in your brief", repeat=Timeout.seconds(0))
