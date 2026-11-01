import {createApp, nextTick} from "vue";
import {expect, test} from "vitest";

window.matchMedia = window.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}}));
const {default: StatusBar} = await import("../src/layout/StatusBar.vue");
const {store} = await import("../src/state/store.js");
const {choose} = await import("../src/state/environment.js");

const standing = (task) => ({environments: [{environment: {id: 1, name: "main"}, agent: null, task, questions: 0, messages: 0, tasks: 1, silent: false}]});

test("the status line above the chat shows a chevron beside what it opens, and none when there is nothing to open", async () => {
    choose("main");
    store.agents = [{table: "agents", id: 1, session: "s1", status: "working", state: "working", heard_at: new Date().toISOString()}];
    store.summary = standing({id: 3, title: "Fix the cover", awaiting: ""});
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".statusbar-roll.link .statusbar-chevron")).not.toBe(null);
    store.summary = standing(null);
    await nextTick();
    expect(host.querySelector(".statusbar-chevron")).toBe(null);
    app.unmount();
    host.remove();
});

test("an agent waiting with no task in hand names what it waits for", async () => {
    choose("main");
    store.agents = [{table: "agents", id: 1, session: "s1", role: "main", status: "idle", state: "expecting", awaiting: "the full run for 4.1.0", wait_refs: "", awaiting_since: new Date().toISOString(), heard_at: new Date().toISOString()}];
    store.summary = standing(null);
    const host = window.document.createElement("div");
    window.document.body.append(host);
    const app = createApp(StatusBar);
    app.directive("tip", {});
    app.mount(host);
    await nextTick();
    expect(host.querySelector(".statusbar-text b").textContent).toBe("Waiting");
    expect(host.querySelector(".statusbar-text").textContent).toContain("the full run for 4.1.0");
    app.unmount();
    host.remove();
});

test("an idle agent in a state pushed over its floor, such as choosing whether to return to a plan, is named by that state's title", async () => {
    const {lineOf} = await import("../src/domain/agentState.js");
    const agent = {table: "agents", id: 1, session: "s1", role: "main", status: "idle", state: "choosing_plan_return", state_title: "Choosing the plan return", stack: [{state: "idle"}, {state: "choosing_plan_return"}], heard_at: new Date().toISOString()};
    expect(lineOf(agent, null, true)).toBe("choosing the plan return");
    expect(lineOf({...agent, state: "idle", state_title: "Idle", stack: [{state: "idle"}]}, null, true)).toBe("ready for the next task");
});
