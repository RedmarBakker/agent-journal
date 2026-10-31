import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test} from "vitest";
import OrganizationPlanBoard from "../src/organization/OrganizationPlanBoard.vue";
import {organizationBoard} from "../src/state/organizationBoard.js";
import {pageOf} from "../src/sync/paging.js";

const sharedPlan = (phase, phase_name, tasks, done, waits_on) => ({
    id: 77,
    title: "The shared report",
    phase,
    phase_name,
    mode: "organization",
    tasks,
    done,
    waits_on,
});
const domains = [
    {
        id: "alpha",
        title: "Alpha",
        icon: "🧭",
        board: {planned: "Ready", in_progress: "Building", in_review: "Reviewing", done: "Complete"},
        plans: [
            sharedPlan("in_progress", "Building", [1, 2, 3], 1, "Role work"),
            {id: 78, title: "An older plan", phase: "done", mode: "solo", tasks: [4], done: 1, waits_on: ""},
        ],
    },
    {
        id: "beta",
        title: "Beta",
        icon: "📦",
        board: {planned: "Queued", in_progress: "Working", in_review: "Checking", done: "Finished"},
        plans: [sharedPlan("in_review", "Checking", [5, 6, 7, 8], 2, "a proof check or approval")],
    },
];

let app = null;
let host = null;

beforeEach(() => {
    organizationBoard.words = "";
    organizationBoard.hideDone = false;
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("one plan appears once in each domain's phase with its own progress, mode and wait", async () => {
    const sprintForecasts = [{
        sprint: {id: 7, starts_on: "2026-10-26", ends_on: "2026-11-09", state: "active", plan_ids: [77]},
        forecast: {as_of: "2026-10-30", status: "forecast", next_sprint_id: 23, plan_forecasts: [{plan_id: 77, status: "forecast", p50: "2026-11-06", probability_this_sprint: 71, probability_next_sprint: 27, probability_later: 2, carry_over: 29, delivered_outcomes: 15, method_version: "baseline-v1", capacity_freshness: "fresh"}]},
    }];
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {domains, sprintForecasts})});
    app.mount(host);
    await nextTick();

    const alpha = host.querySelector('[data-domain="alpha"]');
    const beta = host.querySelector('[data-domain="beta"]');
    expect(alpha.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    expect(beta.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    const alphaCard = alpha.querySelector('[data-phase="in_progress"] .organization-plan-card');
    const betaCard = beta.querySelector('[data-phase="in_review"] .organization-plan-card');
    expect(alphaCard.dataset.planId).toBe("77");
    expect(betaCard.dataset.planId).toBe("77");
    expect(host.querySelectorAll('[data-plan-id="77"]')).toHaveLength(2);
    expect(alpha.querySelector('[data-phase="in_progress"] h3').textContent).toContain("Building");
    expect(beta.querySelector('[data-phase="in_review"] h3').textContent).toContain("Checking");
    expect(alphaCard.textContent).toContain("Organization mode");
    expect(alphaCard.textContent).toContain("1 of 3 done");
    expect(alphaCard.textContent).toContain("Waits on: Role work");
    expect(betaCard.textContent).toContain("2 of 4 done");
    expect(betaCard.textContent).toContain("Waits on: a proof check or approval");
    expect(alphaCard.textContent).toContain("71% chance in Sprint 7");
    expect(alphaCard.textContent).toContain("baseline-v1");
    expect(alphaCard.textContent).not.toContain("Move to another sprint");

    const filter = host.querySelector('input[type="search"]');
    expect(filter.placeholder).toBe("Plan title, mode, or waiting reason");
    filter.value = "not on this board";
    filter.dispatchEvent(new Event("input", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(0);
    filter.value = "shared report";
    filter.dispatchEvent(new Event("input", {bubbles: true}));
    await nextTick();
    expect(host.querySelectorAll('[data-plan-id="77"]')).toHaveLength(2);

    host.querySelector('input[type="checkbox"]').click();
    await nextTick();
    expect(host.querySelector('[data-domain="alpha"] [data-phase="done"] .organization-plan-card')).toBeNull();
    expect(host.querySelector('[data-domain="alpha"] [data-phase="done"]').textContent).toContain("Completed plans are hidden.");
});

test("the shared board shows four loading lanes while it reads", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {loading: true})});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".organization-board-loading").getAttribute("aria-busy")).toBe("true");
    expect(host.querySelectorAll(".organization-board-loading .organization-board-lane")).toHaveLength(4);
});

