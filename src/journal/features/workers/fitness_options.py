from journal.support.option import Option


class FitnessOptions:
    """The options of the fitness the workers feature measures."""

    LEVEL_STEP = Option("workers.fitness_level_step", "Fitness drop told at every", "The fitness score falls past a multiple of this many points, such as 95 and 90, and the agent is told once with the measures off their range; 0 turns this off", 5, unit="points")
