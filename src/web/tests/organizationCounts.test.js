import {beforeEach, expect, test, vi} from "vitest";

let held = [];
vi.mock("../src/api/client.js", () => ({
    api: {env: () => "main", list: async () => ({rows: held, counts: {all: held.length, open: held.length, unread: 0}, is_last_page: true}), entries: async () => [], settings: async () => ({})},
    onWrite: () => {},
}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: () => {}}));
vi.mock("../src/route.js", () => ({route: {value: {env: "main", page: "", open: null}}}));

const {store} = await import("../src/state/store.js");
const {takeEntries, hasLoaded} = await import("../src/sync/rows.js");
const {domainCounts, runningIn} = await import("../src/domain/organizationCounts.js");

const row = (instances, plans, at) => ({table: "domain_counts", id: 1, name: "alpha", plans_active: plans, roles: {builder: {instances, queued: 0}}, updated_at: at});
const arrived = () => takeEntries([{entry_type: "updated", data: {table: "domain_counts", id: 1, joins: []}}]);
const until = async (done) => {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 20));
};

beforeEach(() => {
    store.booted = true;
});

test("a domain_counts row arriving through the sync changes the figures the sidebar reads, without a reload", async () => {
    held = [row(1, 1, "2026-10-29T10:00:00")];
    expect(domainCounts()).toEqual({});
    await until(() => hasLoaded("domain_counts"));
    expect(domainCounts()).toEqual({alpha: {plansActive: 1, roles: {builder: {instances: 1, queued: 0}}}});
    expect(runningIn(domainCounts(), "alpha")).toBe(1);
    held = [row(3, 2, "2026-10-29T10:05:00")];
    await arrived();
    await until(() => runningIn(domainCounts(), "alpha") === 3);
    expect(domainCounts().alpha.plansActive).toBe(2);
    expect(runningIn(domainCounts(), "alpha")).toBe(3);
});
