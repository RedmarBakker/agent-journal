import {createApp, h} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const api = {supervisorControl: vi.fn(), supervisorChange: vi.fn(), supervisorProposal: vi.fn(), supervisorRemoveRule: vi.fn(), list: vi.fn(), change: vi.fn()};
vi.mock("../src/api/client.js", async (importOriginal) => ({...(await importOriginal()), api}));

const {default: SupervisorControlPage} = await import("../src/pages/SupervisorControlPage.vue");

let app = null;
let host = null;

const areas = [
    {key: "plans-and-tasks", title: "Plans and tasks", enabled: true, verbs: [{capability: "task create", title: "Create a task", tier: 1, enabled: true, mode: "act"}]},
    {key: "dependencies-and-blocks", title: "Dependencies and blocks", enabled: false, verbs: [{capability: "task block", title: "Block a task", tier: 2, enabled: false, mode: "act"}]},
    {key: "checks", title: "Checks", enabled: false, verbs: [{capability: "check create", title: "Create a check", tier: 1, enabled: false, mode: "act"}]},
    {key: "sequences", title: "Sequences", enabled: false, verbs: [{capability: "sequence create", title: "Create a sequence", tier: 1, enabled: false, mode: "act"}]},
    {key: "rules-and-reminders", title: "Rules and reminders", enabled: false, verbs: [{capability: "rule create", title: "Create a rule", tier: 3, enabled: false, mode: "propose"}]},
    {key: "triggers", title: "Triggers", enabled: false, verbs: [{capability: "trigger create", title: "Create a trigger", tier: 2, enabled: false, mode: "act"}]},
    {key: "workers-and-reviewers", title: "Workers and reviewers", enabled: false, verbs: [{capability: "worker notify", title: "Notify a worker", tier: 2, enabled: false, mode: "act"}]},
    {key: "messages-and-organization", title: "Messages and organization", enabled: false, verbs: [{capability: "message tag", title: "Tag a message", tier: 1, enabled: false, mode: "act"}]},
    {key: "documents-reports-and-collections", title: "Documents, reports and collections", enabled: false, verbs: [{capability: "doc create", title: "Create a document", tier: 1, enabled: false, mode: "act"}]},
    {key: "settings-and-modes", title: "Settings and modes", enabled: false, verbs: [{capability: "mode", title: "Change a work mode", tier: 2, enabled: false, mode: "act"}]},
    {key: "plugins-mcp-and-updates", title: "Plugins, MCP and updates", enabled: false, verbs: []},
    {key: "secrets", title: "Secrets", enabled: false, verbs: []},
    {key: "git-and-sharing", title: "Git and sharing", enabled: false, verbs: []},
];

const settings = () => ({
    grant_id: "grant-7",
    grant_version: 3,
    status: "on",
    grant: {
        owner_user_id: 1,
        environment_id: 4,
        watched_plans: "all",
        capabilities: {"area:plans-and-tasks": {on: true, mode: "propose"}, "task create": {on: true, mode: "act"}},
        wake_interval_minutes: 15,
        event_wakeups: ["failed_check"],
        limits: {
            max_turns_per_day: 96,
            max_input_tokens_per_turn: 40000,
            max_output_tokens_per_turn: 4000,
            max_provider_requests_per_turn: 6,
            max_turn_seconds: 300,
            max_cost_microusd_per_day: 5000000,
            max_bundles_per_project_day: 40,
            max_bundles_per_episode_day: 3,
            max_new_diagnostics_per_episode: 1,
        },
        valid_until_ms: 1795867200000,
        paused: false,
        revoked: false,
    },
    areas,
    needs_decision: [{capability: "plan approve", title: "Approve a plan", area: "Plans and tasks", tier: 3}],
    replacement_enrollment: {protocol_version: 1},
    restore_review: null,
    proposals: [{
        receipt_id: 911,
        plan_id: 7,
        plan_title: "Release plan",
        created_at: "2026-11-02T12:00:00Z",
        rationale: "The check has failed repeatedly.",
        actions: [{title: "Edit check", area: "Checks", tier: 2}],
    }, {
        receipt_id: 912,
        plan_id: 7,
        plan_title: "Release plan",
        created_at: "2026-11-02T11:00:00Z",
        rationale: "The plan could use a higher priority.",
        actions: [{title: "Set plan priorities", area: "Plans and tasks", tier: 2}],
    }],
});

