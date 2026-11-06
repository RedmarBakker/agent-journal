import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const api = {supervisorHistory: vi.fn(), supervisorControl: vi.fn(), supervisorUndo: vi.fn(), supervisorProposal: vi.fn(), supervisorFeedback: vi.fn(), supervisorFeedbackRule: vi.fn(), list: vi.fn()};
vi.mock("../src/api/client.js", async (importOriginal) => ({...(await importOriginal()), api}));

const {default: SupervisorPage} = await import("../src/pages/SupervisorPage.vue");

let app = null;
let host = null;

const action = (tier, overrides = {}) => ({
    area: "Checks",
    area_key: "checks",
    title: "Edit check",
    tier,
    status: "applied",
    receipt_status: "applied",
    receipt_id: 911,
    changes: [{field: "interval", before: "15 minutes", after: "30 minutes"}],
    undo_available: tier === 1,
    ...overrides,
});

const row = (id, overrides = {}) => ({
    id,
    created_at: new Date(Date.UTC(2026, 10, 2, 12) - (301 - id) * 60000).toISOString(),
    woken_by: "Event: Failed check",
    plan_id: 31,
    result: "Acted",
    what_saw: "Check 8 failed: connection timed out.",
    what_chose: "Edit check",
    why: "The check has failed repeatedly.",
    cost: {status: "known", usd: "0.07"},
    actions: [action(1)],
    ...overrides,
});

const fullHistory = [
    row(301),
    row(300, {
        result: "Skipped as quiet",
        kind: "quiet",
        quiet_count: 4,
        what_saw: "No relevant changes were found.",
        what_chose: "Skip this wake-up.",
        why: "No change to investigate.",
        cost: {status: "known", usd: "0.00"},
        actions: [],
    }),
    row(299, {result: "Proposed", actions: [action(2, {undo_available: false})]}),
    ...Array.from({length: 97}, (_, index) => row(298 - index, {actions: [action(2, {undo_available: false})]})),
];

const response = (status, history, nextHistoryBefore = null) => ({
    status,
    history,
    next_before: nextHistoryBefore,
    areas: ["checks", "plans-and-tasks"],
});

