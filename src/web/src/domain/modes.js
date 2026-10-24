// How the agent shares its work with workers, as the plan bar's buttons offer it; the journal keeps it as workers.mode.
export const MODES = [
    {key: "builder", label: "Builder", note: "The agent builds it itself, and sends workers when a job is better done beside it."},
    {key: "orchestrator", label: "Orchestrator", note: "The agent plans, hands the work to workers, then reviews and merges it; it writes code only for reviews and small fixes."},
    {key: "solo", label: "Solo", note: "The agent does everything itself, with no workers."},
];

export const DEFAULT_MODE = "builder";

// How workers test, as the workers list offers it; the journal keeps it as workers.testing, by these words.
export const TESTINGS = [
    {key: "Hand the tests over", label: "Hand the tests over", note: "A worker never runs a test; each proof names the test and the command that runs it, and the agent that merges runs them."},
    {key: "Run the tests it wrote", label: "Run the tests it wrote", note: "A worker runs the tests it wrote, by name, never the full suite."},
];

export const DEFAULT_TESTING = TESTINGS[0].key;
