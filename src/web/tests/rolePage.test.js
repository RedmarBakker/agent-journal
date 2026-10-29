import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {roleInstanceTitle, roleInstances, roleWorkOf} from "../src/domain/roleInstances.js";
import RolePage from "../src/organization/RolePage.vue";
import {href, route} from "../src/route.js";
import {store} from "../src/state/store.js";
import {settle} from "./settle.js";

const {fixtures, apiMock} = vi.hoisted(() => ({
    fixtures: {snapshot: null},
    apiMock: {
        env: () => "main",
        list: vi.fn(async () => ({rows: [], is_last_page: true})),
        organizationRole: vi.fn(),
        in: vi.fn((env) => ({env: () => env, act: vi.fn()})),
    },
}));

vi.mock("../src/api/client.js", () => ({api: apiMock}));
vi.mock("../src/composables/poll.js", () => ({
    usePoll: (_key, options = {}) => {
        if (fixtures.snapshot && options.take) options.take(fixtures.snapshot);
        return vi.fn();
    },
}));
vi.mock("../src/composables/scope.js", () => ({
    scopeIn: () => ({holding: vi.fn(async () => {})}),
    scopeOfChat: (session, send, client) => ({env: client.env(), api: client, chat: {session, send}}),
}));
vi.mock("../src/sync/rows.js", () => ({holding: vi.fn(async () => {})}));
vi.mock("../src/composables/transcript.js", () => ({useTranscript: () => ({turns: [], error: "", loading: false, refresh: vi.fn()})}));
vi.mock("../src/agents/AgentInspector.vue", () => ({
    default: {
        props: ["info", "env", "agent", "chatScope", "run"],
        template: `<section class="mock-agent-inspector" :data-instance-name="info.name" :data-chat-mode="chatScope ? 'worker' : 'plan'" :data-env="env"><button>{{ chatScope ? 'Worker chat is writable' : 'Plan agent chat is writable' }}</button></section>`,
    },
}));
vi.mock("../src/agents/TranscriptInspector.vue", () => ({
    default: {
        props: ["name", "state", "moves", "facts", "parts", "env", "transcript", "speakers"],
        template: `<section class="mock-transcript-inspector" :data-env="env"><h2>{{ name }}</h2><p>Read-only seat transcript</p></section>`,
    },
}));

const role = {id: "architect", title: "Architect", domain: "product", cardinality: "many", models: {claude: "opus"}};
const agent = (id, environment, extra = {}) => ({id, environment, status: "working", session: `session-${id}`, ...extra});
const worker = (id, environment, extra = {}) => ({
    id,
    environment,
    role: role.id,
    plan_id: 4,
    profile: "",
    agent: id + 100,
    session: `worker-${id}`,
    state: "dispatched",
    name: `Worker ${id}`,
    queue: [],
    updated_at: "2026-10-29T12:00:00Z",
    ...extra,
});

let app;
let host;

async function settleRoute() {
    await new Promise((done) => setTimeout(done));
    await settle();
}

async function mount() {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(RolePage)});
    app.mount(host);
    await settleRoute();
}

beforeEach(async () => {
    apiMock.organizationRole.mockReset().mockResolvedValue(role);
    apiMock.in.mockClear();
    store.settings = {plans: {plan_agents: true}};
    location.hash = href.rolePage(role.domain, role.id);
    await settleRoute();
});

afterEach(() => {
    app?.unmount();
    host?.remove();
    app = null;
    host = null;
    fixtures.snapshot = null;
    document.body.innerHTML = "";
});

