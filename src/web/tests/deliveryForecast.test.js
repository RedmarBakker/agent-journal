import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test} from "vitest";
import DeliveryForecastLabel from "../src/organization/DeliveryForecastLabel.vue";
import DeliveryForecastPanel from "../src/resource/DeliveryForecastPanel.vue";
import {forecastTone} from "../src/domain/deliveryForecast.js";

const sprint = {
    id: 22,
    starts_on: "2026-10-26",
    ends_on: "2026-11-09",
    starts_at: "2026-10-25T22:00:00+00:00",
    ends_at: "2026-11-08T23:00:00+00:00",
    timezone: "Europe/Amsterdam",
    state: "active",
};

const mature = {
    status: "forecast",
    p50: "2026-11-06",
    p85: "2026-11-12",
    probability_this_sprint: 71,
    probability_next_sprint: 27,
    next_sprint_id: 23,
    probability_later: 2,
    carry_over: 29,
    delivered_outcomes: 15,
    minimum_comparable_outcomes: 10,
    observed_capacity_days: 28,
    minimum_capacity_days: 20,
    method_version: "delivery-baseline-v1",
    as_of: "2026-10-30",
    capacity_freshness: "fresh",
    capacity_observed_through: "2026-10-29",
    capacity_age_days: 1,
    current_end: "2026-11-09",
    next_end: "2026-11-23",
    delivery_status: "awaiting deployment",
    delivery_complete: false,
    execution_complete: true,
    delivered_scope: [101],
    awaiting_deploy_count: 1,
    awaiting_deploy_oldest_age_days: 3,
    current_scope: {task_ids: [101, 102, 103], task_count: 3, delivered_count: 1, remaining_count: 2, remaining_points: 8, unknown_size_tasks: 0},
    domain_criteria: [{domain: "development", criterion: "A successful production deployment of the committed revision.", evidence: "production_deployment", target: "production", version: "development-v1"}],
};

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("the plan label shows a likely finish and uses the delivery chance", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastLabel, {forecast: mature, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Likely finish 6 Nov");
    expect(host.textContent).toContain("71% chance in Sprint 22");
    expect(host.textContent).toContain("Sprint 23 27% · later 2% · carry-over 29%");
    expect(host.querySelector(".delivery-probability").getAttribute("aria-label")).toBe("71% in Sprint 22, 27% in Sprint 23, 2% later");
    expect(host.textContent).toContain("15 delivered plans");
    expect(host.textContent).toContain("Delivery chance uses past sprint results");
    expect(host.querySelector("[data-chance-tone]").dataset.chanceTone).toBe("good");
});

test("organization plan labels explain past sprint results and later task times", async () => {
    const forecast = {
        ...mature,
        duration_calibration: {status: "measured", observed_count: 10,
            coverage: {p50: {covered: 5, observed: 10, percent: 50}}},
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastLabel, {forecast, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("15 delivered plans");
    expect(host.textContent).toContain("Delivery chance uses past sprint results");
    expect(host.textContent).toContain("Compared with 10 later task results; the usual range included 50%");
    expect(host.textContent).toContain("Capacity through 29 Oct · 1 day old · fresh");
});

test("delivery chance colors use the approved 70 and 40 percent thresholds", () => {
    expect(forecastTone(100)).toBe("good");
    expect(forecastTone(70)).toBe("good");
    expect(forecastTone(69)).toBe("caution");
    expect(forecastTone(40)).toBe("caution");
    expect(forecastTone(39)).toBe("risk");
    expect(forecastTone(0)).toBe("risk");
    expect(forecastTone(null)).toBe("unknown");
});

test("plan cards color likely finishes green, amber and red at the approved thresholds", async () => {
    const forecasts = [70, 69, 39].map((probability) => ({...mature, probability_this_sprint: probability}));
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h("div", forecasts.map((forecast, index) => h(DeliveryForecastLabel, {
        key: index, forecast, sprint, plan: {state: "started"},
    })))});
    app.mount(host);
    await nextTick();

    const labels = [...host.querySelectorAll(".delivery-forecast-label")];
    expect(labels.map((label) => label.dataset.chanceTone)).toEqual(["good", "caution", "risk"]);
    expect(labels.map((label) => label.querySelector(".delivery-likely-finish").classList.contains(`tone-${label.dataset.chanceTone}`))).toEqual([true, true, true]);
});

