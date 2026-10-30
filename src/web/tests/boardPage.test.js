import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

vi.mock("../src/pages/Home.vue", () => ({default: {template: "<section data-existing-home />"}}));

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

const {default: AppPages} = await import("../src/AppPages.vue");
const {api} = await import("../src/api/client.js");
const {store} = await import("../src/state/store.js");
const {PAGES} = await import("../src/route.js");

const plans = [
    {id: 1, title: "A planned report", phase: "planned", mode: "solo", tasks: [1, 2], done: 0, waits_on: "Approval"},
    {id: 2, title: "A running report", phase: "in_progress", mode: "organization", tasks: [3, 4], done: 1, waits_on: "Role work"},
    {id: 3, title: "A report in review", phase: "in_review", mode: "solo", tasks: [5], done: 1, waits_on: ""},
    {id: 4, title: "A finished report", phase: "done", mode: "organization", tasks: [6], done: 1, waits_on: ""},
];

let app = null;
let host = null;

beforeEach(() => {
    location.hash = "#/board";
    store.people = {hosted: false};
    store.settings = {plans: {plan_agents: false}};
    vi.spyOn(api, "organization").mockResolvedValue({plans, scheduled_plans: [], domains: []});
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    vi.restoreAllMocks();
    document.body.innerHTML = "";
});

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((resolve) => setTimeout(resolve, 10));
    await nextTick();
}

test("the Board page puts every plan in its shared four phase board with details and a plan link", async () => {
    expect(PAGES).toContain("board");
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(AppPages, {page: "board"})});
    app.mount(host);
    await until(() => host.querySelector('[data-plan-id="1"]'));

    expect(api.organization).toHaveBeenCalledOnce();
    expect(host.querySelectorAll(".organization-domain-board")).toHaveLength(1);
    expect(host.querySelectorAll(".organization-domain-board-head")).toHaveLength(0);
    expect(host.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(plans.length);
    expect([...host.querySelectorAll(".organization-board-lane")].map((lane) => lane.dataset.phase)).toEqual(["planned", "in_progress", "in_review", "done"]);
    for (const [phase, title] of [["planned", "A planned report"], ["in_progress", "A running report"], ["in_review", "A report in review"], ["done", "A finished report"]]) {
        expect(host.querySelectorAll(`[data-phase="${phase}"] .organization-plan-card`)).toHaveLength(1);
        expect(host.querySelector(`[data-phase="${phase}"] .organization-plan-card`).textContent).toContain(title);
    }
    for (const plan of plans) {
        const card = host.querySelector(`[data-plan-id="${plan.id}"]`);
        expect(card.querySelector(".organization-plan-title").getAttribute("aria-label")).toBe(`Open plan ${plan.title}`);
        expect(card.textContent).toContain(plan.mode === "organization" ? "Organization mode" : "Solo");
        expect(card.textContent).toContain(`${plan.done} of ${plan.tasks.length} done`);
        if (plan.waits_on) expect(card.textContent).toContain(`Waits on: ${plan.waits_on}`);
    }

    const running = host.querySelector('[data-plan-id="2"]');
    running.querySelector(".organization-plan-title").click();
    await nextTick();
    expect(location.hash).toContain("open=plans:2");
});
