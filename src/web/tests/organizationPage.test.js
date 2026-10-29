import {createApp, h, nextTick} from "vue";
import {beforeEach, expect, test, vi} from "vitest";

let heldCounts = [];
const api = {
    env: () => "main",
    list: vi.fn(),
    entries: vi.fn(),
    settings: vi.fn(),
    organization: vi.fn(),
    organizationRole: vi.fn(),
    reloadOrganization: vi.fn(),
};
vi.mock("../src/api/client.js", () => ({api, onWrite: vi.fn()}));
vi.mock("../src/chat/outbox.js", () => ({onOutboxChange: vi.fn()}));

const {default: OrganizationPage} = await import("../src/pages/OrganizationPage.vue");
const {store} = await import("../src/state/store.js");
const {organizationBoard} = await import("../src/state/organizationBoard.js");
const {route} = await import("../src/route.js");
const {takeEntries} = await import("../src/sync/rows.js");

const folder = "/workspace/agentic-organization";
const commit = "abcdef0123456789abcdef0123456789abcdef01";
const organization = (sha = commit) => ({
    folder,
    commit: sha,
    version: "contract-digest",
    problems: [{path: "domains/sales/roles/ghost/role.toml", rule: "role", message: "Add a role.toml file or remove this folder."}],
    domains: [{
        id: "sales",
        title: "Sales",
        icon: "📊",
        description: "Help customers choose the right service.",
        board: {planned: "Ready", in_progress: "Working", in_review: "Review", done: "Complete"},
        edges: [{kind: "escalates_to", to: "support", about: "A blocker outside sales"}],
        plans: [{id: 42, title: "Recommend a service", phase: "in_progress", phase_name: "Working", mode: "organization", tasks: [1, 2], done: 1, waits_on: "Role work"}],
        models: {claude: "opus", codex: "gpt-6.1-sol", effort: "xhigh"},
        roles: [{
            id: "account-manager",
            title: "Account manager",
            cardinality: "plan",
            writes: false,
            edges: [{kind: "delegates_to", to: "sales-lead", about: "A decision needs approval"}],
            models: {claude: "sonnet", codex: "gpt-6.1-sol", effort: "xhigh"},
            instances: 1,
            queued: 0,
        }, {
            id: "sales-lead",
            title: "Sales lead",
            cardinality: "journal",
            writes: false,
            models: {claude: "sonnet", codex: "gpt-6.1-sol", effort: "xhigh"},
            instances: 0,
            queued: 0,
        }],
    }],
});

const detail = {
    id: "account-manager",
    title: "Account manager",
    domain: "sales",
    description: "Help customers choose the right service.",
    cardinality: "plan",
    writes: false,
    responsible: ["Customer needs"],
    not_responsible: ["Product delivery"],
    inputs: ["A customer request"],
    outputs: ["A service recommendation"],
    edges: [{kind: "escalates_to", to: "sales-lead", about: "A decision outside this role"}],
    skills: ["governance"],
    tools: ["read_files"],
    approval_required: ["production_deployment"],
    models: {claude: "sonnet", codex: "gpt-6.1-sol", effort: "xhigh"},
    guidance: "## How to work\n\nListen first, then explain the recommendation.",
};
const countRow = (instances) => ({id: 1, name: "sales", roles: {"account-manager": {instances, queued: 0}}, plans_active: 1});

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

beforeEach(() => {
    location.hash = "#/organization";
    store.booted = false;
    store.settings = {plans: {plan_agents: true}, workers: {organization_folder: folder}};
    store.rows.domain_counts = [countRow(3)];
    store.entries = [];
    organizationBoard.words = "";
    organizationBoard.hideDone = false;
    heldCounts = [countRow(3)];
    api.list.mockReset().mockImplementation(async () => ({rows: heldCounts, counts: {all: heldCounts.length, open: heldCounts.length, unread: 0}, is_last_page: true}));
    api.entries.mockReset().mockResolvedValue([]);
    api.settings.mockReset().mockResolvedValue(store.settings);
    api.organization.mockReset().mockResolvedValue(organization());
    api.organizationRole.mockReset().mockResolvedValue(detail);
    api.reloadOrganization.mockReset().mockResolvedValue(organization("fedcba9876543210fedcba9876543210fedcba98"));
});

