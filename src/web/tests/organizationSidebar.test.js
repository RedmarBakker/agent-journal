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
    {id: 1, key: "main-key", name: "main", environment_type: "local", team_key: ""},
    {id: 2, key: "release-key", name: "release", environment_type: "local", team_key: ""},
    {id: 3, key: "ordinary-plan-7", name: "plan-7", environment_type: "local", team_key: ""},
    {id: 4, key: "plan-agent-key", name: "plan-1", environment_type: "local", team_key: "", generated_for: "plan", parent_key: "main-key"},
    {id: 5, key: "domain-agent-key", name: "sales-agent", environment_type: "local", team_key: "", generated_for: "", parent_key: "plan-agent-key"},
    {id: 6, key: "role-seat-key", name: "builder-seat", environment_type: "local", team_key: "", generated_for: "", parent_key: "plan-agent-key"},
    {id: 7, key: "task-agent-key", name: "task-11", environment_type: "local", team_key: "", generated_for: "task", parent_key: "main-key"},
    {id: 10, key: "team-a-key", name: "acme", team_name: "Acme", environment_type: "hub", team_key: "team-a"},
    {id: 11, key: "team-plan-key", name: "plan-12", environment_type: "local", team_key: "team-a", generated_for: "plan", parent_key: "team-a-key"},
    {id: 12, key: "team-domain-key", name: "sales-agent", environment_type: "local", team_key: "team-a", generated_for: "", parent_key: "team-plan-key"},
    {id: 13, key: "team-role-key", name: "builder-seat", environment_type: "local", team_key: "team-a", generated_for: "", parent_key: "team-plan-key"},
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
    }, ...Array.from({length: 12}, (_, index) => ({
        id: `domain-${index + 1}`,
        title: `Domain ${index + 1}`,
        icon: "🧭",
        plans_active: 0,
        roles: Array.from({length: 4}, (__, roleIndex) => ({
            id: `role-${index + 1}-${roleIndex + 1}`,
            title: `Role ${index + 1}-${roleIndex + 1}`,
            cardinality: "plan",
            instances: 0,
            queued: 0,
        })),
    }))],
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

    const homeLinks = [...host.querySelector(".side .group").querySelectorAll("a.item")];
    expect(homeLinks.slice(0, 3).map((link) => link.textContent.trim())).toEqual(["Home", "Board", "Chat"]);

    await until(() => host.querySelector('a[href="#/organization?domain=sales"]') && hasLoaded("domain_counts"));
    expect(api.organization).toHaveBeenCalledOnce();
    expect(organization.domains).toHaveLength(13);
    expect(organization.domains.reduce((total, domain) => total + domain.roles.length, 0)).toBe(50);
    expect(host.querySelectorAll(".organization-domain-link")).toHaveLength(13);
    const sharedRoles = host.querySelector('a[href="#/organization?roles=shared"]');
    expect(sharedRoles.textContent).toContain("Shared Roles");
    location.hash = sharedRoles.getAttribute("href");
    await until(() => sharedRoles.classList.contains("on"));
    expect(sharedRoles.classList.contains("on")).toBe(true);
    location.hash = "#/organization";
    await until(() => !sharedRoles.classList.contains("on"));

    const headers = [...host.querySelectorAll(".fold-head")].map((button) => button.textContent.trim());
    expect(headers.indexOf("Project")).toBeLessThan(headers.indexOf("Organization"));
    expect(headers.indexOf("Organization")).toBeLessThan(headers.indexOf("Environments"));

    const domain = host.querySelector('a[href="#/organization?domain=sales"]');
    expect(domain.querySelector(".organization-domain-icon").textContent).toBe("📊");
    expect(domain.querySelector(".count").textContent).toBe("1");
    expect([...host.querySelectorAll(".env-row > a.item:not(.hub-item)")].every((link) => link.getAttribute("href") === "#/chat")).toBe(true);
    expect(domain.querySelector(".count").title).toBe("1 active plans");
    expect(host.querySelector(".organization-role")).toBeNull();

    host.querySelector('button[aria-label="Show Roles in Sales"]').click();
    await until(() => host.querySelectorAll(".organization-role").length === 2);
    const roles = [...host.querySelectorAll(".organization-role")];
    const many = roles.find((link) => link.textContent.includes("Many jobs"));
    const queue = roles.find((link) => link.textContent.includes("Queue"));
    expect(many.getAttribute("href")).toBe("#/role?domain=sales&role=many");
    expect(queue.getAttribute("href")).toBe("#/role?domain=sales&role=queue");
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
    expect(visibleEnvironments).toEqual(["main", "release", "plan-7"]);
    expect(host.textContent).toContain("plan-7");
    expect(host.textContent).not.toContain("plan-12");
    expect(host.textContent).not.toContain("sales-agent");
    expect(host.textContent).not.toContain("builder-seat");
    expect(host.textContent).not.toContain("task-11");

    const domainToggles = [...host.querySelectorAll(".organization-domain-toggle")];
    domainToggles.filter((button) => button.getAttribute("aria-expanded") === "false").forEach((button) => button.click());
    await nextTick();
    expect(host.querySelectorAll(".organization-role")).toHaveLength(50);
    const organizationHeader = [...host.querySelectorAll(".fold-head")].find((button) => button.textContent.trim() === "Organization");
    expect(organizationHeader.tagName).toBe("BUTTON");
    expect(organizationHeader.tabIndex).toBe(0);
    organizationHeader.focus();
    organizationHeader.click();
    await nextTick();
    expect(organizationHeader.getAttribute("aria-expanded")).toBe("false");
    expect(host.querySelectorAll(".organization-domain-link")).toHaveLength(0);
    expect(host.querySelectorAll(".organization-role")).toHaveLength(0);

    store.settings = {...store.settings, plans: {plan_agents: false}};
    await nextTick();
    const oldModeGroup = [...host.querySelectorAll(".fold-group")].find((group) => group.querySelector(".fold-head")?.textContent.trim() === "Environments");
    const oldModeEnvironments = [...oldModeGroup.querySelectorAll(".env-row .label")].map((label) => label.textContent.trim());
    expect(oldModeEnvironments).toContain("plan-7");
});
