from tests.simulation.scenario import Scenario

QUIET_BUILDER = Scenario("a quiet builder", "builder", 30, 4, 1, 600, "builder")
FLOODED_BUILDER = Scenario("a builder under a flood of messages", "builder", 30, 4, 30, 600, "builder")
ORCHESTRATOR = Scenario("an orchestrator with five tasks and three places", "orchestrator", 30, 5, 2, 600, "orchestrator")
SOLO = Scenario("solo", "solo", 30, 3, 1, 600, "solo")
CARELESS = Scenario("a careless agent", "builder", 20, 4, 4, 300, "careless")
ENGINE_MOMENTS = Scenario("a builder through the engine's own moments", "builder", 30, 4, 2, 600, "builder", engine_events_hourly=40)
ALL = (QUIET_BUILDER, FLOODED_BUILDER, ORCHESTRATOR, SOLO, CARELESS, ENGINE_MOMENTS)
