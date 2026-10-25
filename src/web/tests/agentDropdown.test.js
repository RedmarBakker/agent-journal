import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import statusBar from "../src/layout/StatusBar.vue?raw";
import workerList from "../src/chat/WorkerList.vue?raw";
import * as route from "../src/route.js";
import AgentDropdown from "../src/chat/AgentDropdown.vue";
import {reviewerEntry, verifierEntry, workerEntry} from "../src/domain/agentEntries.js";

const ago = new Date(Date.now() - 5 * 60 * 1000).toISOString();
const worker = {table: "workers", id: 2, name: "Lady Lovelace", state: "clocked in", brief: "Write the parser", created_at: ago, updated_at: ago};
const verifier = {table: "verifiers", id: 4, state: "judged", judged: ["reader_reports:65", "reader_reports:66"], created_at: ago, updated_at: ago};
const reviewer = {table: "reviewers", id: 6, name: "Hypatia", state: "reviewing", brief: "Review the parser work", created_at: ago, updated_at: ago};

const mounted = (props) => {
    const root = document.createElement("div");
    const app = createApp({render: () => h(AgentDropdown, props)});
    app.directive("tip", {});
    app.mount(root);
    return root;
};

test("the one agent dropdown shows a worker, a verifier and a reviewer each with its name, state, when it was last active and what it worked on or judged", async () => {
    const shown = [
        [mounted({title: "Workers", table: "workers", entries: [workerEntry(worker)]}), ["Lady Lovelace", "Working", "Active 5m ago", "Write the parser"]],
        [mounted({title: "Verifiers", table: "verifiers", entries: [verifierEntry(verifier)]}), ["Verifier 4", "Idle", "Active 5m ago", "Judged 2 dismissals"]],
        [mounted({title: "Reviewers", entries: [reviewerEntry(reviewer)]}), ["Hypatia", "Reviewing", "Active 5m ago", "Review the parser work"]],
    ];
    await nextTick();
    for (const [root, words] of shown) for (const word of words) expect(root.textContent).toContain(word);
});

test("a click on a worker or verifier entry opens its inspector, and a reviewer entry, which has none, is not a button", async () => {
    const peek = vi.spyOn(route, "peek").mockImplementation(() => {});
    const verifiers = mounted({title: "Verifiers", table: "verifiers", entries: [verifierEntry(verifier)]});
    const reviewers = mounted({title: "Reviewers", entries: [reviewerEntry(reviewer)]});
    await nextTick();
    verifiers.querySelector("button.agent").click();
    expect(peek).toHaveBeenCalledWith("verifiers", 4);
    expect(reviewers.querySelector("button.agent")).toBe(null);
    peek.mockRestore();
});

test("the status bar opens the one dropdown for workers, verifiers and reviewers, and no separate list markup is left", () => {
    expect(statusBar).toContain('title="Verifiers"');
    expect(statusBar).toContain('title="Reviewers"');
    expect(workerList).toContain("<AgentDropdown");
    expect(statusBar).not.toContain("<VerifierList");
});
