// How the agent shares its work with workers, as the plan bar's buttons offer it; the journal keeps it as workers.mode.
export const MODES = [
    {key: "builder", label: "Builder", note: "The agent builds the work itself and sends workers for jobs better done beside it."},
    {key: "orchestrator", label: "Orchestrator", note: "The agent plans, hands tasks to workers and reviews their work."},
    {key: "solo", label: "Solo", note: "The agent does all the work itself, with no workers."},
];

export const DEFAULT_MODE = "builder";

// The settings each mode's button shows in its hover panel, below its one line, each with a line saying what it does; every one is the user's to set.
// Each names the setting it saves, by its feature and its name, and the value it has when the user never set it; a switch's children are a choice shown under it while it is on.
const ORCHESTRATOR_TOGGLES = [
    {feature: "workers", name: "orchestrator_writes_plans", label: "May write plans", note: "Drafts plans itself with journal plan create. Off, only you write a plan.", fallback: true},
    {
        feature: "workers",
        name: "orchestrator_approves_plans",
        label: "Approves plans",
        note: "Approves plans itself with journal plan approve. Off, only you approve a plan.",
        fallback: false,
        children: {
            feature: "workers",
            name: "orchestrator_plan_approval",
            fallback: "can approve all plans",
            choices: [
                {value: "can approve only its own plans", label: "Only its own"},
                {value: "can approve plans the user made", label: "Plans you made"},
                {value: "can approve all plans", label: "All plans"},
            ],
        },
    },
    {feature: "workers", name: "orchestrator_releases", label: "May release", note: "Tags a version and publishes a release. Off, a git tag or gh release waits for you.", fallback: false},
    {feature: "reviewing", name: "reviewer", label: "Reviewer", note: "A reviewer reads each worker's proofs and runs their tests before you merge.", fallback: false},
];
const MODE_TOGGLES = {orchestrator: ORCHESTRATOR_TOGGLES};

export const modeToggles = (mode) => MODE_TOGGLES[mode] || [];

// a toggle's setting, as the user set it or by its value when never set
export const toggleValue = (toggle, settings) => {
    const value = settings && settings[toggle.feature] && settings[toggle.feature][toggle.name];
    return value === undefined || value === null ? toggle.fallback : value;
};

// whether a switch's setting is on
export const toggleOn = (toggle, settings) => Boolean(toggleValue(toggle, settings));

// How workers test, as the workers list offers it; the journal keeps it as workers.testing, by these words.
export const TESTINGS = [
    {key: "Hand the tests over", label: "Hand the tests over", note: "A worker never runs a test; each proof names the test and the command that runs it, and the agent that merges runs them."},
    {key: "Run the tests it wrote", label: "Run the tests it wrote", note: "A worker runs the tests it wrote, by name, never the full suite."},
];

export const DEFAULT_TESTING = TESTINGS[0].key;
