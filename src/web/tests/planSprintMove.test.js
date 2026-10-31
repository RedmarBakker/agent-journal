import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const api = {sprints: vi.fn(), carryPlan: vi.fn()};
vi.mock("../src/composables/scope.js", () => ({useScope: () => ({api})}));

const {default:PlanSprintMove} = await import("../src/resource/PlanSprintMove.vue");

let app = null;
let host = null;
const current = {id: 21, state: "closed", starts_on: "2026-10-12", ends_on: "2026-10-26", starts_at: "2026-10-12T00:00:00Z", ends_at: "2026-10-26T00:00:00Z"};

beforeEach(() => {
    api.sprints.mockReset().mockResolvedValue([
        {id: 21, state: "closed", starts_on: "2026-10-12", ends_on: "2026-10-26", starts_at: "2026-10-12T00:00:00Z", ends_at: current.ends_at},
        {id: 22, state: "closed", starts_on: "2026-10-26", ends_on: "2026-11-09", starts_at: current.ends_at, ends_at: "2026-11-09T00:00:00Z"},
        {id: 23, state: "draft", starts_on: "2026-11-09", ends_on: "2026-11-23", starts_at: "2026-11-09T00:00:00Z", ends_at: "2026-11-23T00:00:00Z"},
    ]);
    api.carryPlan.mockReset().mockResolvedValue({});
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function mount(props) {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanSprintMove, props)});
    app.mount(host);
    await nextTick();
}

test("a closed sprint can be carried to a later open sprint with a reason", async () => {
    await mount({planId: 31, sprint: current});
    host.querySelector("button").click();
    await vi.waitFor(() => expect(document.body.querySelector('[role="dialog"]')?.textContent || "").toContain("Sprint 23"));
    expect(api.sprints).toHaveBeenCalledOnce();
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog.textContent).toContain("Sprint 23");
    expect(dialog.textContent).not.toContain("Sprint 22");
    expect(dialog.textContent).not.toContain("Reading later sprints");
    const reason = dialog.querySelector("textarea");
    reason.value = "The deployment is scheduled for the next period.";
    reason.dispatchEvent(new Event("input", {bubbles: true}));
    dialog.querySelector("select").value = "23";
    dialog.querySelector("select").dispatchEvent(new Event("change", {bubbles: true}));
    [...dialog.querySelectorAll("button")].find((button) => button.textContent.includes("Move plan")).click();
    await vi.waitFor(() => expect(api.carryPlan).toHaveBeenCalledWith(21, 31, 23, "The deployment is scheduled for the next period."));
});

test("a read-only plan never offers the sprint membership action", async () => {
    await mount({planId: 31, sprint: current, readOnly: true});

    expect(host.textContent).not.toContain("Move to another sprint");
    expect(api.sprints).not.toHaveBeenCalled();
    expect(api.carryPlan).not.toHaveBeenCalled();
});

test("an active sprint explains that its frozen commitment cannot move yet", async () => {
    await mount({planId: 31, sprint: {...current, state: "active"}});
    host.querySelector("button").click();
    await nextTick();

    expect(document.body.textContent).toContain("Its commitment is fixed until it closes.");
    expect(api.sprints).not.toHaveBeenCalled();
    expect(api.carryPlan).not.toHaveBeenCalled();
});
