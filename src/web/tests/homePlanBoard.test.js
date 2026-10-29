import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {pageOf} from "../src/sync/paging.js";

vi.mock("../src/pages/Home.vue", () => ({default: {template: "<section data-existing-home />"}}));

const {default: AppPages} = await import("../src/AppPages.vue");
const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {organizationBoard} = await import("../src/state/organizationBoard.js");

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    vi.restoreAllMocks();
    document.body.innerHTML = "";
});

beforeEach(() => {
    store.people = {hosted: false};
    store.settings = {plans: {plan_agents: false}};
    organizationBoard.words = "";
    organizationBoard.hideDone = false;
    vi.spyOn(api, "organization").mockResolvedValue({plans: [], scheduled_plans: [], domains: []});
});

function mount() {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(AppPages, {page: "home"})});
    app.mount(host);
}

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((resolve) => setTimeout(resolve, 10));
    await nextTick();
}

test("with Plan agents off, Home keeps rendering its existing page", async () => {
    mount();
    await nextTick();

    expect(host.querySelector("[data-existing-home]")).not.toBeNull();
    expect(host.querySelector("[data-home-plan-board]")).toBeNull();
    expect(api.organization).not.toHaveBeenCalled();
});

test("with Plan agents on, Home shows one paged board of every plan and scheduled next starts", async () => {
    const plans = Array.from({length: pageOf("plans") + 1}, (_, index) => ({
        id: index + 1,
        title: `Plan ${index + 1}`,
        phase: "in_progress",
        mode: "solo",
        state: index === 1 ? "paused" : "started",
        plan_agent_state: index === 0 ? "running" : "stopped",
        tasks: [index * 2 + 1, index * 2 + 2],
        done: index === 0 ? 1 : 0,
        waits_on: index === 0 ? "Role work" : "",
        waiting_on_you: index === 0,
        estimated_api_cost_usd: index === 0 ? 2.5 : null,
        estimated_api_cost_status: index === 0 ? "estimated" : "missing",
        cost_cap_usd: index === 0 ? 5 : 0,
        chat: index === 0 ? "plan-1" : "",
    }));
    api.organization.mockResolvedValue({
        plans,
        scheduled_plans: [{id: 900, title: "Nightly report", schedule: "daily", next_start: "2026-10-30T00:00:00+01:00"}],
        domains: [{id: "engineering", title: "Engineering", plans: [...plans, plans[0]]}],
    });
    store.settings = {plans: {plan_agents: true}};
    mount();
    await until(() => host.querySelector('[data-plan-id="1"] .organization-plan-title'));

    expect(api.organization).toHaveBeenCalledOnce();
    expect(host.querySelector("[data-home-plan-board] h1").textContent).toBe("Plans");
    expect(host.querySelector("[data-existing-home]")).not.toBeNull();
    expect(host.querySelectorAll("[data-domain]")).toHaveLength(0);
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(pageOf("plans"));
    expect(host.querySelector(".paged-cards-controls span").textContent).toContain(`1–${pageOf("plans")} of ${pageOf("plans") + 1} plans`);
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Estimated API cost: $2.50");
    expect(host.querySelector('[data-plan-id="2"]').textContent).toContain("Estimated API cost: Not reported");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Cost cap: $5.00");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Plan agent: running");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Solo");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Phase: In progress");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("1 of 2 done");
    expect(host.querySelector('[data-plan-id="1"]').textContent).toContain("Waits on: Role work");
    expect(host.querySelector('[data-plan-id="1"] a').textContent).toContain("Open its chat");
    expect(host.querySelector(".home-plan-board-scheduled").textContent).toContain("Starts on a schedule");
    expect(host.querySelector(".home-plan-board-scheduled").textContent).toContain("Nightly report");
    expect(host.querySelector(".home-plan-board-scheduled").textContent).toContain("Next start:");
    expect(host.querySelector(".home-plan-board-scheduled time").getAttribute("datetime")).toBe("2026-10-30T00:00:00+01:00");

    host.querySelector('button[aria-label="Next All In progress plans page"]').click();
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(1);
    expect(host.querySelector(".organization-plan-card").textContent).toContain("Plan 51");

    const filter = host.querySelector('select[aria-label="Filter plans"]');
    filter.value = "running";
    filter.dispatchEvent(new Event("change", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(1);
    expect(host.querySelector(".organization-plan-card").textContent).toContain("Plan 1");

    filter.value = "waiting";
    filter.dispatchEvent(new Event("change", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(1);
    expect(host.querySelector(".organization-plan-card").textContent).toContain("Plan 1");

    filter.value = "paused";
    filter.dispatchEvent(new Event("change", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(1);
    expect(host.querySelector(".organization-plan-card").textContent).toContain("Plan 2");

    filter.value = "scheduled";
    filter.dispatchEvent(new Event("change", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(0);
    expect(host.querySelector(".home-plan-board-scheduled").textContent).toContain("Nightly report");
});
