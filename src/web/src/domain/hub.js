import {colleagueOwner, sidebarEnvironments} from "./people.js";
import {updatedAt} from "./row.js";

// A team's hub is an environment of kind hub, named for the team; what the team's colleagues share and the Team chat are its sessions.
export const isHub = (row) => row.kind === "hub";

const isSession = (row, people) => !isHub(row) && (row.is_team_chat || (row.is_shared_with_team && colleagueOwner(row.id, people) > 0));

// Each team's hub with its sessions, a session joining the hub of its own team key and, with none, the first hub.
export function teamGroups(rows, people) {
    const hubs = rows.filter(isHub);
    const sessions = sidebarEnvironments(rows, people).filter((row) => isSession(row, people));
    return hubs.map((hub, n) => ({
        key: hub.team_key || String(hub.id),
        team: hub.team_name || hub.name,
        hub,
        sessions: sessions.filter((row) => (row.team_key ? row.team_key === hub.team_key : n === 0)),
    }));
}

// The environments the sidebar lists apart from every team: the person's own.
export const ownEnvironments = (rows, people) => sidebarEnvironments(rows, people).filter((row) => !isHub(row) && !isSession(row, people));

export const inHub = (rows, hub) => rows.filter((row) => row.environment_id === hub.id);

export const BOARD_COLUMNS = [
    {key: "open", title: "Open", states: ["open"]},
    {key: "started", title: "In progress", states: ["started", "delegated"]},
    {key: "waiting", title: "Waiting", states: ["paused", "blocked"]},
    {key: "done", title: "Done", states: ["done"]},
];

export const boardColumns = (tasks) => BOARD_COLUMNS.map((column) => ({...column, tasks: tasks.filter((task) => column.states.includes(task.state))}));

export const recentActivity = (messages, limit = 10) => [...messages].sort((a, b) => updatedAt(b) - updatedAt(a)).slice(0, limit);