beforeEach(() => {
    api.supervisorControl.mockReset().mockResolvedValue(settings());
    api.supervisorChange.mockReset().mockResolvedValue({grant_version: 4});
    api.supervisorProposal.mockReset().mockResolvedValue({decision: "accepted"});
    api.supervisorRemoveRule.mockReset().mockResolvedValue({});
    api.list.mockReset().mockImplementation((table) => Promise.resolve({rows: table === "plans"
        ? [{id: 7, title: "Release plan"}]
        : [{id: 21, title: "Held task", plan_id: 7, supervisor_reserved: true}]}));
    api.change.mockReset().mockResolvedValue({});
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
    app = createApp({render: () => h(SupervisorControlPage)});
    app.directive("tip", {});
    app.mount(host);
    await vi.waitFor(() => expect(api.supervisorControl).toHaveBeenCalled());
    await vi.waitFor(() => expect(host.querySelector("[data-supervisor-controls], [data-control-denied]")).not.toBeNull());
    return host;
}

test("the owner sees grant settings for all 13 areas and saves every control through the grant route", async () => {
    const page = await openPage();
    await vi.waitFor(() => expect(page.querySelector('[aria-label="Wake up every"]').value).toBe("15"));

    expect(page.querySelectorAll("[data-capability-area]")).toHaveLength(13);
    expect(page.textContent).toContain("Wake up on");
    expect(page.textContent).toContain("Watched plans");
    expect(page.textContent).toContain("Limits");
    expect(page.textContent).toContain("Proposes");
    expect(page.textContent).toContain("Acts");
    expect(page.querySelector('[aria-label="On: Create a task"]')).not.toBeNull();
    expect(page.querySelector('[data-area="plans-and-tasks"] .control-tier').textContent).toBe("Tier 1");
    expect(page.textContent).toContain("Needs your decision");
    expect(page.textContent).toContain("Changing its own grant");
    expect(page.textContent).toContain("Never allowed");
    expect(page.textContent).toContain("Release held task");
    expect(page.textContent).toContain("Replace grant");
    expect(page.textContent).toContain("Revoke grant");

    const interval = page.querySelector('[aria-label="Wake up every"]');
    interval.value = "30";
    interval.dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalled());
    expect(api.supervisorChange).toHaveBeenCalledWith({
        protocol_version: 1,
        grant_id: "grant-7",
        expected_grant_version: 3,
        change: {kind: "configure", grant: {...settings().grant, wake_interval_minutes: 30}},
    });
});

test("the owner saves wake events, plan scope, limits, area switches and verb modes as grant revisions", async () => {
    const page = await openPage();

    const event = [...page.querySelectorAll("label")].find((label) => label.textContent.includes("Stalled task"));
    event.querySelector("input").checked = true;
    event.querySelector("input").dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(1));
    expect(api.supervisorChange.mock.calls[0][0].change.grant.event_wakeups).toContain("stalled_task");

    page.querySelector('[aria-label="Turns per day"]').value = "120";
    page.querySelector('[aria-label="Turns per day"]').dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(2));
    expect(api.supervisorChange.mock.calls[1][0].change.grant.limits.max_turns_per_day).toBe(120);

    page.querySelector('[aria-label="Enable Plans and tasks"]').checked = false;
    page.querySelector('[aria-label="Enable Plans and tasks"]').dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(3));
    expect(api.supervisorChange.mock.calls[2][0].change.grant.capabilities["area:plans-and-tasks"])
        .toEqual({on: false, mode: "act"});

    page.querySelector('[aria-label="Create a task mode"]').value = "propose";
    page.querySelector('[aria-label="Create a task mode"]').dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(4));
    expect(api.supervisorChange.mock.calls[3][0].change.grant.capabilities["task create"].mode).toBe("propose");

    [...page.querySelectorAll("button")].find((button) => button.textContent === "Chosen plans").click();
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(5));
    expect(api.supervisorChange.mock.calls[4][0].change.grant.watched_plans).toEqual([]);

    const plan = [...page.querySelectorAll("label")].find((label) => label.textContent.includes("Plan 7: Release plan"));
    plan.querySelector("input").checked = true;
    plan.querySelector("input").dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(6));
    expect(api.supervisorChange.mock.calls[5][0].change.grant.watched_plans).toEqual([7]);

    page.querySelector('[aria-label="Decision: Approve a plan"]').value = "act";
    page.querySelector('[aria-label="Decision: Approve a plan"]').dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(7));
    expect(api.supervisorChange.mock.calls[6][0].change.grant.capabilities["plan approve"])
        .toEqual({on: true, mode: "act"});

    const createTaskOn = page.querySelector('[aria-label="On: Create a task"]');
    createTaskOn.checked = false;
    createTaskOn.dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(api.supervisorChange).toHaveBeenCalledTimes(8));
    expect(api.supervisorChange.mock.calls[7][0].change.grant.capabilities["task create"].on).toBe(false);
});

test("Control shows waiting proposals and removes an accepted proposal", async () => {
    api.supervisorControl.mockReset()
        .mockResolvedValueOnce(settings())
        .mockResolvedValueOnce({...settings(), proposals: [settings().proposals[1]]})
        .mockResolvedValueOnce({...settings(), proposals: []});
    const page = await openPage();

    expect(page.textContent).toContain("Waiting for you");
    expect(page.textContent).toContain("The check has failed repeatedly.");
    expect(page.querySelector('[data-proposal="911"] button[data-proposal-decision="accept"]')).not.toBeNull();
    page.querySelector('[data-proposal="911"] button[data-proposal-decision="accept"]').click();

    await vi.waitFor(() => expect(api.supervisorProposal).toHaveBeenCalledWith(7, 911, "accept"));
    await vi.waitFor(() => expect(page.querySelector('[data-proposal="911"]')).toBeNull());

    page.querySelector('[data-proposal="912"] button[data-proposal-decision="decline"]').click();
    await vi.waitFor(() => expect(api.supervisorProposal).toHaveBeenCalledWith(7, 912, "decline"));
    await vi.waitFor(() => expect(page.querySelector('[data-proposal="912"]')).toBeNull());
});

