import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
document.documentElement.classList.add("phone");

vi.mock("../src/pages/Home.vue", () => ({default: {template: "<section data-existing-home />"}}));

const {default: AppPages} = await import("../src/AppPages.vue");
const {default: PlanTimelinePanel} = await import("../src/resource/PlanTimelinePanel.vue");
const {choose} = await import("../src/state/environment.js");
const {store} = await import("../src/state/store.js");

let mounted = [];

beforeEach(() => document.documentElement.classList.add("phone"));

afterEach(() => {
    for (const {app, host} of mounted) {
        app.unmount();
        host.remove();
    }
    mounted = [];
    vi.unstubAllGlobals();
    document.documentElement.classList.remove("phone");
    document.body.innerHTML = "";
});

function mount(component, props = {}) {
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(component, props)});
    app.mount(host);
    mounted.push({app, host});
    return host;
}

test("on the phone, Home loads and shows the shared plan cards through the phone journal path", async () => {
    choose("main");
    store.people = {hosted: false};
    store.settings = {plans: {plan_agents: true}};
    const organization = {
        plans: [{
            id: 73,
            title: "Phone board plan",
            phase: "in_progress",
            mode: "organization",
            state: "started",
            tasks: [730, 731],
            done: 1,
            waits_on: "your answer",
            waiting_on_you: true,
            plan_agent_state: "running",
            chat: "plan-73",
            estimated_api_cost_usd: 1.25,
            cost_cap_usd: 4,
        }],
        scheduled_plans: [],
        domains: [],
    };
    const fetched = vi.fn(async () => new Response(JSON.stringify(organization), {status: 200, headers: {"Content-Type": "application/json"}}));
    vi.stubGlobal("fetch", fetched);

    const host = mount(AppPages, {page: "home"});
    await vi.waitFor(() => expect(host.querySelector('[data-plan-id="73"]')).not.toBeNull());

    expect(host.querySelector("[data-home-plan-board]")).not.toBeNull();
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Phone board plan");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Organization");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Phase: In progress");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("1 of 2 done");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Plan agent: running");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Estimated API cost: $1.25");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Cost cap: $4.00");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Waits on: your answer");
    expect(host.querySelector('[data-plan-id="73"] a').textContent).toContain("Open its chat");
    expect(fetched).toHaveBeenCalledOnce();
    expect(fetched.mock.calls[0][0]).toBe("/p/journal/organization");
    expect(fetched.mock.calls[0][1].headers["X-Phone"]).toBe("1");
    expect(fetched.mock.calls[0][1].headers["X-Journal-Viewer"]).toBeUndefined();
});

test("the Organization, Role and plan timeline screens say they open on the desktop", async () => {
    store.people = {hosted: false};
    store.settings = {plans: {plan_agents: true}};
    const fetched = vi.fn();
    vi.stubGlobal("fetch", fetched);

    for (const [page, notice] of [
        ["organization", "The organization screen opens on the desktop."],
        ["role", "The Role screen opens on the desktop."],
    ]) {
        const host = mount(AppPages, {page});
        await nextTick();
        expect(host.textContent).toContain(notice);
    }

    const timeline = mount(PlanTimelinePanel, {plan: {id: 73}});
    await nextTick();
    expect(timeline.textContent).toContain("The plan timeline opens on the desktop.");
    expect(fetched).not.toHaveBeenCalled();
});
