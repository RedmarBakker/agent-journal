import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

const peeked = vi.hoisted(() => []);
vi.mock("../src/route.js", async (original) => ({...(await original()), peek: (table, id) => peeked.push(`${table}/${id}`)}));
import {reportOf} from "../src/domain/report.js";
import {threadTurns} from "../src/domain/thread.js";

globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const at = (seconds) => new Date(seconds * 1000).toISOString();
const message = (id, text, data = {}) => ({table: "messages", id, created_at: at(id), author: "agent", text, files: [], data, comments_on: [], idempotency: "", reply_target: null});
const messages = [message(1, "Lady Montagu reports: the footer is fixed", {kind: "report", worker: "Lady Montagu", worker_id: 7}), message(2, "Montagu reports: not a report")];
const tasks = [{table: "tasks", id: 12, title: "Fix the footer", worker_id: 7}];
const scope = {env: "", api: {}, rows: (table) => (table === "tasks" ? tasks : messages), loaded: () => true, holding: () => {}, earlier: () => {}};

async function drawn(turn) {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: TurnMessage} = await import("../src/chat/TurnMessage.vue");
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(TurnMessage, {turn})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const card = host.querySelector(".growing-card");
    const bubble = host.querySelector(".thread-bubble");
    const shown = {report: host.querySelector(".thread-turn").classList.contains("report"), card: card ? card.textContent : "", bubbleShown: bubble.style.display !== "none"};
    if (card) {
        card.click();
        await nextTick();
        shown.expanded = host.querySelector(".growing-card-text")?.textContent || "";
    }
    app.unmount();
    host.remove();
    return shown;
}

test("a worker's report is told from the agent's own words by the worker it names", () => {
    const [report, own] = threadTurns(messages, []).turns;
    expect(reportOf(report)).toEqual({worker: "Lady Montagu", workerId: 7, text: "the footer is fixed"});
    expect(reportOf(own)).toBe(null);
});

test("a report in the chat is one card saying whose report on which task, and a click expands it to the report", async () => {
    const [report, own] = threadTurns(messages, []).turns;
    const shown = await drawn(report);
    expect(shown.report).toBe(true);
    expect(shown.card).toContain("Report from worker 7, Lady Montagu, on task 12");
    expect(shown.card).not.toContain("the footer is fixed");
    expect(shown.bubbleShown).toBe(false);
    expect(shown.expanded).toBe("the footer is fixed");
    expect((await drawn(own)).report).toBe(false);
});

test("a worker's report stays in the main chat while the worker's own turns stay in its chat", async () => {
    const {mainChat} = await import("../src/domain/thread.js");
    const report = {...message(5, "Lady Montagu reports: the header is fixed", {kind: "report", worker: "Lady Montagu", worker_id: 7}), agent_role: "main"};
    const turn = {...message(6, "Editing the header"), agent_role: "worker", session: "w7"};
    expect(mainChat([report, turn]).map((m) => m.id)).toEqual([5]);
    expect(reportOf(threadTurns(mainChat([report, turn]), []).turns[0])?.worker).toBe("Lady Montagu");
});