test("the owner can turn the supervisor off, release a held task, replace the grant and revoke it", async () => {
    const page = await openPage();
    await vi.waitFor(() => expect(page.textContent).toContain("Held task"));

    page.querySelector(".control-heading button").click();
    await vi.waitFor(() => expect(api.supervisorChange.mock.calls[0][0].change.kind).toBe("off"));
    await vi.waitFor(() => expect(page.querySelector(".control-heading button").disabled).toBe(false));

    [...page.querySelectorAll("button")].find((button) => button.textContent === "Release held task").click();
    await vi.waitFor(() => expect(api.change).toHaveBeenCalledWith("tasks", 21, {supervisor_reserved: false}));
    await vi.waitFor(() => expect(page.querySelector(".control-heading button").disabled).toBe(false));

    [...page.querySelectorAll("button")].find((button) => button.textContent === "Replace grant").click();
    await vi.waitFor(() => expect(api.supervisorChange.mock.calls.some(([body]) => body.change.kind === "replace")).toBe(true));
    expect(api.supervisorChange.mock.calls.find(([body]) => body.change.kind === "replace")[0].change.enrollment)
        .toEqual(settings().replacement_enrollment);

    [...page.querySelectorAll("button")].find((button) => button.textContent === "Revoke grant").click();
    await vi.waitFor(() => expect(api.supervisorChange.mock.calls.some(([body]) => body.change.kind === "revoke")).toBe(true));
});

test("a restored installation must be reviewed before the owner replaces its grant", async () => {
    api.supervisorControl.mockResolvedValue({...settings(), restore_review: {
        epoch: 2, evidence_watermark_ms: null, evidence_rpo_gap_ms: null, accept_unavailable_evidence: true,
    }});
    const page = await openPage();

    [...page.querySelectorAll("button")].find((button) => button.textContent === "Replace grant").click();
    expect(page.querySelector('[role="alert"]').textContent).toContain("Review the restored installation");
    expect(api.supervisorChange).not.toHaveBeenCalled();

    const review = [...page.querySelectorAll("label")].find((label) => label.textContent.includes("I accept that restoration evidence is unavailable."));
    review.querySelector("input").checked = true;
    review.querySelector("input").dispatchEvent(new Event("change", {bubbles: true}));
    [...page.querySelectorAll("button")].find((button) => button.textContent === "Replace grant").click();
    await vi.waitFor(() => expect(api.supervisorChange.mock.calls.some(([body]) => body.change.kind === "replace")).toBe(true));
    expect(api.supervisorChange.mock.calls[0][0].change.restore_review.accept_unavailable_evidence).toBe(true);
});

test("a non-owner cannot see grant controls", async () => {
    api.supervisorControl.mockRejectedValue(new Error("Only the owner can change the supervisor."));
    const page = await openPage();
    await vi.waitFor(() => expect(page.textContent).toContain("Only the owner can change the supervisor."));

    expect(page.querySelector("[data-control-denied]")).not.toBeNull();
    expect(page.querySelector("[data-supervisor-controls]")).toBeNull();
});

test("a stale grant revision displays the grant route's conflict text", async () => {
    api.supervisorChange.mockRejectedValue(new Error("The settings changed since you opened them; reload."));
    const page = await openPage();
    const interval = page.querySelector('[aria-label="Wake up every"]');
    interval.value = "30";
    interval.dispatchEvent(new Event("change", {bubbles: true}));
    await vi.waitFor(() => expect(page.querySelector('[role="alert"]').textContent).toContain("The settings changed since you opened them; reload."));
});

test("Control lists narrowing rules and removes them through the owner route", async () => {
    const rule = {id: 47, text: "For Plan 7 in Checks: inspect before changing the interval.", reason: "A supervisor correction."};
    api.supervisorControl.mockReset()
        .mockResolvedValueOnce({...settings(), rules: [rule]})
        .mockResolvedValueOnce({...settings(), rules: []});
    const page = await openPage();
    await vi.waitFor(() => expect(page.textContent).toContain(rule.text));
    expect(page.querySelector('[data-supervisor-rule="47"] [data-rule-remove]').textContent).toBe("Remove the rule");

    page.querySelector('[data-supervisor-rule="47"] [data-rule-remove]').click();
    await vi.waitFor(() => expect(api.supervisorRemoveRule).toHaveBeenCalledWith(47));
    await vi.waitFor(() => expect(page.querySelector('[data-supervisor-rule="47"]')).toBeNull());
});
