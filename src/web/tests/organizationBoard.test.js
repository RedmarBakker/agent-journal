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
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(OrganizationPlanBoard, {domains})});
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
