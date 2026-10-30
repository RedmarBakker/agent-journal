import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import HomeDashboard from "../src/pages/HomeDashboard.vue";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
    vi.useRealTimers();
    vi.restoreAllMocks();
});

function list(rows = []) {
    return {rows, is_last_page: true, counts: {all: rows.length, open: rows.length, unread: 0}};
}

function dashboardScope({empty = false} = {}) {
    const now = Date.now() / 1000;
    const plans = empty ? [] : [
        {id: 8, title: "Release", mode: "organization", state: "started", tasks: [1, 2, 3], done: 1, plan_agent_state: "running", estimated_api_cost_usd: 9, estimated_api_cost_status: "estimated", cost_cap_usd: 10},
        {id: 9, title: "Fresh plan", mode: "solo", state: "started", tasks: [4, 5], done: 0, plan_agent_state: "running", estimated_api_cost_usd: 2, estimated_api_cost_status: "estimated", cost_cap_usd: 20},
    ];
    const question = {id: 30, table: "questions", text: "Should the deploy wait for the review?", creator: "agent:release", created_at: new Date((now - 60) * 1000).toISOString()};
    const approvalQuestion = {id: 90, table: "questions", text: "Approve the production deployment?", creator: "agent:release", created_at: new Date((now - 180) * 1000).toISOString()};
    const approval = {id: 12, table: "approvals", role: "Release Manager", plan_id: 8, task_id: 3, question_id: 90, decision: "pending", expires_at: new Date((now + 3600) * 1000).toISOString(), created_at: new Date((now - 180) * 1000).toISOString()};
    const secret = {id: 17, table: "secrets", title: "Mollie", fields: [{name: "API key", hidden: true, variable: "MOLLIE_API_KEY"}], filled: [], questioned_at: new Date((now - 300) * 1000).toISOString(), created_at: new Date((now - 600) * 1000).toISOString()};
    const worker = {id: 7, table: "workers", name: "Feature Implementation", role: "Feature Implementation", state: "dispatched", plan_id: 8, moves: {steps: [["dispatched", now - 3600]]}};
    const scope = {
        env: "main",
        rows: () => [],
        api: {
            organization: vi.fn().mockResolvedValue({plans}),
            homeDashboard: vi.fn().mockResolvedValue({
                blocked_tasks: empty ? [] : [{id: 20, title: "Deploy", plan_id: 8, block_reason: "", wait_reasons: ["task 21, \"Run the tests\", which Feature Implementation is still on"]}],
                latest_merges: empty ? [] : [{task_id: 1, task_title: "Write migration", plan_id: 8, branch: "release/upgrade", worker: "Feature Implementation", merged_at: new Date((now - 840) * 1000).toISOString(), added: 12, removed: 4}],
            }),
            planTasks: vi.fn(async (id) => id === 8
                ? [{id: 1, state: "completed", completed_at: new Date((now - 86400) * 1000).toISOString()}, {id: 2, state: "open"}, {id: 3, state: "open"}]
                : [{id: 4, state: "open"}, {id: 5, state: "open"}]),
            list: vi.fn(async (table, options = {}) => {
                if (table === "approvals") return list(empty ? [] : [approval]);
                if (table === "questions") return list(empty ? [] : [question, approvalQuestion]);
                if (table === "secrets") return list(empty ? [] : [secret]);
                if (table === "workers" && options.ids) return list(empty ? [] : [{...worker, task: {task_id: 1}}]);
                if (table === "workers") return list(empty ? [] : [worker]);
                if (table === "tasks" && options.ids) return list(empty ? [] : [{id: 1, title: "Write migration", plan_id: 8}]);
                return list();
            }),
            act: vi.fn().mockResolvedValue({...approval, decision: "approved", updater: "user:1"}),
        },
    };
    return scope;
}

async function mounted(scope, component = HomeDashboard, props = {}) {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(component, props)});
    app.provide("scope", scope);
    app.mount(host);
    for (let index = 0; index < 20; index++) await Promise.resolve();
    await nextTick();
    return host;
}

