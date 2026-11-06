import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const api = {supervisorRecords: vi.fn(), list: vi.fn()};
vi.mock("../src/api/client.js", async (importOriginal) => ({...(await importOriginal()), api}));

const {default: SupervisorPage} = await import("../src/pages/SupervisorPage.vue");
const {pageTitle} = await import("../src/composables/pageTitle.js");

let app = null;
let host = null;

const summary = (runs, receipts, verified) => ({runs, receipts, verified_receipts: verified});
const records = (status, current, previous) => ({
    status,
    current,
    previous,
    records: [],
    waiting_proposals: 3,
    next_before: null,
    areas: ["checks", "plans-and-tasks"],
});

beforeEach(() => {
    location.hash = "#/supervisor?sub=dashboard";
    api.supervisorRecords.mockReset().mockResolvedValue(records(
        "on",
        summary(9, {applied: 7, conflicted: 2, proposed: 3, rejected: 1}, 5),
        summary(5, {applied: 4, conflicted: 2, proposed: 1, rejected: 2}, 3),
    ));
    api.list.mockReset().mockResolvedValue({rows: [{id: 2, title: "Second plan"}, {id: 1, title: "First plan"}]});
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
    await vi.waitFor(() => expect(api.supervisorRecords).toHaveBeenCalled());
    await vi.waitFor(() => expect(host.querySelector("[data-supervisor-dashboard], [data-record-fault]")).not.toBeNull());
    await vi.waitFor(() => expect(host.querySelector(".supervisor-loading")).toBeNull());
    return host;
}

test("the viewer title follows the Supervisor sub-page", async () => {
    await vi.waitFor(() => expect(pageTitle.value).toBe("Supervisor › Dashboard"));
});

test("the Dashboard reads owner records and compares built action counts with the previous period", async () => {
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-action="applied"] .stat-value').textContent).toBe("7"));

    expect(api.supervisorRecords).toHaveBeenCalledWith({period: "last_7_days", planId: "", area: ""});
    expect([...page.querySelectorAll(".summary-label")].map((label) => label.textContent)).toEqual([
        "Status", "Wake-ups", "Today's cost", "Waiting for you",
    ]);
    expect(page.querySelector('[data-summary-status] .summary-value').textContent).toBe("Supervisor on");
    expect(page.querySelector('[data-action="applied"] .stat-comparison').textContent).toContain("3 more than before (4)");
    expect(page.querySelector('[data-stat="wake-ups"] .not-built-yet').textContent).toBe("Not built yet");
    expect(page.querySelector('[data-stat="today-cost"] .not-built-yet').textContent).toBe("Not built yet");
    expect(page.querySelector('[data-stat="waiting"] .summary-value').textContent).toBe("3");
});

test("the period, plan and area filters are read from the owner route", async () => {
    const page = await openPage();
    const plan = page.querySelector('select[aria-label="Plan"]');
    const area = page.querySelector('select[aria-label="Area"]');

    page.querySelector('.segmented-option[role="radio"]:first-child').click();
    plan.value = "2";
    plan.dispatchEvent(new Event("change", {bubbles: true}));
    area.value = "checks";
    area.dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorRecords).toHaveBeenLastCalledWith({period: "today", planId: "2", area: "checks"}));
});

test("a never set up Supervisor shows the document 13 empty message without invented totals", async () => {
    api.supervisorRecords.mockResolvedValue(records(
        "never_set_up",
        summary(0, {applied: 0, conflicted: 0, proposed: 0, rejected: 0}, 0),
        summary(0, {applied: 0, conflicted: 0, proposed: 0, rejected: 0}, 0),
    ));
    const page = await openPage();

    expect(page.querySelector('[data-summary-status] .summary-value').textContent).toBe("Never set up");
    expect(page.textContent).toContain("The supervisor is not set up for this environment.");
    expect(page.querySelector('[data-summary-status] [data-supervisor-setup]').getAttribute("href")).toBe("#/plans");
    expect(page.textContent).toContain("The supervisor has not woken in this period.");
    expect(page.querySelector('[data-stat="today-cost"] .not-built-yet').textContent).toBe("Not built yet");
    expect(page.querySelector('[data-action="applied"]')).toBeNull();
});

test("an off Supervisor keeps past action figures and labels them as past", async () => {
    api.supervisorRecords.mockResolvedValue(records(
        "off",
        summary(4, {applied: 3, conflicted: 0, proposed: 1, rejected: 0}, 2),
        summary(2, {applied: 1, conflicted: 0, proposed: 1, rejected: 0}, 1),
    ));
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-action="applied"] .stat-value').textContent).toBe("3"));

    expect(page.querySelector('[data-summary-status] .summary-value').textContent).toBe("Supervisor off");
    expect(page.textContent).toContain("The supervisor is off.");
    expect(page.textContent).toContain("These figures are from before it was turned off.");
});

test("a failed owner read explains the fault and does not show zero figures", async () => {
    api.supervisorRecords.mockRejectedValue(new Error("connection refused"));
    const page = await openPage();
    await vi.waitFor(() => expect(page.textContent).toContain("connection refused"));

    expect(page.textContent).toContain("Could not read the supervisor's records");
    expect(page.querySelector('[data-action="applied"]')).toBeNull();
    expect(page.querySelector('[data-summary-status]')).toBeNull();
});
