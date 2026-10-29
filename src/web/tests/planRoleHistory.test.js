import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";

const api = {planRoles: vi.fn()};
vi.mock("../src/composables/scope.js", () => ({useScope: () => ({api})}));

const {default: PlanRoleHistory} = await import("../src/resource/PlanRoleHistory.vue");
const {store} = await import("../src/state/store.js");

let app = null;
let host = null;

beforeEach(() => {
    api.planRoles.mockReset().mockResolvedValue({
        current_role: "keeper",
        steps: [
            {role: "keeper", task: 17, title: "Check the floors", time: 1793271600},
            {role: "scout", task: 18, title: "Check the roof", time: 1793275200},
        ],
    });
    store.organization = {domains: [{roles: [{id: "keeper", title: "Keeper"}, {id: "scout", title: "Scout"}]}]};
    store.summary = {environments: [{environment: {name: "plan-3"}, agent: {stack: [{name: "role_work", values: {role: "keeper"}}]}}]};
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function mount(initial = null) {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanRoleHistory, {plan: {id: 3, mode: "solo", chat: "plan-3"}, initial})});
    app.mount(host);
    await nextTick();
}

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

test("a solo Plan page shows its current Role and every Role step with its task", async () => {
    await mount();
    await until(() => host.querySelectorAll(".plan-role-steps li").length === 2);

    expect(api.planRoles).toHaveBeenCalledWith(3);
    expect(host.querySelector(".plan-role-current").textContent).toBe("Current Role: Keeper");
    const steps = [...host.querySelectorAll(".plan-role-steps li")].map((step) => step.textContent);
    expect(steps[0]).toContain("Keeper");
    expect(steps[0]).toContain("Task 17 · Check the floors");
    expect(steps[1]).toContain("Scout");
    expect(steps[1]).toContain("Task 18 · Check the roof");
});

test("Role history is only mounted for a solo plan when Plan agents are enabled", () => {
    const page = readFileSync(resolve(__dirname, "../src/resource/PlanPage.vue"), "utf8");
    expect(page).toMatch(/<PlanRoleHistory v-if="planAgents && resource\.mode === 'solo'/);
    expect(page).toMatch(/:initial="readOnly \? resource\.plan_agent_roles : null"/);
});

test("a shared plan uses its preloaded Role history without calling the journal API", async () => {
    const initial = {current_role: "keeper", steps: [{role: "keeper", task: 17, title: "Check the floors", time: 1793271600}]};
    await mount(initial);
    await nextTick();

    expect(api.planRoles).not.toHaveBeenCalled();
    expect(host.textContent).toContain("Task 17 · Check the floors");
});
