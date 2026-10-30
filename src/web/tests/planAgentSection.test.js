import {createApp, h, nextTick} from "vue";
import {afterEach, beforeEach, expect, test, vi} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";

const api = {launchAgent: vi.fn(), stopAgentIn: vi.fn(), page: (name) => `/?env=${name}#/chat`};
vi.mock("../src/api/client.js", async (importOriginal) => ({...(await importOriginal()), api}));
vi.mock("../src/kit/MenuPanel.vue", () => ({default: {props: ["anchor"], template: "<div class='menu-panel'><slot /></div>"}}));

const {default: PlanAgentSection} = await import("../src/resource/PlanAgentSection.vue");
const {store} = await import("../src/state/store.js");

const plan = {id: 3, title: "Floors", state: "started", chat: "plan-3", plan_agent_last_action_at: "2026-01-01T10:00:00Z"};
let app = null;
let host = null;

beforeEach(() => {
    api.launchAgent.mockReset().mockResolvedValue({});
    api.stopAgentIn.mockReset().mockResolvedValue({});
    store.summary = {environments: [{environment: {id: 44, key: "plan-key", name: "plan-3", branch: "plan/floors", generated_for: "plan"}, agent: null, task: null}]};
    store.rows.environments = [];
});

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

async function mount(resource = plan) {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanAgentSection, {plan: resource})});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
}

async function until(done) {
    for (let n = 0; n < 100 && !done(); n++) await new Promise((settle) => setTimeout(settle, 10));
    await nextTick();
}

test("a stopped Plan agent shows its environment, branch, last action time, chat link, and can be started", async () => {
    await mount();

    expect(host.textContent).toContain("Stopped");
    expect(host.textContent).toContain("Environment: plan-3");
    expect(host.textContent).toContain("Branch: plan/floors");
    expect(host.textContent).toContain("Last action: No action reported");
    expect(host.textContent).toContain("ago");
    expect(host.querySelector(".plan-agent-chat").getAttribute("href")).toContain("env=plan-3");
    expect(host.querySelector(".plan-agent-chat").getAttribute("href")).toContain("#/chat");

    host.querySelector(".agent-start button").click();
    await nextTick();
    [...host.querySelectorAll("button")].find((button) => button.textContent.trim() === "Codex").click();
    await until(() => api.launchAgent.mock.calls.length === 1);
    expect(api.launchAgent).toHaveBeenCalledWith(44, "codex");
});

test("a running Plan agent needs stop confirmation and shows the plain refusal", async () => {
    store.summary.environments[0].agent = {status: "busy", branch: "plan/floors", doing: "merging the branch", heard_at: "2026-10-29T10:05:00Z"};
    api.stopAgentIn.mockRejectedValue(new Error("Cannot stop while a merge is in progress; finish the merge first."));
    await mount();

    expect(host.textContent).toContain("Running");
    expect(host.textContent).toContain("Last action: merging the branch");
    host.querySelector(".agent-stop-button").click();
    await nextTick();
    expect(api.stopAgentIn).not.toHaveBeenCalled();
    const stop = [...host.querySelectorAll(".stop-row button")].at(-1);
    stop.click();
    await until(() => host.querySelector(".stop-error"));
    expect(api.stopAgentIn).toHaveBeenCalledWith(44);
    expect(host.querySelector('[role="alert"]').textContent).toBe("Cannot stop while a merge is in progress; finish the merge first.");
});

test("the plan page and agent bar only add Plan agent UI while the Plan agents switch is on", () => {
    const page = readFileSync(resolve(__dirname, "../src/resource/PlanPage.vue"), "utf8");
    const bar = readFileSync(resolve(__dirname, "../src/chat/AgentBar.vue"), "utf8");
    expect(page).toMatch(/<PlanAgentSection v-if="planAgents"/);
    expect(bar).toMatch(/<PlanAgentChats v-if="planAgents"/);
});