beforeEach(() => {
    location.hash = "#/supervisor?sub=decisions";
    api.supervisorHistory.mockReset().mockResolvedValue(response("on", fullHistory, "1234:202"));
    api.supervisorControl.mockReset().mockResolvedValue({grant_id: "grant-7"});
    api.supervisorUndo.mockReset().mockResolvedValue({status: "undone"});
    api.supervisorProposal.mockReset().mockResolvedValue({decision: "accepted"});
    api.supervisorFeedback.mockReset().mockResolvedValue({feedback: {useful: null, comment: "", correction: "", rule_id: null}});
    api.supervisorFeedbackRule.mockReset().mockResolvedValue({rule: {id: 17, text: "For Plan 31 in Checks: inspect before changing the interval."}});
    api.list.mockReset().mockResolvedValue({rows: [{id: 31, title: "Pricing for add-ons"}]});
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
    await vi.waitFor(() => expect(api.supervisorHistory).toHaveBeenCalled());
    await vi.waitFor(() => expect(host.querySelector("[data-supervisor-decisions], [data-history-fault]")).not.toBeNull());
    await vi.waitFor(() => expect(host.querySelector(".history-loading")).toBeNull());
    return host;
}

test("the owner sees complete wake-up history, filters it, undoes tier one actions and loads 100 older rows", async () => {
    const olderRows = [row(200), row(199), row(198)];
    api.supervisorHistory.mockImplementation(({before} = {}) => Promise.resolve(
        before ? response("on", olderRows) : response("on", fullHistory, "1234:202"),
    ));
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="301"] button')).not.toBeNull());
    await vi.waitFor(() => expect(page.textContent).toContain("Pricing for add-ons"));

    expect(page.querySelectorAll("[data-history-row]")).toHaveLength(100);
    expect(page.querySelector('[data-history-row="301"] .history-result').textContent).toBe("Acted");
    for (const label of ["When", "Woken by", "Plan", "Result", "Cost"]) {
        expect(page.querySelector('[data-history-row="301"]').textContent).toContain(label);
    }
    expect(new Date(page.querySelector('[data-history-row="301"] time').dateTime).getTime())
        .toBeGreaterThan(new Date(page.querySelector('[data-history-row="300"] time').dateTime).getTime());
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("What it saw");
    expect(page.querySelector('[data-history-row="301"]')
        .textContent).toContain("Check 8 failed: connection timed out.");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("What it chose");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("Why");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("Before");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("After");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("Receipt 911");
    expect(page.querySelector('[data-history-row="301"] .history-action').textContent).toContain("Checks");
    expect(page.querySelector('[data-history-row="301"] .history-tier').textContent).toBe("Tier 1");
    const undo = [...page.querySelectorAll('[data-history-row="301"] button')]
        .find((button) => button.textContent.trim() === "Undo");
    expect(undo).toBeDefined();
    expect(page.querySelector('[data-history-row="299"] .history-action button')).toBeNull();
    expect(page.querySelector('[data-history-row="300"]').textContent).toContain("Skipped as quiet: 4 wake-ups");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("$0.07");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("Event: Failed check");
    expect(page.querySelector('[data-history-row="301"]').textContent).toContain("Pricing for add-ons");

    undo.click();
    await vi.waitFor(() => expect(api.supervisorUndo).toHaveBeenCalledWith(31, 911));

    page.querySelector('[aria-label="Load 100 older rows"]').click();
    await vi.waitFor(() => expect(page.querySelectorAll("[data-history-row]")).toHaveLength(103));
    expect(api.supervisorHistory).toHaveBeenLastCalledWith({
        planId: "", area: "", tier: "", result: "", before: "1234:202",
    });

    const plan = page.querySelector('[aria-label="Plan"]');
    const area = page.querySelector('[aria-label="Area"]');
    const tier = page.querySelector('[aria-label="Tier"]');
    const result = page.querySelector('[aria-label="Result"]');
    plan.value = "31";
    plan.dispatchEvent(new Event("change", {bubbles: true}));
    area.value = "checks";
    area.dispatchEvent(new Event("change", {bubbles: true}));
    tier.value = "1";
    tier.dispatchEvent(new Event("change", {bubbles: true}));
    result.value = "Acted";
    result.dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorHistory).toHaveBeenLastCalledWith({
        planId: "31", area: "checks", tier: "1", result: "Acted", before: "",
    }));
});

test("a never set up supervisor offers the owner a plan to start setup", async () => {
    api.supervisorHistory.mockResolvedValue(response("never_set_up", []));
    api.supervisorControl.mockResolvedValue({status: "never_set_up", grant: null});
    const page = await openPage();

    expect(page.textContent).toContain("The supervisor is not set up for this environment.");
    expect(page.querySelector("[data-supervisor-setup]").getAttribute("href")).toBe("#/plans");
    expect(page.querySelectorAll("[data-history-row]")).toHaveLength(0);
});

test("history remains readable while the supervisor is off", async () => {
    api.supervisorHistory.mockResolvedValue(response("off", [row(82, {actions: [action(2, {undo_available: false})]})]));
    const page = await openPage();

    expect(page.textContent).toContain("The supervisor is off. History stays readable.");
    expect(page.querySelector('[data-history-row="82"]')).not.toBeNull();
    expect(page.querySelector('[data-history-row="82"] .history-result').textContent).toBe("Acted");
});

