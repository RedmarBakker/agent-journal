from tests.simulation.scenario import Scenario

QUIET_BUILDER = Scenario("a quiet builder", "builder", 30, 4, 1, 600, "builder")
FLOODED_BUILDER = Scenario("a builder under a flood of messages", "builder", 30, 4, 30, 600, "builder")
ORCHESTRATOR = Scenario("an orchestrator with five tasks and three places", "orchestrator", 30, 5, 2, 600, "orchestrator")
SOLO = Scenario("solo", "solo", 30, 3, 1, 600, "solo")
CARELESS = Scenario("a careless agent", "builder", 20, 4, 4, 300, "careless")
ENGINE_MOMENTS = Scenario("a builder through the engine's own moments", "builder", 30, 4, 2, 600, "builder", engine_events_hourly=40)
# the measured week of doc 1065, section 7: a worker's job in minutes by decile, and the shares of jobs sent back once, twice and three times
JOB_DECILES = (0.7, 1.0, 1.5, 2.1, 3.0, 4.2, 5.4, 7.2, 10.3)
SEND_BACK_SHARES = (0.30, 0.08, 0.03)
# fifty tasks inside sixty minutes, gaps of nought to five minutes drawn once and kept, as the largest bursts of the week came
SPREE_ARRIVALS = ((0, 6), (2, 4), (3, 5), (5, 3), (7, 4), (10, 2), (12, 5), (15, 3), (20, 4), (21, 2), (26, 3), (30, 2), (33, 1), (40, 2), (45, 1), (52, 2), (60, 1))
HISTORY_MINUTES = 180
TASK_SPREE = tuple(Scenario(f"last week's task spree, {mode}", mode, HISTORY_MINUTES, 0, 2, 180, mode, arrivals=SPREE_ARRIVALS, job_minutes=JOB_DECILES) for mode in ("builder", "orchestrator", "solo"))
MESSAGES_WHILE_WORKING = tuple(Scenario(f"last week's messages while working, {mode}", mode, HISTORY_MINUTES, 10, 30, 180, mode, job_minutes=JOB_DECILES) for mode in ("builder", "orchestrator", "solo"))
SEND_BACK_LOOP = Scenario("last week's send-back loop", "orchestrator", HISTORY_MINUTES, 15, 2, 180, "orchestrator", job_minutes=JOB_DECILES, send_backs=SEND_BACK_SHARES)
CLASH_CASCADE = Scenario("a clash cascade", "orchestrator", HISTORY_MINUTES, 15, 2, 180, "orchestrator", job_minutes=JOB_DECILES, clashes_per_merge=99)
LONG_JOBS = Scenario("last week's job lengths three times over", "orchestrator", HISTORY_MINUTES, 15, 2, 180, "orchestrator", job_minutes=tuple(minutes * 3 for minutes in JOB_DECILES))
HEREDOC_BUILDER = Scenario("a builder writing all its code through the shell", "builder", HISTORY_MINUTES, 15, 2, 180, "heredoc", job_minutes=JOB_DECILES)
MODE_SWITCH = Scenario("a builder switched to orchestrator at minute 60", "builder", HISTORY_MINUTES, 20, 2, 180, "builder", job_minutes=JOB_DECILES, switch_minute=60, switch_mode="orchestrator")
HISTORY = (*TASK_SPREE, *MESSAGES_WHILE_WORKING, SEND_BACK_LOOP, CLASH_CASCADE, LONG_JOBS, HEREDOC_BUILDER, MODE_SWITCH)

ALL = (QUIET_BUILDER, FLOODED_BUILDER, ORCHESTRATOR, SOLO, CARELESS, ENGINE_MOMENTS, *HISTORY)
BUILDER_SPREE = Scenario("a builder given a spree of tasks", "builder", 120, 30, 30, 180, "builder")
BUILDER_SPREE_HANDED_OUT = Scenario("a builder that hands a spree of tasks out", "builder", 120, 30, 30, 180, "orchestrator")
ORCHESTRATOR_SPREE = Scenario("an orchestrator given a spree of tasks", "orchestrator", 120, 30, 30, 180, "orchestrator")
ORCHESTRATOR_SPREE_WRITTEN = Scenario("an orchestrator that writes a spree of tasks itself", "orchestrator", 120, 30, 30, 180, "builder")
SOLO_SPREE = Scenario("solo given a spree of tasks", "solo", 120, 30, 30, 180, "solo")
SOLO_SPREE_HANDED_OUT = Scenario("solo that tries to hand a spree of tasks out", "solo", 120, 30, 30, 180, "orchestrator")
KNOWN_PAIRS = ((BUILDER_SPREE, BUILDER_SPREE_HANDED_OUT), (ORCHESTRATOR_SPREE, ORCHESTRATOR_SPREE_WRITTEN), (SOLO_SPREE, SOLO_SPREE_HANDED_OUT))
