// People named relative to the viewer: the viewer's own person is you, a colleague is called by name, and an agent by the
// person who owns its environment. `people` is what /journal/people answers: me, device, people and owners.

export const NOBODY = {me: 1, device: "", people: [], owners: {}};

export const personName = (number, people) => (people.people.find((person) => person.id === number) || {}).name || `user ${number}`;

export const isMe = (stamp, people = NOBODY) => stamp === `user:${people.me}`;

// The colours a colleague's messages are drawn in, one per person by their account number, so the same on every machine; never the
// blue of the viewer's own messages nor the agent's plain bubble
export const COLLEAGUE_COLOURS = ["#3fb37f", "#e0803a", "#a77bf3", "#e2669a", "#2bb5b0", "#d4b13f"];

export function colleagueColour(stamp, people = NOBODY) {
    const [kind, id] = (stamp || "").split(":");
    return kind === "user" && Number(id) !== people.me ? COLLEAGUE_COLOURS[Number(id) % COLLEAGUE_COLOURS.length] : "";
}

export function agentName(environmentId, people = NOBODY) {
    const owner = people.owners[String(environmentId)] || 0;
    return !owner || owner === people.me ? "the agent" : `${personName(owner, people)}'s agent`;
}

export function actorName(stamp, people = NOBODY, environmentId = 0) {
    const [kind, id] = (stamp || "system").split(":");
    if (kind === "user") return Number(id) === people.me ? "you" : personName(Number(id), people);
    if (kind === "agent") return agentName(environmentId, people);
    if (kind === "worker") return `worker ${id}`;
    if (kind === "phone") return "you, from your phone";
    return kind === "system" ? "the journal" : id || kind;
}

// The owner of an environment when that is not the viewer, else 0.
export function colleagueOwner(environmentId, people = NOBODY) {
    const owner = people.owners[String(environmentId)] || 0;
    return owner && owner !== people.me ? owner : 0;
}

// The environments the sidebar lists: the viewer's own and the Team chat, never a colleague's, which open from the Team page.
export const ownEnvironments = (rows, people = NOBODY) => rows.filter((row) => !colleagueOwner(row.id, people));
