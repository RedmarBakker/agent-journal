import {expect, test, vi} from "vitest";

const reloads = [];
vi.mock("../src/platform/timing.js", async (original) => ({...(await original()), wait: async () => {}}));
vi.mock("../src/platform/busyField.js", () => ({reloadWhenFree: (w) => reloads.push(w)}));
import {api} from "../src/api/client.js";
import {runUpdate} from "../src/composables/updates.js";
import {clear, followServer, updating} from "../src/state/updating.js";

const stepTo98 = {installed: "4.97.0", updating: "4.99.0", step_count: 2, step_version: "4.98.0", final_version: "4.99.0"};
const stepTo99 = {installed: "4.98.0", updating: "4.99.0", step_count: 2, step_version: "4.99.0", final_version: "4.99.0"};

test("the cover follows a path of two steps to its final version, its time to give up starting again at each step", async () => {
    clear();
    let polls = 0;
    vi.spyOn(api, "update").mockResolvedValue({});
    vi.spyOn(api, "releases").mockImplementation(async () => {
        polls += 1;
        return polls <= 449 ? stepTo98 : polls <= 898 ? stepTo99 : {installed: "4.99.0"};
    });
    const reload = vi.fn();
    Object.defineProperty(window, "location", {value: {...window.location, hash: "", reload}, configurable: true});
    await runUpdate("4.99.0");
    expect(reload).toHaveBeenCalled();
    expect([updating.late, updating.failure]).toEqual([false, ""]);
});

test("a server restarted on a step of the path this page updates along reloads nothing, and the final version reloads it", () => {
    clear();
    followServer({version: "4.97.0", started: 1, updating: ""});
    updating.version = "4.99.0";
    followServer({version: "4.98.0", started: 2, updating: ""});
    expect(reloads.length).toBe(0);
    followServer({version: "4.99.0", started: 3, updating: ""});
    expect(reloads.length).toBe(1);
});
