import {createApp} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const scopeState = vi.hoisted(() => ({
    api: {planForecast: vi.fn(), sprints: vi.fn(), carryPlan: vi.fn()},
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
    scopeState.api.planForecast.mockReset().mockResolvedValue({
        sprint: {id: 21, state: "closed", starts_on: "2026-10-12", ends_on: "2026-10-26", starts_at: "2026-10-12T00:00:00Z", ends_at: "2026-10-26T00:00:00Z"},
        status: "not enough history",
    });
    scopeState.api.sprints.mockReset();
    scopeState.api.carryPlan.mockReset();
    scopeState.rows.length = 0;
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("the plan page shows the sprint move action for a plan with a closed sprint", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp(PlanPage, {resource: {
        id: 31,
        title: "Prospect list for the fleet tracker campaign",
        state: "started",
        mode: "solo",
        current_phase: 1,
        task_ids: [],
        phases: [],
    }});
    app.mount(host);
    await vi.waitFor(() => expect(host.querySelector(".plan-sprint-membership button")?.textContent).toBe("Move to another sprint"));

    expect(scopeState.api.planForecast).toHaveBeenCalledWith(31);
    expect(host.textContent).toContain("Sprint 21 · 12 Oct to 25 Oct");
    expect(host.querySelector(".plan-sprint-membership").textContent).toContain("Move to another sprint");
});
