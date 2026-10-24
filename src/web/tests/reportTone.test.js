import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {expect, test} from "vitest";

const source = (path) => readFileSync(resolve(__dirname, "../src", path), "utf8");

test("a worker's report bubble and its state take the quiet blue, never the green kept for a finished task", () => {
    expect(source("chat/TurnMessage.vue")).not.toMatch(/\.thread-turn\.report[^}]*tone-good/s);
    expect(source("chat/WorkerRow.vue")).not.toMatch(/\.worker-(dot|state)\.reported\s*\{[^}]*tone-good/s);
    expect(source("chat/WorkerRow.vue")).toMatch(/\.worker-state\.reported\s*\{\s*color: var\(--tone-work\)/);
});

test("the skill mark is plain", () => {
    expect(source("chat/Turn.vue")).not.toMatch(/tone: "good"/);
});
