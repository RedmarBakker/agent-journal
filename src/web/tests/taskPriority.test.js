import {expect, test} from "vitest";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {priorityLabel} from "../src/domain/taskPriority.js";

test("a task's priority reads by its level's name, or by its number between the levels", () => {
    expect([priorityLabel(50), priorityLabel(100), priorityLabel(150), priorityLabel(200), priorityLabel(120)]).toEqual(["Low", "Normal", "High", "Critical", "120"]);
});

test("a task row shows a priority that is not normal, and the inspector sets it", () => {
    const row = readFileSync(resolve(__dirname, "../src/tasks/TaskRow.vue"), "utf8");
    expect(row).toMatch(/<template v-if="\(task\.priority \?\? NORMAL_PRIORITY\) !== NORMAL_PRIORITY">/);
    const inspector = readFileSync(resolve(__dirname, "../src/tasks/TaskInspector.vue"), "utf8");
    expect(inspector).toMatch(/<Segmented :options="PRIORITY_LEVELS" :value="task\.priority \?\? NORMAL_PRIORITY" @pick="setPriority" \/>/);
    expect(inspector).toMatch(/scope\.api\.change\("tasks", props\.task\.id, \{priority\}\)/);
});
