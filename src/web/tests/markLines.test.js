import {createApp, h, nextTick} from "vue";
import {expect, test, vi} from "vitest";

vi.mock("../src/route.js", async (original) => ({...(await original()), peek: vi.fn()}));
import {threadTurns} from "../src/domain/thread.js";

const lines = Array.from({length: 13}, (_, i) => `finding ${i + 1}`);
const message = {table: "messages", id: 1, created_at: new Date(1e4).toISOString(), creator: "plugin:lint", author: "system", text: "Lint found 13 problems", files: [], comments_on: [], idempotency: "", data: {kind: "plugin", plugin: "lint", detail: lines[0], lines, collapsed: true, row: ""}};
const scope = {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}};

test("a card with thirteen lines opens thirteen rows under it on a click and closes on a second", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const {turns} = threadTurns([message], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelectorAll(".mark-line").length).toBe(0);
    host.querySelector(".mark").click();
    await nextTick();
    expect(host.querySelectorAll(".mark-line").length).toBe(13);
    expect(host.querySelector(".mark .detail")).toBeNull();
    host.querySelector(".mark").click();
    await nextTick();
    expect(host.querySelectorAll(".mark-line").length).toBe(0);
    app.unmount();
    host.remove();
});

test("a process card opens in one click to its summary and a terminal view fetched then, with a height of its own, and folds on a second", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const run = {...message, data: {kind: "card", output: 12, line: "pytest -q", summary: "3 failed, 1146 passed", detail: "FAILED test_b", lines: [], ending: "Failed", row: ""}};
    const {turns} = threadTurns([run], []);
    const readOutput = vi.fn().mockResolvedValue({lines: ["collecting", "FAILED test_b"], start: 0, next: 2});
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", {...scope, api: {readOutput}});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(readOutput).not.toHaveBeenCalled();
    expect(host.querySelector(".mark-terminal")).toBeNull();
    host.querySelector(".mark").click();
    await new Promise((done) => setTimeout(done, 0));
    await nextTick();
    expect(readOutput).toHaveBeenCalledWith(12);
    expect(host.querySelector(".mark-summary").textContent).toBe("3 failed, 1146 passed");
    expect(host.querySelector(".mark-terminal").textContent).toBe("collecting\nFAILED test_b");
    expect(host.querySelector(".mark-more").classList.contains("open")).toBe(true);
    expect(host.querySelector(".mark").hasAttribute("data-open")).toBe(true);
    host.querySelector(".mark").click();
    await nextTick();
    expect(host.querySelector(".mark-more").classList.contains("open")).toBe(false);
    app.unmount();
    host.remove();
});

test("a card of a task created from a message opens the task on a click, not the message", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const {peek} = await import("../src/route.js");
    const created = {...message, data: {kind: "card", detail: "", lines: [], row: "tasks:12", shows: "filed"}, text: "Created task 12 from your message"};
    const {turns} = threadTurns([created], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".mark .head").textContent).toContain("Created task 12 from your message");
    host.querySelector(".mark").click();
    await nextTick();
    expect(peek).toHaveBeenCalledWith("tasks", 12, 0);
    app.unmount();
    host.remove();
});

test("a push is one live mark titled for the branch and the remote, and opens to the range of commits it sent", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const push = {...message, text: "Pushing development to origin", data: {kind: "card", output: 3, line: "git push origin development", detail: "abc1234..def5678  development -> development", lines: [], ending: "pushed", row: ""}};
    const {turns} = threadTurns([push], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", {...scope, api: {readOutput: vi.fn().mockResolvedValue({lines: ["To github.com:me/project.git", "   abc1234..def5678  development -> development"], start: 0, next: 2})}});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".mark .head").textContent).toContain("Pushing development to origin");
    host.querySelector(".mark").click();
    await new Promise((done) => setTimeout(done, 0));
    await nextTick();
    expect(host.querySelector(".mark-terminal").textContent).toContain("abc1234..def5678");
    app.unmount();
    host.remove();
});

test("a card keeps the same mark element while it opens and closes, and its title never wraps", async () => {
    window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const {turns} = threadTurns([message], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", scope);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    const mark = host.querySelector(".mark");
    mark.click();
    await nextTick();
    expect(host.querySelector(".mark")).toBe(mark);
    mark.click();
    await nextTick();
    expect(host.querySelector(".mark")).toBe(mark);
    const {readFileSync} = await import("node:fs");
    const css = readFileSync(new URL("../src/kit/ChatMark.vue", import.meta.url), "utf8");
    expect(css).toMatch(/\.head \{[^}]*white-space: nowrap/);
    app.unmount();
    host.remove();
});
