import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

let heldCounts = [];
const api = {
    env: () => "main",
    list: vi.fn(),
    entries: vi.fn(),
    organization: vi.fn(),
};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: vi.fn()}));
vi.mock("../src/platform/view.js", () => ({narrow: {value: false}}));
vi.mock("../src/layout/EnvStart.vue", () => ({default: {template: "<span />"}}));
vi.mock("../src/layout/NewEnvironment.vue", () => ({default: {template: "<span />"}}));

const {default: Sidebar} = await import("../src/layout/Sidebar.vue");
const {store} = await import("../src/state/store.js");
const {takeEntries, hasLoaded} = await import("../src/sync/rows.js");

const environments = [
    {id: 1, name: "main", environment_type: "local", team_key: ""},
    {id: 2, name: "release", environment_type: "local", team_key: ""},
    {id: 3, name: "plan-7", environment_type: "local", team_key: ""},
    {id: 4, name: "plan-7/domain-sales", environment_type: "local", team_key: ""},
    {id: 5, name: "plan-7/role-builder", environment_type: "local", team_key: ""},
    {id: 6, name: "task-11", environment_type: "local", team_key: ""},
    {id: 10, name: "acme", team_name: "Acme", environment_type: "hub", team_key: "team-a"},
    {id: 11, name: "plan-12", environment_type: "local", team_key: "team-a"},
    {id: 12, name: "plan-12/domain-sales", environment_type: "local", team_key: "team-a"},
    {id: 13, name: "plan-12/role-builder", environment_type: "local", team_key: "team-a"},
];
const organization = {
    domains: [{
        id: "sales",
        title: "Sales",
        icon: "📊",
        plans_active: 1,
        roles: [
            {id: "many", title: "Many jobs", cardinality: "many", instances: 2, queued: 8},
            {id: "queue", title: "Queue", cardinality: "plan", instances: 1, queued: 3},
        ],
    }],
};
const countRow = (plans, manyInstances, manyQueued, queueInstances, queueQueued) => ({
    id: 9,
    name: "sales",
    plans_active: plans,
    roles: {
        many: {instances: manyInstances, queued: manyQueued},
        queue: {instances: queueInstances, queued: queueQueued},
    },
});

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

let app = null;
let host = null;
afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

beforeEach(() => {
    location.hash = "#/organization";
    store.booted = true;
    store.settings = {plans: {plan_agents: true}, workers: {organization_folder: "/workspace/agentic-organization"}};
    store.spec = {version: "test"};
    store.people = {me: 1, hosted: false, people: [{id: 2, name: "Ada"}], owners: {11: 2, 12: 2, 13: 2}};
    store.sideMini = false;
    store.pluginPage = null;
    store.rows.environments = environments;
    store.rows.domain_counts = [];
    store.rows.plans = [];
    store.rows.plugins = [];
    store.entries = [];
    heldCounts = [countRow(1, 2, 8, 1, 3)];
    api.list.mockReset().mockImplementation(async (table) => {
        const rows = table === "environments" ? environments : table === "domain_counts" ? heldCounts : [];
        return {rows, counts: {all: rows.length, open: rows.length, unread: 0}, is_last_page: true};
    });
    api.entries.mockReset().mockResolvedValue([]);
    api.organization.mockReset().mockResolvedValue(organization);
});

test("the Organization sidebar links domains and Roles, follows live counts, and hides plan environments and their descendants", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(Sidebar)});
    app.directive("tip", {});
    app.mount(host);

    await until(() => host.querySelector('a[href="#/organization?domain=sales"]') && hasLoaded("domain_counts"));
    expect(api.organization).toHaveBeenCalledOnce();

    const headers = [...host.querySelectorAll(".fold-head")].map((button) => button.textContent.trim());
    expect(headers.indexOf("Project")).toBeLessThan(headers.indexOf("Organization"));
    expect(headers.indexOf("Organization")).toBeLessThan(headers.indexOf("Environments"));

    const domain = host.querySelector('a[href="#/organization?domain=sales"]');
    expect(domain.querySelector(".organization-domain-icon").textContent).toBe("📊");
    expect(domain.querySelector(".count").textContent).toBe("1");
    expect(domain.querySelector(".count").title).toBe("1 active plans");
    expect(host.querySelector(".organization-role")).toBeNull();

    host.querySelector('button[aria-label="Show Roles in Sales"]').click();
    await until(() => host.querySelectorAll(".organization-role").length === 2);
    const roles = [...host.querySelectorAll(".organization-role")];
    const many = roles.find((link) => link.textContent.includes("Many jobs"));
    const queue = roles.find((link) => link.textContent.includes("Queue"));
    expect(many.getAttribute("href")).toBe("#/organization?domain=sales&role=many");
    expect(queue.getAttribute("href")).toBe("#/organization?domain=sales&role=queue");
    expect(many.querySelector(".count").textContent).toBe("2");
    expect(many.querySelector(".count").title).toBe("2 running instances");
    expect(queue.querySelector(".count").textContent).toBe("4");
    expect(queue.querySelector(".count").title).toBe("4 queued jobs including the current job");

    heldCounts = [countRow(3, 4, 0, 2, 3)];
    await takeEntries([{entry_type: "updated", data: {table: "domain_counts", id: 9, joins: []}}]);
    await until(() => domain.querySelector(".count").textContent === "3" && many.querySelector(".count").textContent === "4" && queue.querySelector(".count").textContent === "5");
    expect(domain.querySelector(".count").textContent).toBe("3");
    expect(many.querySelector(".count").textContent).toBe("4");
    expect(queue.querySelector(".count").textContent).toBe("5");

    const environmentGroup = [...host.querySelectorAll(".fold-group")].find((group) => group.querySelector(".fold-head")?.textContent.trim() === "Environments");
    const visibleEnvironments = [...environmentGroup.querySelectorAll(".env-row .label")].map((label) => label.textContent.trim());
    expect(visibleEnvironments).toEqual(["main", "release"]);
    expect(host.textContent).not.toContain("plan-7");
    expect(host.textContent).not.toContain("plan-12");
    expect(host.textContent).not.toContain("task-11");
});
