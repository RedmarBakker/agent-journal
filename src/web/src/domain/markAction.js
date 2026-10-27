import {meta} from "./tables.js";

// what a mark's one-click action opens, named for the kind of thing it opens: Open the task, Open the output, Open the agent
const OWN_WORDS = {outputs: "output", skills: "skill", agents: "agent", subagents: "agent", pages: "page"};

export const actionLabel = (table) => `Open the ${OWN_WORDS[table] || meta(table)?.title.toLowerCase() || "row"}`;

// the action of a mark whose card names a row, by the row's ref as tasks:12
export const refAction = (ref) => actionLabel(String(ref).split(":")[0]);