test("the owner accepts a proposal and it disappears from the available actions", async () => {
    const firstAction = action(2, {status: "proposed", receipt_status: "proposed", undo_available: false});
    const secondAction = action(2, {
        title: "Set plan priorities", area: "Plans and tasks", status: "proposed", receipt_status: "proposed",
        undo_available: false,
    });
    const proposed = row(81, {result: "Proposed", actions: [firstAction, secondAction]});
    api.supervisorHistory.mockResolvedValueOnce(response("on", [proposed]))
        .mockResolvedValueOnce(response("on", [{...proposed, actions: proposed.actions.map((action) => ({...action, proposal_decision: "accepted"}))}]));
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="81"] button[data-proposal-decision="accept"]')).not.toBeNull());
    expect(page.querySelector('[data-history-row="81"] button[data-proposal-decision="decline"]')).not.toBeNull();
    expect(page.querySelectorAll('[data-history-row="81"] button[data-proposal-decision="accept"]')).toHaveLength(1);

    page.querySelector('[data-history-row="81"] button[data-proposal-decision="accept"]').click();
    await vi.waitFor(() => expect(api.supervisorProposal).toHaveBeenCalledWith(31, 911, "accept"));
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="81"] button[data-proposal-decision="accept"]')).toBeNull());
    expect(page.querySelector('[data-history-row="81"]').textContent).toContain("Accepted");
});

test("a refused proposal acceptance shows the route's reason", async () => {
    api.supervisorHistory.mockResolvedValue(response("on", [row(80, {
        result: "Proposed", actions: [action(2, {status: "proposed", receipt_status: "proposed", undo_available: false})],
    })]));
    api.supervisorProposal.mockRejectedValue(new Error("The proposal is no longer current."));
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="80"] button[data-proposal-decision="accept"]')).not.toBeNull());

    page.querySelector('[data-history-row="80"] button[data-proposal-decision="accept"]').click();
    await vi.waitFor(() => expect(page.querySelector('[role="alert"]').textContent).toContain("The proposal is no longer current."));
});

test("the owner saves feedback for a decision and turns its correction into a rule", async () => {
    api.supervisorHistory.mockResolvedValue(response("on", [row(79, {feedback: {useful: null, comment: "", correction: "", rule_id: null}})]));
    api.supervisorFeedback.mockResolvedValue({feedback: {useful: true, comment: "Good result.", correction: "Inspect before changing the interval.", rule_id: null}});
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="79"] [data-feedback-useful]')).not.toBeNull());
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="79"] .history-action button')).not.toBeNull());

    page.querySelector('[data-history-row="79"] [data-feedback-useful]').click();
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="79"] [data-feedback-save]').disabled).toBe(false));
    const comment = page.querySelector('[data-history-row="79"] textarea[aria-label="Comment"]');
    comment.value = "Good result.";
    comment.dispatchEvent(new Event("input", {bubbles: true}));
    const correction = page.querySelector('[data-history-row="79"] textarea[aria-label="Correction"]');
    correction.value = "Inspect before changing the interval.";
    correction.dispatchEvent(new Event("input", {bubbles: true}));
    page.querySelector('[data-history-row="79"] [data-feedback-save]').click();

    await vi.waitFor(() => expect(api.supervisorFeedback).toHaveBeenCalledWith(79, {
        useful: true, comment: "Good result.", correction: "Inspect before changing the interval.",
    }));
    await vi.waitFor(() => expect(page.querySelector('[data-history-row="79"] [data-feedback-rule]')).not.toBeNull());
    page.querySelector('[data-history-row="79"] [data-feedback-rule]').click();
    await vi.waitFor(() => expect(api.supervisorFeedbackRule).toHaveBeenCalledWith(79));
    await vi.waitFor(() => expect(page.textContent).toContain("Correction added as a rule."));
});

test("a non-owner can give feedback but does not get rule controls", async () => {
    api.supervisorHistory.mockResolvedValue(response("on", [row(78, {feedback: {useful: null, comment: "", correction: "", rule_id: null}})]));
    api.supervisorControl.mockRejectedValue(new Error("Only the owner can change the supervisor."));
    const page = await openPage();
    await vi.waitFor(() => expect(api.supervisorControl).toHaveBeenCalled());

    expect(page.querySelector('[data-history-row="78"] [data-feedback-useful]')).not.toBeNull();
    expect(page.querySelector('[data-history-row="78"] [data-feedback-not-useful]')).not.toBeNull();
    expect(page.querySelector('[data-history-row="78"] [data-feedback-rule]')).toBeNull();
});