test("the Plans view puts unfinished ended sprints first, then current, next and unscheduled plans", async () => {
    const plans = [
        {id: 21, title: "Waiting for deployment", phase: "done", state: "done", mode: "organization", tasks: [1], done: 1, story_points: {total: 13, done: 13, sized_tasks: 1, unknown_tasks: 0}},
        {id: 22, title: "Current plan", phase: "in_progress", state: "started", mode: "solo", tasks: [2], done: 0, story_points: {total: 5, done: null, sized_tasks: 1, unknown_tasks: 0}},
        {id: 23, title: "Next plan", phase: "planned", state: "ready", mode: "organization", tasks: [3], done: 0, story_points: {total: 8, done: null, sized_tasks: 1, unknown_tasks: 0}},
        {id: 24, title: "Later plan", phase: "planned", state: "ready", mode: "solo", tasks: [4], done: 0, story_points: {total: 3, done: null, sized_tasks: 1, unknown_tasks: 0}},
        {id: 25, title: "Delivered plan", phase: "done", state: "done", mode: "solo", tasks: [5], done: 1, story_points: {total: 2, done: 2, sized_tasks: 1, unknown_tasks: 0}},
        {id: 26, title: "Unscheduled plan", phase: "planned", state: "ready", mode: "solo", tasks: [6], done: 0, story_points: {total: null, done: null, sized_tasks: 0, unknown_tasks: 1}},
    ];
    const sprintForecasts = [
        {sprint: {id: 24, starts_on: "2026-11-23", ends_on: "2026-12-07", state: "draft", plan_ids: [24]}, forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 24, delivery_complete: false, status: "not enough history"}]}},
        {sprint: {id: 20, starts_on: "2026-09-28", ends_on: "2026-10-12", state: "closed", plan_ids: [25]}, forecast: {as_of: "2026-10-30", status: "forecast", plan_forecasts: [{plan_id: 25, delivery_complete: true, status: "forecast"}]}},
        {sprint: {id: 22, starts_on: "2026-10-26", ends_on: "2026-11-09", state: "active", plan_ids: [22]}, forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 22, delivery_complete: false, status: "not enough history"}]}},
        {sprint: {id: 23, starts_on: "2026-11-09", ends_on: "2026-11-23", state: "draft", plan_ids: [23]}, forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 23, delivery_complete: false, status: "not enough history"}]}},
        {sprint: {id: 21, starts_on: "2026-10-12", ends_on: "2026-10-26", state: "closed", plan_ids: [21]}, forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 21, delivery_complete: false, status: "not enough history", delivery_status: "awaiting deployment"}]}},
    ];
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {plans, sprintForecasts, view: "plans"})});
    app.mount(host);
    await nextTick();

    expect([...host.querySelectorAll("[data-sprint-group]")].map((group) => group.dataset.sprintId)).toEqual(["21", "22", "23", "24", "20", "none"]);
    expect(host.querySelector('[data-sprint-id="21"]').textContent).toContain("Waiting for deployment");
    expect(host.querySelector('[data-sprint-id="21"]').textContent).toContain("12 Oct to 25 Oct");
    expect(host.querySelector('[data-sprint-group][data-sprint-id="21"]').textContent).toContain("13 points");
    expect(host.querySelector('[data-sprint-id="23"]').textContent).toContain("Next plan");
    expect(host.querySelector('[data-sprint-id="24"]').textContent).toContain("Later plan");
    expect(host.querySelector('[data-sprint-id="20"]').textContent).toContain("Delivered plan");
    expect(host.querySelector('[data-plan-id="21"]').textContent).toContain("Not enough history yet");
    expect(host.querySelector('[data-plan-id="26"]').textContent).toContain("No sprint");
    expect(host.querySelector('[data-plan-id="26"]').textContent).toContain("Size unknown");
    expect(host.querySelector('[data-sprint-group][data-sprint-id="none"]').textContent).not.toContain("0 points");
});

