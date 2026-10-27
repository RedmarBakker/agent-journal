from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class SecretsNudges:
    """The nudges of the secrets feature."""

    PRIVATE_SECRETS = Nudge("secrets", "secrets_out_of_reach", "you cannot read secrets", "pass one to a program with `journal secret run <n> -- <program>`", repeat=Timeout.seconds(0))
    SECRET_PROGRAM_GRANT = Nudge("secrets", "secret_allowed_for_programs", "the user allowed secret {{n}} for {{programs|cap=30}}", "use it with `journal secret run {{n}} -- <program> ...`", repeat=Timeout.seconds(0))
