import {colleagueOwner, isSession, isShared, sidebarEnvironments} from "./people.js";
import {updatedAt} from "./row.js";

// A team's hub is an environment of kind hub, named for the team; what the team's colleagues share and the Team chat are its sessions.
export const isHub = (row) => row.environment_type === "hub";

const isTeamListed = (row, people) => !isHub(row) && (isSession(row) || (isShared(row) && colleagueOwner(row.id, people) > 0));
// Plan and standalone-task agents use generated environment names; descendants keep that prefix and open through their plan or Role page.
const isTopLevelEnvironment = (row) => row.environment_type !== "local" || !/^(?:plan|task)-\d+(?:$|[-/:._])/.test(row.name);

// Each team's hub with its sessions, a session joining the hub of its own team key and, with none, the first hub.
export function teamGroups(rows, people) {
    const hubs = rows.filter(isHub);
    const sessions = sidebarEnvironments(rows, people).filter((row) => isTopLevelEnvironment(row) && isTeamListed(row, people));
    return hubs.map((hub, n) => ({
        key: hub.team_key || String(hub.id),
        team: hub.team_name || hub.name,
        hub,
        sessions: sessions.filter((row) => (row.team_key ? row.team_key === hub.team_key : n === 0)),
    }));
}

// The environments the sidebar lists apart from every team: the person's own.
// On a hosted journal only what is shared is listed: an environment that is not shared, not the hub and not a session never is.
export const ownEnvironments = (rows, people) =>
    sidebarEnvironments(rows, people).filter((row) => isTopLevelEnvironment(row) && !isHub(row) && !isTeamListed(row, people) && (!people.hosted || isShared(row)));

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
