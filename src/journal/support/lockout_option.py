from journal.support.option import Option

LOCKOUT_OPTION = Option("workers.lockout_seconds", "Seconds a worker waits for a journal that stopped answering", "A worker whose journal stops answering holds every tool for this long, asking again, and ends once it passes without an answer; the main agent's hooks go on while the journal is down", 30, unit="seconds")