test("Role instances identify workers, old profile rows, solo RoleWork and organization seats from served rows", () => {
    const seat = worker(4, "plan-4", {name: "Release seat", agent: 8});
    const old = worker(5, "main", {role: "", profile: role.id, plan_id: 0, name: "Old Release Worker", agent: 9, closed_at: "2026-10-29T11:00:00Z"});
    const solo = agent(12, "plan-12", {
        created_at: "2026-10-29T12:00:00Z",
        stack: [
            {state: "leading_plan", data: {plan_id: 12}},
            {state: "following_plan", data: {plan_id: 12, task_id: 31}},
            {state: "role_work", data: {role: role.id, version: "v1"}},
        ],
    });
    const found = roleInstances(role, {
        workers: [seat, old],
        agents: [agent(8, "plan-4"), agent(9, "main"), solo],
        plans: [
            {id: 4, environment: "main", mode: "solo", title: "Same-number solo plan"},
            {id: 4, environment: "plan-4", mode: "organization", title: "Release"},
            {id: 12, environment: "plan-12", mode: "solo", title: "Research"},
        ],
    });

    expect(found).toHaveLength(3);
    expect(found.map((instance) => instance.kind)).toEqual(expect.arrayContaining(["solo", "seat", "worker"]));
    expect(found.find((instance) => instance.kind === "seat").plan.title).toBe("Release");
    expect(found.find((instance) => instance.legacy).name).toBe("Old Release Worker");
    expect(roleWorkOf(solo, role.id)).toEqual({plan_id: 12, task_id: 31});
    expect(roleInstanceTitle(found.find((instance) => instance.kind === "solo"))).toContain("Architect · Plan 12: Research · Task 31");
    expect(roleInstanceTitle(found.find((instance) => instance.kind === "solo"))).toContain("Started");
});

test("an organization-plan Role seat shows its read-only transcript and queue beside it", async () => {
    fixtures.snapshot = {
        key: "product/architect",
        workers: [worker(4, "plan-4", {name: "Release seat", queue: [{id: 51, title: "Run final review"}], task: {task_id: 50, title: "Review"}})],
        agents: [agent(8, "plan-4")],
        plans: [{id: 4, environment: "plan-4", mode: "organization", title: "Release"}],
    };
    await mount();

    expect(host.querySelector(".mock-transcript-inspector").textContent).toContain("Read-only seat transcript");
    expect(host.querySelector(".mock-agent-inspector")).toBeFalsy();
    expect(host.querySelector(".role-instance-queue").textContent).toContain("Task 51: Run final review");
    host.querySelector(".queued-task").click();
    await settleRoute();
    expect(route.value.open).toMatchObject({table: "tasks", id: 51, env: "plan-4"});
});

test("a worker Role gets writable chat and keeps a legacy worker under its old title in the instance picker", async () => {
    fixtures.snapshot = {
        key: "product/architect",
        workers: [
            worker(6, "main", {name: "Current architect", plan_id: 0, updated_at: "2026-10-29T12:00:00Z", agent: 106}),
            worker(7, "main", {role: "", profile: role.id, name: "Old planning title", plan_id: 0, updated_at: "2025-10-29T12:00:00Z", closed_at: "2025-10-29T13:00:00Z", agent: 107}),
        ],
        agents: [agent(106, "main"), agent(107, "main")],
        plans: [],
    };
    await mount();

    const inspector = host.querySelector(".mock-agent-inspector");
    expect(inspector.getAttribute("data-chat-mode")).toBe("worker");
    expect(inspector.textContent).toContain("Worker chat is writable");
    const options = [...host.querySelectorAll(".role-instance-picker option")].map((option) => option.textContent);
    expect(options).toContain("Older worker · Old planning title");

    const picker = host.querySelector(".role-instance-picker select");
    picker.value = "worker:main:7";
    picker.dispatchEvent(new Event("change"));
    await settleRoute();
    expect(host.querySelector(".mock-agent-inspector").getAttribute("data-instance-name")).toBe("Old planning title");
});

test("a solo-plan Role uses its Plan agent's writable chat", async () => {
    fixtures.snapshot = {
        key: "product/architect",
        workers: [],
        agents: [agent(12, "plan-12", {stack: [
            {state: "leading_plan", data: {plan_id: 12}},
            {state: "following_plan", data: {plan_id: 12, task_id: 31}},
            {state: "role_work", data: {role: role.id, version: "v1"}},
        ]})],
        plans: [{id: 12, environment: "plan-12", mode: "solo", title: "Research"}],
    };
    await mount();

    expect(host.querySelector(".mock-agent-inspector").getAttribute("data-env")).toBe("plan-12");
    expect(host.querySelector(".mock-agent-inspector").getAttribute("data-chat-mode")).toBe("plan");
    expect(host.textContent).toContain("Plan agent chat is writable");
});
