import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const api = {supervisorCosts: vi.fn(), supervisorControl: vi.fn()};
vi.mock("../src/api/client.js", () => ({api}));

const {default: SupervisorPage} = await import("../src/pages/SupervisorPage.vue");

const fullCosts = {
    status: "on",
    periods: {
        today: {days: 1, known_usd: "0.40", unknown_runs: 1, runs: 2, known_runs: 1, wakeups: 3},
        week: {days: 7, known_usd: "0.60", unknown_runs: 1, runs: 4, known_runs: 3, wakeups: 6},
        month: {days: 30, known_usd: "1.10", unknown_runs: 1, runs: 5, known_runs: 4, wakeups: 7},
    },
    averages: {
        per_wakeup: {usd: "0.20", known_runs: 3, unknown_runs: 1},
        per_action: {usd: "0.15", known_actions: 4, unknown_runs: 1},
        per_useful_result: {usd: "0.20", known_results: 2, unknown_results: 0},
    },
    per_plan: [
        {plan_id: 24, title: "Release 2.41", known_usd: "0.40", unknown_runs: 0},
        {plan_id: 31, title: "Prospect list", known_usd: "0.20", unknown_runs: 1},
    ],
    per_area: [
        {area_key: "checks", title: "Checks", known_usd: "0.45", unknown_runs: 0},
        {area_key: "plans-and-tasks", title: "Plans and tasks", known_usd: "0.15", unknown_runs: 1},
    ],
    quiet_savings: {quiet_wakeups: 2, estimated_usd: "0.40"},
    wakeups_per_day: Array.from({length: 7}, (_, index) => ({
        date: `2026-11-0${index + 2}`, total: index === 6 ? 3 : 1, quiet: index === 6 ? 2 : 0,
    })),
    daily_trend: Array.from({length: 30}, (_, index) => ({
        date: new Date(Date.UTC(2026, 9, index + 4)).toISOString().slice(0, 10),
        known_usd: index === 29 ? null : "0.00",
        unknown_runs: index === 29 ? 1 : 0,
    })),
};

const emptyCosts = {
    status: "never_set_up",
    periods: Object.fromEntries(["today", "week", "month"].map((key) => [key, {
        days: key === "today" ? 1 : key === "week" ? 7 : 30,
        known_usd: "0.00", unknown_runs: 0, runs: 0, known_runs: 0, wakeups: 0,
    }])),
    averages: {
        per_wakeup: {usd: null, known_runs: 0, unknown_runs: 0},
        per_action: {usd: null, known_actions: 0, unknown_runs: 0},
        per_useful_result: {usd: null, known_results: 0, unknown_results: 0},
    },
    per_plan: [], per_area: [], quiet_savings: {quiet_wakeups: 0, estimated_usd: null},
    wakeups_per_day: Array.from({length: 7}, (_, index) => ({date: `2026-11-0${index + 2}`, total: 0, quiet: 0})),
    daily_trend: Array.from({length: 30}, (_, index) => ({
        date: new Date(Date.UTC(2026, 9, index + 4)).toISOString().slice(0, 10),
        known_usd: "0.00", unknown_runs: 0,
    })),
};

const unknownCosts = {
    ...emptyCosts,
    status: "on",
    periods: Object.fromEntries(["today", "week", "month"].map((key) => [key, {
        days: key === "today" ? 1 : key === "week" ? 7 : 30,
        known_usd: "0.00", unknown_runs: 1, runs: 1, known_runs: 0, wakeups: 1,
    }])),
    per_plan: [{plan_id: 31, title: "Prospect list", known_usd: "0.00", unknown_runs: 1}],
    per_area: [{area_key: "checks", title: "Checks", known_usd: "0.00", unknown_runs: 1}],
    daily_trend: Array.from({length: 30}, (_, index) => ({
        date: new Date(Date.UTC(2026, 9, index + 4)).toISOString().slice(0, 10),
        known_usd: index === 29 ? null : "0.00",
        unknown_runs: index === 29 ? 1 : 0,
    })),
};

let app = null;
let host = null;

beforeEach(() => {
    location.hash = "#/supervisor?sub=cost";
    api.supervisorCosts.mockReset().mockResolvedValue(fullCosts);
    api.supervisorControl.mockReset().mockResolvedValue({grant: {
        wake_interval_minutes: 15,
        limits: {max_cost_microusd_per_day: 5000000},
    }});
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function openPage() {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(SupervisorPage)});
    app.directive("tip", {});
    app.mount(host);
    await vi.waitFor(() => expect(api.supervisorCosts).toHaveBeenCalled());
    await vi.waitFor(() => expect(host.querySelector("[data-supervisor-costs], [data-cost-fault]")).not.toBeNull());
    await vi.waitFor(() => expect(host.querySelector(".cost-loading")).toBeNull());
    return host;
}

test("the owner sees cost limits, averages, plan and area totals, intervals, quiet savings and 30 days", async () => {
    const page = await openPage();

    expect(page.querySelector('[data-cost-period="today"]').textContent).toContain("$0.40");
    expect(page.querySelector('[data-cost-period="today"]').textContent).toContain("Not known");
    expect(page.querySelector('[data-cost-period="today"]').textContent).toContain("$5.00");
    expect(page.querySelector('[data-cost-period="week"]').textContent).toContain("$35.00");
    expect(page.querySelector('[data-cost-period="month"]').textContent).toContain("$150.00");
    expect(page.textContent).toContain("Cost per wake-up");
    expect(page.textContent).toContain("Cost per action");
    expect(page.textContent).toContain("Cost per useful result");
    expect(page.textContent).toContain("Release 2.41");
    expect(page.textContent).toContain("Prospect list");
    expect(page.textContent).toContain("Checks");
    expect(page.textContent).toContain("Plans and tasks");
    expect(page.textContent).toContain("Cost per interval");
    expect(page.textContent).toContain("Every 15 minutes");
    expect(page.textContent).toContain("Saved by skipping quiet wake-ups");
    expect(page.textContent).toContain("Wake-ups per day");
    expect(page.querySelectorAll("[data-trend-day]")).toHaveLength(30);
    expect(page.querySelector("[data-cost-cap-line]")).not.toBeNull();
    expect(api.supervisorControl).toHaveBeenCalled();
});

test("an empty cost history says no cost has been recorded", async () => {
    api.supervisorCosts.mockResolvedValue(emptyCosts);
    const page = await openPage();

    expect(page.textContent).toContain("No cost recorded.");
    expect(page.querySelectorAll("[data-trend-day]")).toHaveLength(0);
});

test("unknown costs stay marked Not known in totals, groups and the trend", async () => {
    api.supervisorCosts.mockResolvedValue(unknownCosts);
    const page = await openPage();

    expect(page.textContent).toContain("Not known");
    expect(page.querySelector('[data-trend-day][data-cost-status="unknown"]')).not.toBeNull();
    expect(page.querySelector('[data-cost-period="today"]').textContent).not.toContain("$0.00");
    expect(page.textContent).not.toContain("$0.00");
});
