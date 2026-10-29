import {createApp, effectScope, h} from "vue";
import {expect, test, vi} from "vitest";
import Approvals from "../src/organization/Approvals.vue";
import TurnQuestion from "../src/chat/TurnQuestion.vue";
import {useNavigation} from "../src/composables/navigation.js";
import {store} from "../src/state/store.js";
import {settle} from "./settle.js";

const requestDetails = `{
  "arguments": {
    "target": "production"
  },
  "command": "",
  "targets": [],
  "tool": "mcp__release__production_deployment"
}`;
const question = `Approve production deployment for Role Release Manager, task 58, requested by agent:release-manager?\n\nExact normalized request:\n${requestDetails}`;
const approval = {
    id: 4,
    table: "approvals",
    environment_id: 12,
    actor: "agent:release-manager",
    role: "Release Manager",
    plan_id: 24,
    task_id: 58,
    action: "production_deployment",
    question_id: 9,
    question_environment_id: 12,
    decision: "pending",
    expires_at: new Date(Date.now() + 3600000).toISOString(),
    creator: "agent:release-manager",
};
const questionRow = {id: 9, table: "questions", environment_id: 12, text: question, creator: "agent:release-manager"};

function button(host, label) {
    return [...host.querySelectorAll("button")].find((one) => one.textContent.includes(label));
}

async function mounted(component = Approvals, props = {approval, question}, scope = {api: {act: vi.fn()}, rows: () => []}) {
    const host = document.body.appendChild(document.createElement("div"));
    const app = createApp({render: () => h(component, props)});
    if (scope) app.provide("scope", scope);
    app.mount(host);
    await settle();
    return {host, app, scope};
}

test("the card preserves the exact persisted request and names its Role, plan and task", async () => {
    const {host, app} = await mounted();

    expect(host.querySelector(".approval-title").textContent).toBe(question);
    expect(host.querySelector(".approval-context").textContent.trim()).toBe("Role: Release Manager · Plan: 24 · Task: 58");
    expect(button(host, "Approve")).toBeTruthy();
    expect(button(host, "Refuse")).toBeTruthy();

    app.unmount();
    host.remove();
});

test("the plan driver's chat replaces the linked question with the shared approval card", async () => {
    const scope = {api: {act: vi.fn()}, rows: (table) => (table === "approvals" ? [approval] : [questionRow])};
    const {host, app} = await mounted(TurnQuestion, {turn: {question: {id: questionRow.id}, text: question}}, scope);

    expect(host.querySelector(".approval-title").textContent).toBe(question);
    expect(host.querySelector(".options")).toBeFalsy();
    button(host, "Approve").click();
    await vi.waitFor(() => expect(scope.api.act).toHaveBeenCalledWith("approvals", approval.id, "approve"));

    app.unmount();
    host.remove();
});

test("the Waiting for you rail shows the same approval card and can refuse it", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default:RailWaiting} = await import("../src/rail/RailWaiting.vue");
    const priorRows = store.rows;
    const priorBooted = store.booted;
    store.rows = {...store.rows, approvals: [approval], questions: [questionRow]};
    store.booted = false;
    const scope = {
        api: {act: vi.fn().mockResolvedValue({...approval, decision: "refused", updater: "user:1"})},
        rows: (table) => (table === "questions" ? [questionRow] : [approval]),
        holding: vi.fn().mockResolvedValue(),
    };
    const {host, app} = await mounted(RailWaiting, {}, scope);

    expect(host.querySelector(".approval-title").textContent).toBe(question);
    button(host, "Refuse").click();
    await vi.waitFor(() => expect(host.textContent).toContain("Refused by you"));
    expect(scope.api.act).toHaveBeenCalledWith("approvals", approval.id, "refuse");

    app.unmount();
    host.remove();
    store.rows = priorRows;
    store.booted = priorBooted;
});