test("the Board keeps each sprint together across its phase lanes", async () => {
    const plans = [
        {...sharedPlan("planned", "Ready", [1], 0, ""), id: 77},
        {...sharedPlan("in_review", "Checking", [2], 0, ""), id: 80},
        {id: 79, title: "Unscheduled", phase: "done", mode: "solo", tasks: [3], done: 1, waits_on: ""},
    ];
    const sprintForecasts = [{
        sprint: {id: 23, starts_on: "2026-11-09", ends_on: "2026-11-23", state: "draft", plan_ids: [80]},
        forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 80, status: "not enough history"}]},
    }, {
        sprint: {id: 22, starts_on: "2026-10-26", ends_on: "2026-11-09", state: "active", plan_ids: [77]},
        forecast: {as_of: "2026-10-30", status: "not enough history", plan_forecasts: [{plan_id: 77, status: "not enough history"}]},
    }];
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {plans, sprintForecasts, view: "board"})});
    app.mount(host);
    await nextTick();

    expect([...host.querySelectorAll("[data-sprint-group]")].map((group) => group.dataset.sprintId)).toEqual(["22", "23", "none"]);
    const sprintBoard = host.querySelector('[data-sprint-id="22"]');
    const nextSprintBoard = host.querySelector('[data-sprint-id="23"]');
    expect(sprintBoard.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    expect(nextSprintBoard.querySelectorAll(".organization-board-lane")).toHaveLength(4);
    expect(sprintBoard.querySelector('[data-phase="planned"] [data-plan-id="77"]')).not.toBeNull();
    expect(nextSprintBoard.querySelector('[data-phase="in_review"] [data-plan-id="80"]')).not.toBeNull();
    expect(host.querySelector('[data-sprint-group][data-sprint-id="none"] [data-phase="done"] [data-plan-id="79"]')).not.toBeNull();
    expect(host.querySelector('[data-plan-id="77"]').textContent).not.toContain("Move to another sprint");
});

test("a 13-domain organization with 50 Roles and many plans renders one page of cards per phase", async () => {
    let role = 0;
    const largeDomains = Array.from({length: 13}, (_, domainIndex) => ({
        id: `domain-${domainIndex + 1}`,
        title: `Domain ${domainIndex + 1}`,
        icon: "🧭",
        board: {planned: "Ready", in_progress: "Working", in_review: "Review", done: "Complete"},
        roles: Array.from({length: domainIndex < 11 ? 4 : 3}, () => ({id: `role-${++role}`})),
        plans: Array.from({length: 101}, (_, planIndex) => ({
            id: domainIndex * 1000 + planIndex + 1,
            title: `Plan ${domainIndex + 1}-${planIndex + 1}`,
            phase: "in_progress",
            mode: "organization",
            tasks: [planIndex + 1],
            done: 0,
            waits_on: "Role work",
        })),
    }));

    expect(largeDomains).toHaveLength(13);
    expect(largeDomains.reduce((total, domain) => total + domain.roles.length, 0)).toBe(50);
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {domains: largeDomains})});
    app.mount(host);
    await nextTick();

    expect(host.querySelectorAll(".organization-domain-board")).toHaveLength(13);
    expect(host.querySelectorAll(".organization-plan-card")).toHaveLength(13 * pageOf("plans"));
    const board = host.querySelector('[data-domain="domain-13"]');
    expect(board.querySelector('.organization-board-columns[role="region"]').tabIndex).toBe(0);
    expect(board.querySelectorAll(".organization-plan-card")).toHaveLength(pageOf("plans"));
    expect(board.querySelector(".paged-cards-controls span").textContent).toContain("1–50 of 101 plans");

    board.querySelector('button[aria-label="Next Domain 13 Working plans page"]').click();
    await nextTick();
    expect(board.querySelectorAll(".organization-plan-card")).toHaveLength(pageOf("plans"));
    expect(board.querySelector(".paged-cards-controls span").textContent).toContain("51–100 of 101 plans");
    board.querySelector('button[aria-label="Next Domain 13 Working plans page"]').click();
    await nextTick();
    expect(board.querySelectorAll(".organization-plan-card")).toHaveLength(1);
    expect(board.querySelector(".paged-cards-controls span").textContent).toContain("101–101 of 101 plans");
});
