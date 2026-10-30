import {updatedAt} from "./row.js";

// A team's hub is an environment of kind hub, named for the team; what the team's colleagues share and the Team chat are its sessions.
export const isHub = (row) => row.environment_type === "hub";

const isGeneratedAgentEnvironment = (row) => row.generated_for === "plan" || row.generated_for === "task";

// Generated plan/task environments and every child open through their plan or Role page.
const topLevelEnvironments = (rows) => rows.filter((row) => !isGeneratedAgentEnvironment(row) && !row.parent_key);

// The sidebar shows each top-level work environment apart from a hub.
export const ownEnvironments = (rows) => topLevelEnvironments(rows).filter((row) => !isHub(row));

export const inHub = (rows, hub) => rows.filter((row) => row.environment_id === hub.id);

// Where a row made in the open environment lands, said in the New dialog of a journal in a team: on the team's hub, or kept in the environment on this machine; nothing in a journal with no hub.
export function destination(environment, environments) {
    if (!environment || !environments.some(isHub)) {
        return "";
    }
    return isHub(environment) ? `Lands on the ${environment.team_name || environment.name} hub` : `Stays in ${environment.name}, on this machine`;
}

// Who drives a hub plan or task: the person and their agent, or nothing when no one does.
export const driverLine = (row) => (row.driver ? `Driven by ${row.driver}, ${row.driver_agent}` : "");

export const BOARD_COLUMNS = [
    {key: "open", title: "Open", states: ["open"]},
    {key: "started", title: "In progress", states: ["started"]},
    {key: "waiting", title: "Waiting", states: ["paused", "blocked"]},
    {key: "done", title: "Completed", states: ["completed"]},
];

export const boardColumns = (tasks) => BOARD_COLUMNS.map((column) => ({...column, tasks: tasks.filter((task) => column.states.includes(task.state))}));

export const recentActivity = (messages, limit = 10) => [...messages].sort((a, b) => updatedAt(b) - updatedAt(a)).slice(0, limit);