test("the sidebar counts approvals that are still waiting", () => {
    const priorRows = store.rows;
    const priorBooted = store.booted;
    store.rows = {...store.rows, approvals: [approval]};
    store.booted = false;

    const navigationScope = effectScope();
    const link = navigationScope.run(() => useNavigation()).everywhere.value.find((item) => item.key === "approvals");
    expect(link).toMatchObject({count: 1, countTitle: "approvals waiting", hot: true});

    navigationScope.stop();
    store.rows = priorRows;
    store.booted = priorBooted;
});

test("a pending card and sidebar count expire as shared time advances without a row event", async () => {
    vi.useFakeTimers();
    const expiring = {...approval, expires_at: new Date(Date.now() + 500).toISOString()};
    const priorRows = store.rows;
    const priorBooted = store.booted;
    store.rows = {...store.rows, approvals: [expiring]};
    const approvalRows = store.rows.approvals;
    store.booted = false;
    const {host, app} = await mounted(Approvals, {approval: expiring, question}, {api: {act: vi.fn()}, rows: () => []});
    const navigationScope = effectScope();
    const navigation = navigationScope.run(() => useNavigation());
    const approvalsLink = () => navigation.everywhere.value.find((item) => item.key === "approvals");

    expect(button(host, "Approve")).toBeTruthy();
    expect(approvalsLink()).toMatchObject({count: 1, hot: true});
    await vi.advanceTimersByTimeAsync(1000);
    await settle();
    expect(host.textContent).toContain("Expired");
    expect(button(host, "Approve")).toBeFalsy();
    expect(button(host, "Refuse")).toBeFalsy();
    expect(approvalsLink()).toMatchObject({count: 0, hot: false});
    expect(store.rows.approvals).toBe(approvalRows);

    app.unmount();
    host.remove();
    navigationScope.stop();
    store.rows = priorRows;
    store.booted = priorBooted;
    vi.useRealTimers();
});

test("a double click sends one answer and names the actor returned by the server", async () => {
    let finish;
    const act = vi.fn(() => new Promise((resolve) => (finish = resolve)));
    const {host, app, scope} = await mounted(Approvals, {approval, question}, {api: {act}, rows: () => []});

    button(host, "Approve").click();
    button(host, "Approve").click();
    expect(scope.api.act).toHaveBeenCalledTimes(1);
    expect(scope.api.act).toHaveBeenCalledWith("approvals", approval.id, "approve");

    finish({...approval, decision: "approved", updater: "phone:1"});
    await vi.waitFor(() => expect(host.textContent).toContain("Approved by you, from your phone"));
    expect(button(host, "Approve")).toBeFalsy();
    expect(button(host, "Refuse")).toBeFalsy();

    app.unmount();
    host.remove();
});

test("a stale refusal shows the server's plain message", async () => {
    const act = vi.fn().mockRejectedValue(new Error("This approval is no longer waiting."));
    const {host, app} = await mounted(Approvals, {approval, question}, {api: {act}, rows: () => []});

    button(host, "Refuse").click();
    await vi.waitFor(() => expect(host.querySelector(".approval-error")?.textContent).toBe("This approval is no longer waiting."));
    expect(act).toHaveBeenCalledWith("approvals", approval.id, "refuse");

    app.unmount();
    host.remove();
});

test("a viewer approval answer goes through the journal API", async () => {
    const fetched = vi.fn(async () => new Response(JSON.stringify({...approval, decision: "approved", updater: "user:1"}), {status: 200, headers: {"Content-Type": "application/json"}}));
    vi.stubGlobal("fetch", fetched);
    (await import("../src/state/environment.js")).choose("main");
    const {host, app} = await mounted(Approvals, {approval, question}, null);

    button(host, "Approve").click();
    await vi.waitFor(() => expect(host.textContent).toContain("Approved by you"));
    expect(fetched.mock.calls[0][0]).toBe("/journal/approvals/4/approve");
    expect(fetched.mock.calls[0][1].headers["X-Journal-Viewer"]).toBe("1");

    app.unmount();
    host.remove();
    vi.unstubAllGlobals();
});
