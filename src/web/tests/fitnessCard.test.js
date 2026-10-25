import {createApp, h, nextTick} from "vue";
import {expect, test} from "vitest";
import {threadTurns} from "../src/domain/thread.js";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const drop = {table: "messages", id: 5, created_at: new Date(1e4).toISOString(), creator: "system", author: "system", text: "Fitness fell 30 points to 70", files: [], comments_on: [], idempotency: "", data: {kind: "card", detail: "worker 3 reported after 40 seconds with no other task open, a job to do yourself", lines: [], row: "", shows: "fitness"}};

test("a drop in the fitness is one line naming the score and the points, its cause on a click", async () => {
    const {default: Turn} = await import("../src/chat/Turn.vue");
    const {turns} = threadTurns([drop], []);
    const host = document.createElement("div");
    document.body.append(host);
    const app = createApp({render: () => h(Turn, {turn: turns[0]})});
    app.provide("scope", {env: "", api: {}, rows: () => [], loaded: () => true, holding: () => {}, earlier: () => {}});
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".mark .head").textContent).toContain("Fitness fell 30 points to 70");
    expect(host.querySelector(".mark .detail")).toBeNull();
    host.querySelector(".mark").click();
    await nextTick();
    expect(host.querySelector(".mark .detail").textContent).toContain("a job to do yourself");
    app.unmount();
    host.remove();
});