test("Home shows the approved dashboard cards, their live rows, and the honest task-rate finish estimate", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-30T12:00:00Z"));
    const scope = dashboardScope();
    const page = await mounted(scope);

    expect(page.querySelector("[data-home-dashboard] h1").textContent).toBe("Home");
    expect([...page.querySelectorAll("[data-dashboard-card]")].map((card) => card.dataset.dashboardCard)).toEqual(["waiting", "cost", "plans", "workers", "blocked", "merges"]);
    expect(page.querySelector('[data-stat="waiting"] .value').textContent).toBe("3");
    expect(page.querySelector('[data-stat="plans"] .value').textContent).toBe("2");
    expect(page.querySelector('[data-stat="workers"] .value').textContent).toBe("1");
    expect(page.querySelector('[data-stat="cost"] .value').textContent).toBe("$11.00");

    const waiting = page.querySelector('[data-dashboard-card="waiting"]');
    expect(waiting.textContent.indexOf("Should the deploy wait for the review?")).toBeLessThan(waiting.textContent.indexOf("Fill in MOLLIE_API_KEY"));
    expect(waiting.textContent).toContain("Fill in MOLLIE_API_KEY");
    expect(waiting.querySelector('[data-waiting-kind="question"]').textContent).toContain("Answer it");
    expect(waiting.querySelector('[data-waiting-kind="secret"]').textContent).toContain("Fill in the secret");
    const approve = [...waiting.querySelectorAll("button")].find((button) => button.textContent.includes("Approve"));
    expect(approve).not.toBeNull();
    expect(waiting.textContent).not.toContain("the secret value");
    approve.click();
    for (let index = 0; index < 10; index++) await Promise.resolve();
    await nextTick();
    expect(scope.api.act).toHaveBeenCalledWith("approvals", 12, "approve");

    const release = page.querySelector('[data-plan-id="8"]');
    expect(release.textContent).toContain("Release");
    expect(release.textContent).toContain("Organization mode");
    expect(release.textContent).toContain("1 of 3 tasks done");
    expect(release.querySelector("time.expected-finish").getAttribute("datetime")).toBe("2026-11-01");
    expect(page.querySelector('[data-dashboard-card="plans"]').textContent).toContain("simple estimate from tasks completed per day");
    expect(page.querySelector('[data-plan-id="9"]').textContent).toContain("No finish date yet: no task has finished");

    expect(page.querySelector('[data-worker-id="7"]').textContent).toContain("Task 1: Write migration");
    expect(page.querySelector('[data-worker-id="7"]').textContent).toContain("Feature Implementation");
    expect(page.querySelector('[data-worker-id="7"]').textContent).toContain("out for 1 h 0 min");
    expect(page.querySelector('[data-cost-plan-id="8"]').classList.contains("near-cap")).toBe(true);
    expect(page.querySelector('[data-cost-plan-id="8"]').textContent).toContain("$9.00 of $10.00");
    expect(page.querySelector('[data-blocked-task-id="20"]').textContent).toContain("Task 20: Deploy");
    expect(page.querySelector('[data-blocked-task-id="20"]').textContent).toContain("which Feature Implementation is still on");
    const merge = page.querySelector('[data-merge-task-id="1"]');
    expect(merge.textContent).toContain("Write migration");
    expect(merge.textContent).toContain("release/upgrade");
    expect(merge.textContent).toContain("by Feature Implementation");
    expect(merge.querySelector("time").getAttribute("datetime")).toContain("2026-10-30T11:46:00");
    expect(merge.textContent).toContain("+12");
    expect(merge.textContent).toContain("−4");
    expect(scope.api.homeDashboard).toHaveBeenCalledOnce();
    expect(scope.api.planTasks).toHaveBeenCalledTimes(2);
});

test("every dashboard card stays visible with a clear empty state", async () => {
    const page = await mounted(dashboardScope({empty: true}));

    expect(page.querySelectorAll("[data-dashboard-card]")).toHaveLength(6);
    expect(page.querySelector('[data-dashboard-card="waiting"]').textContent).toContain("Nothing is waiting on you.");
    expect(page.querySelector('[data-dashboard-card="plans"]').textContent).toContain("No plan is running.");
    expect(page.querySelector('[data-dashboard-card="workers"]').textContent).toContain("No worker is out.");
    expect(page.querySelector('[data-dashboard-card="blocked"]').textContent).toContain("No tasks are blocked.");
    expect(page.querySelector('[data-dashboard-card="cost"]').textContent).toContain("No cost estimate has been reported.");
    expect(page.querySelector('[data-dashboard-card="merges"]').textContent).toContain("No recent merges.");
});

test("the phone layout moves blocked work ahead of cost while desktop keeps the wider cards", async () => {
    const page = await mounted(dashboardScope({empty: true}));

    expect(page.querySelector('[data-dashboard-card="waiting"]').classList.contains("wide")).toBe(true);
    expect(page.querySelector('[data-dashboard-card="plans"]').classList.contains("wide")).toBe(true);
    expect(page.querySelector('[data-dashboard-card="cost"]').classList.contains("narrow")).toBe(true);
    expect(page.querySelector('[data-dashboard-card="blocked"]').classList.contains("phone-fourth")).toBe(true);
});

test("the Home route opens the dashboard", async () => {
    const {default: AppPages} = await import("../src/AppPages.vue");
    const page = await mounted(dashboardScope({empty: true}), AppPages, {page: "home"});

    expect(page.querySelector("[data-home-dashboard] h1").textContent).toBe("Home");
    expect(page.querySelectorAll("[data-dashboard-card]")).toHaveLength(6);
});
