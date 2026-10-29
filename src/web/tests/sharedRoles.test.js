import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import SharedRoles from "../src/organization/SharedRoles.vue";
import {store} from "../src/state/store.js";

const {fixtures, apiMock} = vi.hoisted(() => ({
    fixtures: {snapshot: null, poller: "", params: null},
    apiMock: {
        organization: vi.fn(),
        organizationRole: vi.fn(),
    },
}));

vi.mock("../src/api/client.js", () => ({api: apiMock}));
vi.mock("../src/composables/poll.js", () => ({
    usePoll: (key, options = {}) => {
        fixtures.poller = key;
        fixtures.params = options.params;
        if (fixtures.snapshot && options.take) options.take(fixtures.snapshot);
        return vi.fn();
    },
}));
vi.mock("../src/kit/SidePanel.vue", () => ({
    default: {
        props: ["title", "abstract"],
        template: `<aside class="test-side-panel" :aria-label="title"><h2>{{ title }}</h2><slot /></aside>`,
    },
}));

const organization = {
    domains: [{
        id: "studio",
        title: "Studio",
        roles: [
            {id: "shared-editor", title: "Shared editor", cardinality: "journal"},
            {id: "plan-guide", title: "Plan guide", cardinality: "plan"},
            {id: "many-reviewer", title: "Many reviewer", cardinality: "many"},
            {id: "idle-shared", title: "Idle shared role", cardinality: "journal"},
        ],
    }],
};

const contract = {
    id: "shared-editor",
    title: "Shared editor",
    domain: "studio",
    cardinality: "journal",
    guidance: "",
    responsible: ["Review shared work"],
    not_responsible: [],
    inputs: [],
    outputs: [],
    skills: [],
    tools: [],
    approval_required: [],
    models: {},
    edges: [],
};

let app = null;
let host = null;

async function settle() {
    for (let i = 0; i < 5; i++) await nextTick();
    await new Promise((done) => setTimeout(done));
    await nextTick();
}

async function mount() {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(SharedRoles)});
    app.mount(host);
    await settle();
}

beforeEach(() => {
    store.settings = {plans: {plan_agents: true}};
    fixtures.snapshot = {
        workers: [{
            id: 8,
            role: "shared-editor",
            environment: "plan-2",
            state: "dispatched",
            task: {task_id: 45},
            queue: [{id: 46, title: "Queued handoff"}],
            worked: [{id: 44, title: "Earlier draft", state: "merged"}],
        }],
        tasks: [
            {id: 45, environment: "plan-2", title: "Current review", plan_id: 2, started_at: new Date(Date.now() - 120000).toISOString()},
            {id: 46, environment: "plan-2", title: "Queued handoff", plan_id: 7, updated_at: new Date(Date.now() - 180000).toISOString()},
            {id: 44, environment: "plan-2", title: "Earlier draft", outcome: "The shared draft shipped"},
        ],
        plans: [
            {id: 2, environment: "plan-2", title: "Current plan", driver: "Ada", driver_agent: "Plan agent on plan-2"},
            {id: 7, environment: "plan-2", title: "Next plan", driver: "Grace", driver_agent: "Plan agent on plan-2"},
        ],
    };
    fixtures.poller = "";
    fixtures.params = null;
    apiMock.organization.mockReset().mockResolvedValue(organization);
    apiMock.organizationRole.mockReset().mockResolvedValue(contract);
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("one row per journal Role shows its running or idle state, current job and queue details", async () => {
    await mount();

    const rows = [...host.querySelectorAll("tbody tr")];
    expect(fixtures.poller).toBe("organization.roles.shared");
    expect(fixtures.params()).toEqual({roles: ["shared-editor", "idle-shared"]});
    expect(rows).toHaveLength(2);
    expect(rows[0].textContent).toContain("Shared editor");
    expect(rows[0].textContent).toContain("Running");
    expect(rows[0].textContent).toContain("Task 45: Current review");
    expect(rows[0].textContent).toContain("Plan 2: Current plan");
    expect(rows[0].textContent).toContain("Started");
    expect(rows[0].textContent).toContain("Task 46: Queued handoff");
    expect(rows[0].textContent).toContain("Plan 7: Next plan");
    expect(rows[0].textContent).toContain("Driver: Grace · Plan agent on plan-2");
    expect(rows[0].textContent).toMatch(/Waited: .+ · since/);
    expect(rows[1].textContent).toContain("Idle shared role");
    expect(rows[1].textContent).toContain("Idle");
    expect(rows[1].textContent).toContain("No current job");
    expect(rows[1].textContent).toContain("No jobs queued");
});

test("opening a shared Role shows its contract and recent job outcomes", async () => {
    await mount();

    host.querySelector(".shared-role-open").click();
    await settle();

    expect(apiMock.organizationRole).toHaveBeenCalledWith("studio", "shared-editor");
    expect(host.querySelector(".test-side-panel h2").textContent).toBe("Shared editor");
    expect(host.querySelector(".test-side-panel").textContent).toContain("Recent jobs");
    expect(host.querySelector(".test-side-panel").textContent).toContain("Task 44: Earlier draft");
    expect(host.querySelector(".test-side-panel").textContent).toContain("Outcome: The shared draft shipped");
});
