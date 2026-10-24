from journal.engine.nudge import Nudge


class SecretsNudges:
    """The nudges of the secrets feature."""

    PRIVATE_SECRETS = Nudge("secrets", "secrets_out_of_reach", "secrets are out of your reach", "pass one to a program with `journal secret run <n> -- <program>`", repeat_interval=0)
    SECRET_PROGRAM_GRANT = Nudge("secrets", "secret_allowed_for_programs", "the user let secret {{n}}, {{title}}, go to {{programs}}", "run it with `journal secret run {{n}} -- <program> ...`", repeat_interval=0)
