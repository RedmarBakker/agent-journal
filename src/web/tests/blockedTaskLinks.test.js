import {createApp} from "vue";
import {afterEach, expect, test} from "vitest";
import {flush} from "./flush.js";
import {mentionedRefs} from "../src/domain/mentions.js";
import {store} from "../src/state/store.js";
import TaskState from "../src/tasks/TaskState.vue";
import Links from "../src/resource/Links.vue";

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    host?.remove();
    store.rows = {};
});

async function mounted(component, props) {
    host = document.createElement("div");
    document.body.append(host);
    app = createApp(component, props);
    app.directive("tip", {});
    app.mount(host);
    await flush();
    return host;
}

test("a reason names its rows by kind and number, each once and in order", () => {
    expect(mentionedRefs("waits for the go in message 85018, then task 12, then message 85018 again")).toEqual(["messages:85018", "tasks:12"]);
    expect(mentionedRefs("waits for the designs")).toEqual([]);
});

test("a task blocked for a reason that names a message offers to open that message", async () => {
    const task = {table: "tasks", id: 4504, title: "the reading", state: "blocked", block_reason: "waits for the go on the design in message 85018", waits: []};
    const into = await mounted(TaskState, {task, tasks: [task]});
    expect([...into.querySelectorAll(".open-named")].map((b) => b.textContent.trim())).toEqual(["Open message 85018"]);
    expect(into.querySelector(".row-pill")?.dataset.peek, "the message in the reason is a link too").toBe("messages:85018");
});

test("each row under Links to reads its kind and number before its title", async () => {
    store.rows = {plans: [{table: "plans", id: 3, title: "the teams plan", state: "ready"}]};
    const into = await mounted(Links, {resource: {table: "tasks", id: 9, title: "a task", links: ["plans:3"]}});
    const bar = into.querySelector(".bar");
    expect(bar.querySelector(".bar-kind").textContent.trim()).toBe("Plan 3");
    expect(bar.querySelector(".bar-title").textContent.trim()).toBe("the teams plan");
});