test("a plan card with too little history shows no invented finish date or percentage", async () => {
    const cold = {...mature, status: "not enough history", p50: null, probability_this_sprint: null, delivered_outcomes: 0, as_of: null};
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastLabel, {forecast: cold, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Not enough history yet");
    expect(host.textContent).not.toContain("Likely finish");
    expect(host.textContent).not.toContain("6 Nov");
    expect(host.textContent).not.toMatch(/\b\d+%/);
});

test("the plan forecast explains scope, delivery policy, ranges, history and freshness", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: mature, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Delivery forecast");
    expect(host.textContent).toContain("Sprint ends 8 Nov");
    expect(host.textContent).toContain("Almost certain by 12 Nov");
    const bands = [...host.querySelectorAll(".forecast-bands div")];
    const currentBand = bands[0];
    expect(currentBand.querySelector("span").textContent).toBe("Sprint 22 (its sprint, 26 Oct to 8 Nov)");
    expect(currentBand.querySelector("strong").textContent).toBe("71%");
    expect(bands[1].querySelector("span").textContent).toBe("Sprint 23");
    expect(bands[1].querySelector("strong").textContent).toBe("27%");
    expect(bands[2].querySelector("span").textContent).toBe("Later");
    expect(bands[2].querySelector("strong").textContent).toBe("2%");
    expect(host.textContent).toContain("Delivered task #101");
    expect(host.textContent).toContain("Current tasks #101, #102, #103");
    expect(host.textContent).not.toContain("Next sprint");
    expect(host.textContent).toContain("15 delivered plans");
    expect(host.textContent).toContain("28 days of observed capacity");
    expect(host.textContent).toContain("Capacity last observed 29 Oct · 1 day old");
    expect(host.textContent).toContain("Based on past sprint results.");
    expect(host.textContent).toContain("A successful production deployment of the committed revision.");
    expect(host.textContent).toContain("1 task awaiting deployment for 3 days");
    expect(host.textContent).toContain("Capacity last observed 29 Oct · 1 day old");
    expect(host.querySelector("button")).toBeNull();
});

