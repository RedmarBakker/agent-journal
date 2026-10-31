import {createApp} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const scopeState = vi.hoisted(() => ({
    api: {planForecast: vi.fn(), organization: vi.fn()},
    rows: [],
}));

vi.mock("../src/composables/scope.js", () => ({
    useScope: () => ({env: "main", api: scopeState.api, rows: () => scopeState.rows, holding: vi.fn()}),
}));
vi.mock("../src/composables/workers.js", () => ({useWorkersHolding: () => ({rows: [], loaded: true})}));
vi.mock("../src/composables/wholePlans.js", () => ({wholePlans: vi.fn()}));
vi.mock("../src/domain/planAgents.js", () => ({planAgents: false}));
vi.mock("../src/kit/CloseButton.vue", () => ({default: {render: () => null}}));
vi.mock("../src/kit/Icon.vue", () => ({default: {render: () => null}}));
vi.mock("../src/kit/TextDisplay.vue", () => ({default: {render: () => null}}));
vi.mock("../src/kit/Folded.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/CommentToggle.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/ShareButton.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/PlanPageActions.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/PlanReviewRounds.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/SideToggle.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/PlanAgentSection.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/PlanRoleHistory.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/PlanTeamSection.vue", () => ({default: {render: () => null}}));
vi.mock("../src/resource/DeliveryForecastPanel.vue", () => ({default: {render: () => null}}));

const {default: PlanPage} = await import("../src/resource/PlanPage.vue");

let app = null;
let host = null;

beforeEach(() => {
    scopeState.api.planForecast.mockReset().mockResolvedValue({});
    scopeState.api.organization.mockReset().mockResolvedValue({domains: []});
    scopeState.rows = [
        {table: "tasks", id: 101, title: "Build the floor", state: "started", plan_id: 31},
        {table: "tasks", id: 102, title: "Write the release note", state: "open", plan_id: 31},
    ];
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("a plan task shows its Domain, route, ordered Role subtasks, workers and merged count", async () => {
    const task = {
        id: 101,
        title: "Build the floor",
        state: "started",
        route_state: "Waiting for the Domain's check",
        domain: {id: "alpha", title: "Alpha", icon: "🧭"},
        subtasks: [
            {id: 201, role: {id: "builder", title: "Builder"}, worker: {name: "Ada Lovelace"}, state: "completed", order: 1, after: null},
            {id: 202, role: {id: "scout", title: "Scout"}, worker: {name: "Grace Hopper"}, state: "started", order: 2, after: {id: 201, title: "Lay the first layer"}},
        ],
    };
    scopeState.api.organization.mockResolvedValue({domains: [{
        id: "alpha",
        title: "Alpha",
        icon: "🧭",
        plans: [{id: 31, task_details: [task]}],
    }]});
    host = document.body.appendChild(document.createElement("div"));
    app = createApp(PlanPage, {resource: {
        id: 31,
        title: "Build the floor",
        state: "started",
        mode: "organization",
        current_phase: 1,
        task_ids: [101, 102],
        phases: [{title: "Build", task_ids: [101, 102]}],
    }});
    app.mount(host);
    await vi.waitFor(() => expect(host.querySelector(".plan-subtask-summary")?.textContent).toContain("2 subtasks for 2 Roles, 1 merged"));

    const details = host.querySelector(".plan-task-details");
    expect(details.textContent).toContain("🧭 Domain: Alpha");
    expect(details.textContent).toContain("Waiting for the Domain's check");
    expect(details.textContent).toContain("2 subtasks for 2 Roles, 1 merged");
    expect(details.querySelector('[data-subtask-id="201"]').textContent).toContain("Role: Builder");
    expect(details.querySelector('[data-subtask-id="201"]').textContent).toContain("Worker: Ada Lovelace");
    expect(details.querySelector('[data-subtask-id="201"]').textContent).toContain("State: completed");
    expect(details.querySelector('[data-subtask-id="201"]').textContent).toContain("First subtask");
    expect(details.querySelector('[data-subtask-id="202"]').textContent).toContain("Role: Scout");
    expect(details.querySelector('[data-subtask-id="202"]').textContent).toContain("Worker: Grace Hopper");
    expect(details.querySelector('[data-subtask-id="202"]').textContent).toContain("After task 201: Lay the first layer");
    const unrouted = host.querySelector('[aria-label="Details for task 102"]');
    expect(unrouted.textContent).toContain("Domain: No Domain assigned");
    expect(unrouted.textContent).toContain("Route: With the Plan");
    expect(scopeState.api.organization).toHaveBeenCalledOnce();
});
