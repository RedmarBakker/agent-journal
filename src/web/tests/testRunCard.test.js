import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import {threadTurns} from "../src/domain/thread.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const run = {table: "messages", id: 6, created_at: new Date(1e4).toISOString(), creator: "system", author: "system", text: "Worker 3, Mrs. Harrison: its tests passed", files: [], comments_on: [], idempotency: "", data: {kind: "card", card_type: "process", process: "test_run", line: "python3 scripts/suite.py tests/test_cli.py", summary: "2 passed", proof_task: 7, lines: [], row: "", shows: "commands", active: false}};

test("a worker's test run card opens to its run and offers the task with its proofs", async () => {
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const {turns} = threadTurns([run], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".mark .head").textContent).toContain("its tests passed");
    host.querySelector(".mark").click();
    await nextTick();
    expect(host.querySelector(".mark-command").textContent).toBe("python3 scripts/suite.py tests/test_cli.py");
    expect(host.querySelector(".mark-proofs").textContent).toBe("Open task 7 and its proofs");
    app.unmount();
    host.remove();
});