test("the dashboard compares saved estimates with later task times while keeping delivery chance based on sprint results", async () => {
    const forecast = {
        ...mature,
        duration_ranges: {
            status: "forecast",
            method_version: "bayesian-log-linear-duration-v1",
            history: {completed_observations: 24, observed_through: "2026-10-29", age_days: 1, freshness: "fresh", recency_half_life_days: 180},
            tasks: [{task_id: 101, comparable_examples: [{task_id: 99, plan_id: 8, title: "prior release",
                original_size_points: 5, execution_size_points: 3, execution_seconds: 3600, delivery_seconds: 7200}]}],
        },
        duration_calibration: {
            status: "measured",
            prediction_count: 14,
            observed_count: 10,
            minimum_calibration_samples: 5,
            coverage: {p50: {covered: 5, observed: 10, percent: 50}, raw_p85: {covered: 8, observed: 10, percent: 80},
                empirical_p50: {covered: 4, observed: 10, percent: 40}, empirical_p85: {covered: 6, observed: 10, percent: 60}},
            sizing_bias: {
                execution_cycle: {status: "measured", observed: 5, actual_to_predicted_p50_ratio: 1.5},
                delivery_delay: {status: "not_enough_history", observed: 2, actual_to_predicted_p50_ratio: null},
            },
        },
        network_forecast: {comparison: {selection: "none"}},
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Based on past sprint results.");
    expect(host.textContent).toContain("Ranges come from past delivered tasks; they are advice only. The wider range included 80% of 10 finished task times.");
    expect(host.textContent).toContain("24 finished task times · last observed 29 Oct · 1 day old · fresh");
    expect(host.textContent).toContain("Compared with 10 later task results from 14 saved estimates, the usual range included 50% and the wider range included 80%.");
    expect(host.textContent).toContain("Past task times alone included 40% in the usual range and 60% in the wider range.");
    expect(host.textContent).toContain("These ranges do not change the delivery chance.");
    expect(host.textContent).toContain("Across 5 finished tasks, work took 1.5 times as long as estimated.");
    expect(host.textContent).toContain("Not enough finished tasks to compare delivery-time estimates (2 of 5).");
    expect(host.textContent).toContain("The shared dependency estimate is shown for comparison only");
    expect(host.textContent).toContain("Similar finished tasks");
    expect(host.textContent).toContain("Task #99 · original estimate 5 points · finished size 3 points · work took 1.0 hours · delivery took 2.0 hours after work finished");
    expect(host.textContent).not.toMatch(/empirical baseline|authorized cohort|held-out actuals|sizing-bias score/i);
    expect(host.querySelectorAll(".forecast-bands div")).toHaveLength(3);
    expect(host.textContent).not.toContain("points per hour");
});

test("cold history explains the missing task results and keeps learned ranges advisory", async () => {
    const forecast = {
        ...mature,
        duration_ranges: {status: "not_enough_history", method_version: "bayesian-log-linear-duration-v1",
            history: {completed_observations: 0, observed_through: null, age_days: null, freshness: "unknown", recency_half_life_days: 180}},
        duration_calibration: {status: "not_enough_history", prediction_count: 0, observed_count: 0, minimum_calibration_samples: 5,
            coverage: {p50: {covered: 0, observed: 0, percent: null}, raw_p85: {covered: 0, observed: 0, percent: null}},
            sizing_bias: {execution_cycle: {status: "not_enough_history", observed: 0, actual_to_predicted_p50_ratio: null}}},
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Based on past sprint results.");
    expect(host.textContent).toContain("Learned ranges: not enough history yet.");
    expect(host.textContent).toContain("Not enough finished tasks to compare work-time estimates (0 of 5).");
    expect(host.textContent).not.toContain("actual durations were");
    expect(host.textContent).not.toMatch(/empirical baseline|authorized cohort|held-out actuals|sizing-bias score/i);
    expect(host.textContent).toContain("71%");
    expect(host.textContent).not.toContain("points per hour");
});

test("the plan page shows the critical path, task slack and independent work from the forecast", async () => {
    const forecast = {
        ...mature,
        critical_path: {
            status: "estimated",
            basis: "shared P50 task durations",
            p50_finish: "2026-11-05",
            critical_path_task_ids: [201, 202],
            critical_task_ids: [201, 202],
            independent_groups: [[203]],
            external_conditions: [],
            edges: [{task_id: 202, prerequisite_id: 201, kind: "prerequisite", external: false}],
            tasks: [
                {task_id: 201, p50_duration_days: 2, earliest_start: "2026-10-30", earliest_finish: "2026-11-01", latest_start: "2026-10-30", latest_finish: "2026-11-01", slack_days: 0, critical: true},
                {task_id: 202, p50_duration_days: 3, earliest_start: "2026-11-01", earliest_finish: "2026-11-04", latest_start: "2026-11-01", latest_finish: "2026-11-04", slack_days: 0, critical: true},
                {task_id: 203, p50_duration_days: 4, earliest_start: "2026-10-30", earliest_finish: "2026-11-03", latest_start: "2026-10-31", latest_finish: "2026-11-04", slack_days: 1, critical: false},
            ],
        },
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Critical path: #201 → #202");
    expect(host.textContent).toContain("P50 finish 5 Nov");
    expect(host.textContent).toContain("Task #203 · P50 4 days");
    expect(host.textContent).toContain("1 day of slack");
    expect(host.textContent).toContain("Independent work: task #203");
});

test("a structural plan graph names an unresolved cross-plan gate without date or slack claims", async () => {
    const forecast = {
        ...mature,
        critical_path: {
            status: "structural",
            basis: "structural dependency graph",
            p50_finish: null,
            critical_path_task_ids: [],
            critical_task_ids: [],
            independent_groups: [],
            edges: [{task_id: 101, prerequisite_id: 900, kind: "delivery_gate", external: true}],
            external_conditions: [{task_id: 101, prerequisite_id: 900, kind: "delivery_gate", external: true, status: "unresolved"}],
            tasks: [{task_id: 101, p50_duration_days: null, earliest_start: null, earliest_finish: null, latest_start: null, latest_finish: null, slack_days: null, critical: false}],
        },
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("The dependency graph is structural. Start, finish and slack are unknown.");
    expect(host.textContent).toContain("Cross-plan delivery gate from task #101 to task #900 is unresolved");
    expect(host.textContent).not.toContain("P50 finish");
    expect(host.textContent).not.toContain("days of slack");
});

test("a cold completed development plan says it is not deployed and invents no date or chance", async () => {
    const cold = {
        ...mature,
        status: "not enough history",
        p50: null,
        p85: null,
        probability_this_sprint: null,
        probability_next_sprint: null,
        probability_later: null,
        carry_over: null,
        delivered_outcomes: 0,
        observed_capacity_days: 0,
        delivered_scope: [],
        awaiting_deploy_count: 2,
        awaiting_deploy_oldest_age_days: null,
        current_scope: {task_count: 2, delivered_count: 0, remaining_count: 2, remaining_points: null, unknown_size_tasks: 1},
        missing_evidence: ["comparable delivery history", "observed capacity", "story points"],
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: cold, sprint, plan: {state: "done"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Not enough history yet");
    expect(host.textContent).toContain("All tasks done, not deployed yet");
    expect(host.textContent).toContain("2 tasks awaiting deployment");
    expect(host.textContent).toContain("1 task has no size");
    expect(host.textContent).not.toContain("0 points remain");
    expect(host.textContent).toContain("A successful production deployment of the committed revision.");
    expect(host.textContent).not.toContain("Likely finish");
    expect(host.textContent).not.toMatch(/\b\d+%/);
    expect(host.querySelector("button")).toBeNull();
});

test("stale capacity remains visible beside the forecast update date", async () => {
    const stale = {...mature, capacity_freshness: "stale", capacity_age_days: 20};
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: stale, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("20 days old · stale");
    expect(host.textContent).toContain("30 Oct");
    expect(host.textContent).toContain("Delivery chance uses past sprint results");
});

test("a missing definition of done is named instead of hidden", async () => {
    const missing = {...mature, domain_criteria: [], missing_criteria: ["Definition of done is not set for development."]};
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: missing, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Definition of done is not set for development.");
});

test("a delivered plan names its accepted deployment date", async () => {
    const delivered = {...mature, delivery_complete: true, latest_delivery_at: "2026-10-28T12:00:00+00:00"};
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastLabel, {forecast: delivered, sprint, plan: {state: "done"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Delivered · deployed 28 Oct.");
});

test("an unscheduled plan has a clear sprint remedy without forecast numbers", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastLabel, {forecast: null, sprint: null, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("No sprint");
    expect(host.textContent).toContain("Put this plan in a sprint");
    expect(host.textContent).not.toMatch(/\b\d+%/);
});
