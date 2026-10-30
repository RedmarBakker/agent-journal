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
    expect(host.textContent).toContain("Next sprint 27% · later 2% · carry-over 29%");
    expect(host.textContent).toContain("15 comparable deliveries");
    expect(host.textContent).toContain("delivery-baseline-v1");
    expect(host.querySelector("[data-chance-tone]").dataset.chanceTone).toBe("good");
});

test("delivery chance colors use the approved 70 and 40 percent thresholds", () => {
    expect(forecastTone(70)).toBe("good");
    expect(forecastTone(40)).toBe("caution");
    expect(forecastTone(39)).toBe("risk");
});

test("the plan forecast explains scope, delivery policy, ranges, history and freshness", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: mature, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("Delivery forecast");
    expect(host.textContent).toContain("Sprint ends");
    expect(host.textContent).toContain("Almost certain by 12 Nov");
    expect(host.textContent).toContain("71% this sprint");
    expect(host.textContent).toContain("Delivered task #101");
    expect(host.textContent).toContain("Current tasks #101, #102, #103");
    expect(host.textContent).toContain("27% next sprint");
    expect(host.textContent).toContain("2% later");
    expect(host.textContent).toContain("15 comparable deliveries");
    expect(host.textContent).toContain("28 days of observed capacity");
    expect(host.textContent).toContain("Capacity last observed 29 Oct · 1 day old");
    expect(host.textContent).toContain("delivery-baseline-v1");
    expect(host.textContent).toContain("A successful production deployment of the committed revision.");
    expect(host.textContent).toContain("1 task awaiting deployment for 3 days");
    expect(host.textContent).toContain("Capacity last observed 29 Oct · 1 day old");
    expect(host.querySelector("button")).toBeNull();
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

test("stale capacity remains visible beside the forecast method and update date", async () => {
    const stale = {...mature, capacity_freshness: "stale", capacity_age_days: 20};
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(DeliveryForecastPanel, {forecast: stale, sprint, plan: {state: "started"}})});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("20 days old · stale");
    expect(host.textContent).toContain("delivery-baseline-v1 · 30 Oct");
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
