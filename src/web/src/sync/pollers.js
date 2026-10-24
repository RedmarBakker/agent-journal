import {agent} from "../composables/leadAgent.js";
import {store} from "../state/store.js";
import {followServer, updating} from "../state/updating.js";
import {isActive} from "../domain/journals.js";
import {api} from "../api/client.js";
import {sharedData} from "../api/shared.js";
import {PAGE, takeEntries} from "./rows.js";
import {barOn} from "../composables/settings.js";
import {loadPhones} from "../composables/phones.js";
import {checkTunnel} from "../composables/shares.js";
import {pageOf} from "./paging.js";

const LIVE = 5;
const BUSY_EVERY = 500;
const CALM_EVERY = 3000;
const ASK_EVERY = 1500;
const newest = () => (store.entries.length ? store.entries[store.entries.length - 1].id : 0);
const polledTo = {env: "", id: 0};
const busy = () => Boolean(store.bar && store.bar.length) || isActive(agent.value && agent.value.status);

function pollEntries() {
    if (polledTo.env !== api.env()) Object.assign(polledTo, {env: api.env(), id: newest()});
    return api.entries(polledTo.id);
}

function takePolled(fresh) {
    if (!fresh.length) return;
    polledTo.id = fresh[fresh.length - 1].id;
    takeEntries(fresh);
}

async function heldElsewhere({scope, table, id}) {
    await scope.holding(table, [id]);
    await scope.recent("comments", PAGE);
}

// Every poller the viewer runs, declared once here and nowhere else, and never at runtime: its key, what it reads from the
// params its users hand it, and how often in milliseconds (or a function of the moment). One that runs per agent or per row
// names in `by` the part of its params that tells one run from another. One the whole app holds keeps its answer in the
// store with `take`. An on-demand poller (`demand`) has no interval: it reads once when asked, pausing the poller it names
// in `pauses` for the length of its own read, so the two never pull at the same time.
export const POLLERS = Object.freeze({
    "status.bar": {
        read: () => api.bar(),
        every: () => (busy() ? BUSY_EVERY : CALM_EVERY),
        take: (got) => Array.isArray(got) && (store.bar = got),
        active: () => barOn.value,
    },
    "agents.index": {read: () => api.list("agents", {limit: LIVE}), every: 1000, take: (got) => (store.agents = got.rows)},
    "agents.live": {read: () => api.liveAgents(), every: 5000, take: (got) => (store.live = got)},
    "status.summary": {
        read: () => api.summary(),
        every: () => (updating.countdown || updating.external || updating.version ? 1000 : 4000),
        take: (got) => {
            store.summary = got;
            followServer(got);
        },
    },
    "journal.manifest": {read: () => api.manifest(), every: 30000, take: (got) => (store.spec = got)},
    "journals.index": {read: () => api.journals(), every: 10000, take: (got) => (store.journals = got)},
    "people.index": {read: () => api.people(), every: 30000, take: (got) => got && got.people && (store.people = got)},
    "entries.recent": {read: pollEntries, every: 1000, take: takePolled},
    "phones.index": {read: () => loadPhones(), every: 30000},
    "phones.pairing": {read: () => loadPhones(), every: ASK_EVERY},
    "phone.tunnel": {read: () => api.tunnelAnswering(), every: ASK_EVERY},
    "phone.tunnel.problems": {read: () => checkTunnel(), every: ASK_EVERY * 2},
    "shares.services": {read: () => api.services(), every: 5000},
    "sync.line": {read: () => api.syncLine(), every: 5000},
    "team.chat": {read: () => api.teamChat(), every: 10000},
    "side.thread": {read: () => api.sideThread(), every: 3000},
    "mcp.servers": {read: () => api.mcp(), every: 30000},
    "share.page": {read: () => sharedData(), every: 20000},
    "outbox.retry": {read: ({retry}) => retry(), every: 5000},
    "tour.start": {read: ({clear}) => clear(), every: 800},
    "workers.index": {read: () => api.list("workers", {limit: pageOf("workers")}).then((got) => got.rows || []), every: 5000},
    "workers.every": {read: () => api.list("workers", {limit: 200}).then((got) => got.rows || []), every: 5000},
    "workers.holding": {read: ({ids}) => api.list("workers", {ids}).then((got) => got.rows || []), every: 5000, by: ({ids}) => ids.join(",")},
    "plugin.dashboard": {read: ({plugin}) => api.pluginDashboard(plugin), every: 10000, by: ({plugin, board}) => `${plugin}:${board}`},
    "plan.timeline": {read: ({scope, plan}) => scope.api.planTimeline(plan), every: 15000, by: ({scope, plan}) => `${scope.env}:${plan}`},
    "reader.elsewhere": {read: heldElsewhere, every: 5000, by: ({scope, table, id}) => `${scope.env}:${table}:${id}`},
    "inspector.agents": {read: ({client}) => client.list("agents", {limit: 20}), every: 5000, by: ({client}) => client.env()},
    "inspector.rows": {read: ({scope, tables}) => scope.recentAll(tables, 50), every: 5000, by: ({scope}) => scope.env},
    "agent.terminal": {read: ({client, agent, after}) => client.terminal(agent, after), every: 2000, by: ({client, agent}) => `${client.env()}:${agent}`},
    "agent.transcript": {
        read: ({client, agent, session, since}) => client.transcript(agent, session, {since, last: PAGE}),
        every: 3000,
        by: ({client, agent, session}) => `${client.env()}:${agent}:${session || ""}`,
    },
    "agent.transcript.older": {read: ({client, agent, session, before}) => client.transcript(agent, session, {before, last: PAGE}), demand: true, pauses: "agent.transcript"},
    "agent.edits": {read: ({client, agent, cursor}) => client.edits(agent, cursor), every: 2000, by: ({client, agent}) => `${client.env()}:${agent}`},
});
