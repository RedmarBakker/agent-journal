import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";

const api = {planTeam: vi.fn()};
vi.mock("../src/composables/scope.js", () => ({useScope: () => ({api})}));

const {default: PlanTeamSection} = await import("../src/resource/PlanTeamSection.vue");

let app = null;
let host = null;

beforeEach(() => {
    api.planTeam.mockReset().mockResolvedValue({
        domains: [{
            id: "alpha",
            title: "Alpha",
            seats: [
                {id: "builder-4", role_id: "builder", title: "Builder", state: "working", task_id: 17, task_title: "Lay the first boards", shared: false, estimated_api_cost_usd: 2.75},
                {id: "scout", role_id: "scout", title: "Scout", state: "waiting", task_id: 18, task_title: "Check the roof", shared: true, estimated_api_cost_usd: null},
                {id: "keeper", role_id: "keeper", title: "Keeper", state: "idle", task_id: null, task_title: "", shared: false, estimated_api_cost_usd: null},
            ],
        }],
        seat_cap: 6,
        estimated_api_cost_usd: 4.5,
        cost_cap_usd: 10,
    });
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function mount({plan = {id: 9, mode: "organization"}, readOnly = false, initial = null} = {}) {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanTeamSection, {plan, readOnly, initial})});
    app.mount(host);
    await nextTick();
}

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

test("an organization Plan shows seat state, per-seat estimates and the plan caps", async () => {
    await mount();
    await until(() => host.textContent.includes("$4.50"));

    expect(api.planTeam).toHaveBeenCalledWith(9);
    expect(host.textContent).toContain("Shared seat cap");
    expect(host.textContent).toContain("6 seats at once");
    expect(host.textContent).toContain("Estimated API cost cap");
    expect(host.textContent).toContain("$10.00");
    expect(host.textContent).toContain("Recorded plan estimate");

    const seats = [...host.querySelectorAll(".plan-team-seat")].map((seat) => seat.textContent);
    expect(seats[0]).toContain("Builder");
    expect(seats[0]).toContain("Working on task 17");
    expect(seats[0]).toContain("Lay the first boards");
    expect(seats[0]).toContain("$2.75");
    expect(seats[1]).toContain("Waiting in a shared Role's queue for task 18");
    expect(seats[1]).toContain("Check the roof");
    expect(seats[1]).toContain("Not measured");
    expect(seats[2]).toContain("Idle");
    expect(seats[2]).toContain("Not measured");
});

test("a read-only shared organization Plan uses its preloaded Team and the page only mounts Team for organization mode", async () => {
    const initial = {domains: [{id: "beta", title: "Beta", seats: [{id: "keeper", role_id: "keeper", title: "Keeper", state: "idle", task_id: null, task_title: "", shared: false, estimated_api_cost_usd: null}]}], seat_cap: 3, estimated_api_cost_usd: null, cost_cap_usd: 12};
    await mount({readOnly: true, initial});

    expect(api.planTeam).not.toHaveBeenCalled();
    expect(host.textContent).toContain("Keeper");
    expect(host.textContent).toContain("3 seats at once");

    const page = readFileSync(resolve(__dirname, "../src/resource/PlanPage.vue"), "utf8");
    const client = readFileSync(resolve(__dirname, "../src/api/client.js"), "utf8");
    expect(page).toMatch(/<PlanTeamSection v-if="planAgents && resource\.mode === 'organization'/);
    expect(page).toMatch(/:initial="readOnly \? resource\.plan_team : null"/);
    expect(client).toMatch(/planTeam\(id\)\s*\{\s*return this\.get\(this\.here\(`\/plans\/\$\{id\}\/team`\)\);/);
});
