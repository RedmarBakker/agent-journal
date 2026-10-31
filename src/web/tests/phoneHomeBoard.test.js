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
    store.settings = {plans: {plan_agents: false}};
});

function mount(component, props = {}) {
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(component, props)});
    app.mount(host);
    mounted.push({app, host});
    return host;
}

test("on the phone, Home stays the dashboard and shows Plan agents through the phone journal path", async () => {
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

    expect(host.querySelector("[data-home-dashboard] h1").textContent).toBe("Home");
    expect(host.querySelector("[data-home-plan-board]")).toBeNull();
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Phone board plan");
    expect(host.querySelector('[data-plan-id="73"]').textContent).toContain("Plan agent: running");
    expect(host.querySelector('[data-plan-id="73"] .plan-agent-chat').textContent).toContain("Open its chat");
    expect(host.querySelector('[data-plan-id="73"] .plan-agent-chat').getAttribute("href")).toContain("#/chat");
    expect(host.querySelector('[data-cost-plan-id="73"]').textContent).toContain("$1.25 of $4.00");
    const organizationRequest = fetched.mock.calls.find(([url]) => url === "/p/journal/organization");
    expect(organizationRequest).toBeDefined();
    expect(organizationRequest[1].headers["X-Phone"]).toBe("1");
    expect(organizationRequest[1].headers["X-Journal-Viewer"]).toBeUndefined();
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
