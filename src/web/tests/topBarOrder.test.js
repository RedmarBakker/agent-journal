import {readFileSync} from "node:fs";
import {expect, test} from "vitest";

const source = readFileSync(new URL("../src/layout/StatusBar.vue", import.meta.url), "utf8");
const at = (needle) => source.indexOf(needle);

test("the fitness value sits beside the mode buttons and the Fold the plans button is the last before the full screen button", () => {
    expect(at('class="statusbar-mode"')).toBeLessThan(at("statusbar-fitness', {low"));
    expect(at("statusbar-fitness', {low")).toBeLessThan(at("statusbar-helpers', {none"));
    expect(at("statusbar-helpers', {none")).toBeLessThan(at("statusbar-strip', {on"));
    expect(at("statusbar-strip', {on")).toBeLessThan(at('data-step="fullscreen"'));
});
