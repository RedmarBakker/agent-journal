from journal.support.option import Option


class FitnessOptions:
    """The options of the fitness the workers feature measures."""

    WARNINGS = Option("workers.fitness_warnings", "Fitness warnings to the agent", "Whether the agent is sent the lines about its fitness: a score under its threshold, a fall past a mark, and the points a quick report or a tiny job cost; off, the score is still measured and shown, and nothing about it reaches the agent", True)
    LEVEL_STEP = Option("workers.fitness_level_step", "Fitness drop told at every", "The fitness score falls past a multiple of this many points, such as 95 and 90, and the agent is told once with the measures off their range; 0 turns this off", 5, unit="points")