test("the Organization page reads its real folder, shows contract problems, and opens the whole Role contract", async () => {
    const host = document.createElement("div");
    document.body.appendChild(host);
    const app = createApp({render: () => h(OrganizationPage)});
    app.mount(host);
    await until(() => host.textContent.includes("Account manager"));

    expect(api.organization).toHaveBeenCalledOnce();
    expect(host.textContent).toContain(folder);
    expect(host.textContent).toContain(commit);
    expect(host.querySelector(".contract-problems").nextElementSibling.classList.contains("communication-edges")).toBe(true);
    const edgeRows = [...host.querySelectorAll("[data-communication-edge]")];
    expect(edgeRows).toHaveLength(2);
    expect(edgeRows[0].textContent).toContain("Domain Sales");
    expect(edgeRows[0].textContent).toContain("escalates_to");
    expect(edgeRows[0].textContent).toContain("domain:support");
    expect(edgeRows[0].textContent).toContain("A blocker outside sales");
    expect(edgeRows[1].textContent).toContain("Role Sales / Account manager");
    expect(edgeRows[1].textContent).toContain("delegates_to");
    expect(edgeRows[1].textContent).toContain("role:sales/sales-lead");
    expect(host.textContent).toContain("Cardinality: One per plan");
    expect(host.textContent).toContain("Writes files: No");
    expect(host.textContent).toContain("Model: Claude: sonnet · Codex: gpt-6.1-sol · Effort: xhigh");
    expect(host.textContent).toContain("Running: 3");

    heldCounts = [countRow(4)];
    store.booted = true;
    takeEntries([{id: 9, entry_type: "updated", data: {table: "domain_counts", id: 1, joins: []}}]);
    await until(() => host.textContent.includes("Running: 4"));
    expect(host.textContent).toContain("Running: 4");

    host.querySelector('[aria-label="Open Account manager"]').click();
    await until(() => document.body.textContent.includes("Listen first, then explain the recommendation."));
    expect(api.organizationRole).toHaveBeenCalledWith("sales", "account-manager");
    expect(document.body.textContent).toContain("Responsible for");
    expect(document.body.textContent).toContain("Customer needs");
    expect(document.body.textContent).toContain("Not responsible for");
    expect(document.body.textContent).toContain("A customer request");
    expect(document.body.textContent).toContain("A service recommendation");
    expect(document.body.textContent).toContain("governance");
    expect(document.body.textContent).toContain("read_files");
    expect(document.body.textContent).toContain("production_deployment");
    expect(document.body.textContent).toContain("escalates_to");
    expect(document.body.textContent).toContain("sales-lead");
    expect(document.body.textContent).toContain("AGENTS.md");

    [...host.querySelectorAll("button")].find((button) => button.textContent.includes("Read the folder again")).click();
    await until(() => host.textContent.includes("fedcba9876543210fedcba9876543210fedcba98"));
    expect(api.reloadOrganization).toHaveBeenCalledOnce();

    app.unmount();
    host.remove();
});

test("a domain route opens its own four phase plan board", async () => {
    location.hash = "#/organization?domain=sales";
    await until(() => route.value.domain === "sales");

    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(OrganizationPage)});
    app.mount(host);
    await until(() => host.querySelector('[data-domain="sales"] .organization-plan-card'));

    const board = host.querySelector('[data-domain="sales"]');
    expect(host.querySelector(".organization-domain-page")).not.toBeNull();
    expect(board.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    expect(board.querySelector('[data-phase="in_progress"] h3').textContent).toContain("Working");
    expect(board.querySelector('[data-plan-id="42"]').textContent).toContain("1 of 2 done");
    expect(board.querySelector('[data-plan-id="42"]').textContent).toContain("Waits on: Role work");
    expect(host.querySelector('button.organization-all-domains').textContent).toContain("All domains");
});
