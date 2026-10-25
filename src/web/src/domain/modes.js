// How the agent shares its work with workers, as the plan bar's buttons offer it; the journal keeps it as workers.mode.
export const MODES = [
    {key: "builder", label: "Builder", note: "The agent builds the work itself and sends workers for jobs better done beside it."},
    {key: "orchestrator", label: "Orchestrator", note: "The agent plans, hands tasks to workers and reviews their work."},
    {key: "solo", label: "Solo", note: "The agent does all the work itself, with no workers."},
];

export const DEFAULT_MODE = "builder";

// The settings each mode's button shows as toggles in its hover panel, below its one line; every one is the user's to set.
// Each names the setting it saves, by its feature and its name, and the value it has when the user never set it.
const ORCHESTRATOR_TOGGLES = [
    {feature: "workers", name: "orchestrator_writes_plans", label: "May write plans", fallback: true},
    {feature: "workers", name: "orchestrator_approves_plans", label: "Approves plans", fallback: false},
    {feature: "workers", name: "orchestrator_approves_others_plans", label: "Approves only plans it did not write", fallback: false},
    {feature: "workers", name: "orchestrator_releases", label: "May release", fallback: false},
    {feature: "reviewing", name: "reviewer", label: "Reviewer", fallback: false},
];
const MODE_TOGGLES = {orchestrator: ORCHESTRATOR_TOGGLES};

export const modeToggles = (mode) => MODE_TOGGLES[mode] || [];

// whether a toggle's setting is on, as the user set it or by its value when never set
export const toggleOn = (toggle, settings) => {
    const value = settings && settings[toggle.feature] && settings[toggle.feature][toggle.name];
    return value === undefined || value === null ? toggle.fallback : Boolean(value);
};

// How workers test, as the workers list offers it; the journal keeps it as workers.testing, by these words.
export const TESTINGS = [
    {key: "Hand the tests over", label: "Hand the tests over", note: "A worker never runs a test; each proof names the test and the command that runs it, and the agent that merges runs them."},
    {key: "Run the tests it wrote", label: "Run the tests it wrote", note: "A worker runs the tests it wrote, by name, never the full suite."},
];

export const DEFAULT_TESTING = TESTINGS[0].key;
