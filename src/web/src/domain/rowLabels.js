import {isHub} from "./hub.js";

// How a row is named in a card: Task 57, and acme task 57 when it is a row of a team's hub environment.
export function rowLabel(noun, row, environments) {
    const hub = environments.find((environment) => isHub(environment) && environment.id === row.environment_id);
    return hub ? `${hub.team_name || hub.name} ${noun} ${row.id}` : `${noun[0].toUpperCase()}${noun.slice(1)} ${row.id}`;
}
