from journal.support.option import USER, Option


class SecretsOptions:
    LONGEST_RUN_SECONDS = Option("secrets.longest_run_seconds", "Longest time a secret program may run", "Seconds a program given a secret may run before it is stopped", 120, unit="seconds", setter=USER)
