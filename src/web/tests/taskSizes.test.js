import {createApp, h, nextTick} from "vue";
import {afterEach, expect, test} from "vitest";
import TaskSizePill from "../src/tasks/TaskSizePill.vue";
import TaskRow from "../src/tasks/TaskRow.vue";
import PlanRowLine from "../src/resource/PlanRowLine.vue";
import {pointLabel, sprintPointLabel, taskSizing} from "../src/domain/taskSizing.js";

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

test("a known task size is shown in points and an unknown size stays amber and explicit", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h("div", [
        h(TaskSizePill, {task: {id: 1, size: 5}}),
        h(TaskSizePill, {task: {id: 2, size: null}}),
    ])});
    app.mount(host);
    await nextTick();

    expect(host.textContent).toContain("5 points");
    const unknown = host.querySelector("[data-size-unknown]");
    expect(unknown.textContent).toBe("Size unknown");
    expect(unknown.className).toBe("task-size unknown");
});

test("the plan task row carries its size pill", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(PlanRowLine, {task: {id: 41, title: "Write the offer", size: 3}})});
    app.mount(host);
    await nextTick();

    expect(host.querySelector(".line").textContent).toContain("3 points");
});

test("the task board row carries its size pill", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h(TaskRow, {task: {id: 42, title: "Write the report", state: "open", size: 8}})});
    app.mount(host);
    await nextTick();

    expect(host.querySelector(".task-row .task-size").textContent).toBe("8 points");
});

test("unknown task rows in the plan and task views keep the amber size pill", async () => {
    host = document.body.appendChild(document.createElement("div"));
    app = createApp({render: () => h("div", [
        h(PlanRowLine, {task: {id: 43, title: "Prepare the release", state: "open", size: null}}),
        h(TaskRow, {task: {id: 44, title: "Check the deployment", state: "open", size: null}}),
    ])});
    app.mount(host);
    await nextTick();

    expect([...host.querySelectorAll("[data-size-unknown]")].map((pill) => [pill.textContent, pill.className])).toEqual([
        ["Size unknown", "task-size unknown"],
        ["Size unknown", "task-size unknown"],
    ]);
});

test("plan sizing totals known points and keeps unknown tasks out of the total", () => {
    const result = taskSizing([
        {id: 1, size: 5, state: "completed"},
        {id: 2, size: 8, state: "open"},
        {id: 3, size: null, state: "open"},
    ]);

    expect(result).toEqual({taskCount: 3, doneCount: 1, totalPoints: 13, donePoints: 5, sizedTasks: 2, unknownTasks: 1});
});

test("a zero or invalid task size is never presented as a known estimate", () => {
    const result = taskSizing([{id: 1, size: 0, state: "open"}, {id: 2, size: "5", state: "open"}]);

    expect(result).toEqual({taskCount: 2, doneCount: 0, totalPoints: null, donePoints: null, sizedTasks: 0, unknownTasks: 2});
    expect(pointLabel({tasks: [1], story_points: {total: 0, done: 0, sized_tasks: 1, unknown_tasks: 0}})).toBe("Size unknown");
    expect(sprintPointLabel([{tasks: [1], story_points: {total: 0, sized_tasks: 1, unknown_tasks: 0}}])).toBe("1 task size unknown");
});
