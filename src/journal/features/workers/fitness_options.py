from journal.support.option import USER, Option


class FitnessOptions:
    """The options of the fitness the workers feature measures."""

    WARNINGS = Option("workers.fitness_warnings", "Fitness warnings to the agent", "Whether the agent is sent the lines about its fitness: a score under its threshold, a fall past a mark, and the points a quick report or a tiny job cost; off, the score is still measured and shown, and nothing about it reaches the agent", False, kind="switch", setter=USER)
    ORCHESTRATOR_HIGH_ENTRY = Option("workers.orchestrator_high_entry", "Orchestrator band turns high at", "The worker queue at which the orchestrator's band becomes high", 0.8)
    ORCHESTRATOR_HIGH_EXIT = Option("workers.orchestrator_high_exit", "Orchestrator band leaves high under", "The worker queue under which the orchestrator's band leaves high", 0.65)
    ORCHESTRATOR_LOW_ENTRY = Option("workers.orchestrator_low_entry", "Orchestrator band turns low under", "The worker queue under which the orchestrator's band becomes low", 0.5)
    ORCHESTRATOR_LOW_EXIT = Option("workers.orchestrator_low_exit", "Orchestrator band leaves low at", "The worker queue from which the orchestrator's band leaves low", 0.65)
    BUILDER_HIGH_ENTRY = Option("workers.builder_high_entry", "Builder band turns high at", "The worker queue at which the builder's band becomes high, its ceiling", 0.5)
    BUILDER_HIGH_EXIT = Option("workers.builder_high_exit", "Builder band leaves high under", "The worker queue under which the builder's band leaves high", 0.4)
    BUILDER_LOW_ENTRY = Option("workers.builder_low_entry", "Builder band turns low under", "The worker queue under which the builder's band becomes low", 0.3)
    BUILDER_LOW_EXIT = Option("workers.builder_low_exit", "Builder band leaves low at", "The worker queue from which the builder's band leaves low", 0.4)
    BUILDER_ACTIVE_WORKERS = Option("workers.builder_active_workers", "Builder: most active workers", "The mean number of active workers over an hour, at work or waiting to be checked, past which the builder's active-workers measure fails", 2)
    WRITE_BLOCK_MINUTES = Option("workers.write_block_minutes", "Minutes the worker queue stands high before writes wait", "The minutes the worker queue held high may fail before the agent's writes wait until it clears the oldest worker; reads and journal commands go through", 15, unit="min")
    SCORE_WARMUP_MINUTES = Option("workers.score_warmup_minutes", "Minutes measured before a score", "The minutes a work mode is measured before the agent's fitness is scored in it", 30, unit="min")
    BAND_MINUTES = Option("workers.band_minutes", "Least minutes in a band", "The minutes a band stays before it changes again, but for leaving high on an empty queue", 10, unit="min")
    EMPTY_QUEUE_MINUTES = Option("workers.empty_queue_minutes", "Empty worker queue leaves high after", "The minutes the worker queue stands empty before a high band leaves high", 5, unit="min")

