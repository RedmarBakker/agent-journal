export const VISIBILITY_GROUPS = [
    {
        title: "Agent",
        kinds: [
            {key: "thoughts", label: "Summaries of the agent's words", icon: "bot"},
            {key: "skills", label: "Skills the agent loads", icon: "book"},
            {key: "agents", label: "Agents talking to each other", icon: "agents"},
            {key: "subagents", label: "Subagents", icon: "agents"},
            {key: "workers", label: "Workers", icon: "agents"},
            {key: "compactions", label: "Conversation compacted", icon: "gauge"},
            {key: "made", label: "Documents the agent made", icon: "docs"},
            {key: "searches", label: "Searches the agent ran", icon: "search"},
            {key: "stuck", label: "Agent stuck", icon: "warn"},
            {key: "acknowledgements", label: "Acknowledged reminders", icon: "check"},
        ],
    },
    {
        title: "Reminders",
        kinds: [
            {key: "rules", label: "Rules", icon: "rules"},
            {key: "facts", label: "Facts", icon: "pins"},
            {key: "reminders", label: "Reminders", icon: "reminders"},
        ],
    },
    {
        title: "Work",
        kinds: [
            {key: "commands", label: "Long commands and outputs", icon: "terminal"},
            {key: "commits", label: "Commits", icon: "branch"},
            {key: "worktrees", label: "Worktrees", icon: "branch"},
            {key: "checks", label: "Checks passing and failing", icon: "check"},
            {key: "questions", label: "Questions asked and answered", icon: "questions"},
            {key: "filed", label: "Filed from your messages", icon: "inbox"},
            {key: "task_moves", label: "Tasks started, finished, paused and blocked", icon: "todos"},
            {key: "conflicts", label: "Your edits a colleague's newer edit replaced", icon: "warn"},
        ],
    },
    {
        title: "The journal",
        kinds: [
            {key: "sequences", label: "Sequences starting and finishing", icon: "list"},
            {key: "sequence_steps", label: "Every step of a sequence", icon: "list"},
            {key: "triggers", label: "Triggers", icon: "bolt"},
            {key: "menus", label: "Menus the journal answered", icon: "bolt"},
            {key: "suggestions", label: "Suggestions", icon: "bulb"},
            {key: "verifiers", label: "Dismissals a verifier checked", icon: "verifier"},
            {key: "plugins", label: "Plugin notes", icon: "plug"},
            {key: "phones", label: "Phones paired", icon: "phone"},
            {key: "requests", label: "Requests filed for you", icon: "inbox"},
            {key: "updates", label: "The journal server replaced by a newer launch", icon: "bolt"},
            {key: "faults", label: "The journal's own faults", icon: "warn"},
            {key: "visitors", label: "Visitor comments", icon: "chat"},
        ],
    },
];

// Which choice above shows or hides each kind of turn the chat draws.
const TURN_KINDS = {thought: "thoughts", receipt: "filed", visitor: "visitors"};
// Which choice above shows or hides a message by the kind in its metadata: a worker's report is the workers' talk.
const MESSAGE_KINDS = {report: "workers"};
// The kinds the agents-talking choice hides together: the agent's dispatches, sends and the reports and marks that come back.
const AGENT_TALK = ["subagents", "workers"];
export const HIDDEN_KEY = "chat_hidden";
export const DEFAULT_HIDDEN = ["acknowledgements", "sequence_steps", "conflicts"];

export const turnKind = (kind) => TURN_KINDS[kind];

export const kindOf = (turn) => {
    if (turn.kind === "message") return turn.acknowledgement ? "acknowledgements" : MESSAGE_KINDS[turn.data?.kind] || "";
    return turn.data?.shows || turnKind(turn.kind) || "";
};

const isAgentTalk = (hidden, kind) => hidden.includes("agents") && AGENT_TALK.includes(kind);

export const visibleIn = (hidden) => (turn) => !hidden.includes(kindOf(turn)) && !isAgentTalk(hidden, kindOf(turn));

export const visibilityChoices = (hidden) =>
    VISIBILITY_GROUPS.map((group) => ({...group, kinds: group.kinds.map((kind) => ({...kind, on: !hidden.includes(kind.key)}))}));

// every chat mark kind, which the Only chat preset hides all at once, leaving the user's and the agent's words, the docks and the pins
export const ALL_MARKS = VISIBILITY_GROUPS.flatMap((group) => group.kinds.map((kind) => kind.key));

// the presets the Show in chat menu offers, each the marks it hides
export const PRESETS = [
    {key: "chat", label: "Only chat", icon: "chat", hidden: ALL_MARKS},
    {key: "context", label: "Chat with context", icon: "list", hidden: DEFAULT_HIDDEN},
];

export const presetOf = (hidden) => PRESETS.find((preset) => preset.hidden.length === hidden.length && preset.hidden.every((key) => hidden.includes(key)))?.key ?? "";

export const toggled = (hidden, key) => (hidden.includes(key) ? hidden.filter((k) => k !== key) : [...hidden, key]);
