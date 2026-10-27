import {createApp, h, ref} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

globalThis.ResizeObserver ??= class {
    observe() {}

    unobserve() {}

    disconnect() {}
};

const {store} = await import("../src/state/store.js");
const {moreActs, nextAct} = await import("../src/domain/taskBoard.js");
const {default: TaskMenus} = await import("../src/tasks/TaskMenus.vue");

const task = (id, more = {}) => ({table: "tasks", id, title: `task ${id}`, brief: "", state: "open", plan_id: null, waits: [], block_reason: "", ...more});
const withWorker = task(4, {state: "started", delegated: true});
const queued = task(2, {delegated: true});
let app = null;

afterEach(() => {
    app?.unmount();
    app = null;
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("the More menu of a task with a worker or queued for one, which has no next act, opens with no error and offers its acts", async () => {
    store.rows = {tasks: [withWorker, queued], plans: [], questions: []};
    expect([nextAct(withWorker), nextAct(queued)]).toEqual([null, null]);
    expect(moreActs(withWorker).map((a) => a.label)).toEqual(["Blocked by a task...", "Edit the title and brief"]);
    const errors = [];
    const logged = vi.spyOn(console, "error").mockImplementation((...args) => errors.push(args.join(" ")));
    const anchor = document.body.appendChild(document.createElement("button"));
    const shown = vi.fn();
    const host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(TaskMenus, {menu: {kind: "more", task: withWorker, el: anchor}, tasks: [withWorker, queued], acts: {asking: ref(null)}, onShow: shown})});
    app.config.errorHandler = (error) => errors.push(String(error));
    app.mount(host);
    await flush();
    const items = [...document.querySelectorAll(".menu-panel button")].map((b) => b.textContent.trim());
    expect(errors).toEqual([]);
    expect(items).toEqual(["Change status", "Blocked by a task...", "Edit the title and brief", "Delete task 4"]);
    [...document.querySelectorAll(".menu-panel button")][0].click();
    expect(shown).toHaveBeenCalledWith("status", withWorker, anchor);
    logged.mockRestore();
});
