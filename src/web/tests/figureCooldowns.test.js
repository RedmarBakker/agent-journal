import {afterEach, describe, expect, it, vi} from "vitest";
import {KeptTimes} from "../src/figure/keptTimes.js";
import {reactionTo, thinkingAct} from "../src/figure/reactions.js";

// the figure's memory as the page builds it at load for the environment `name`, `now` wall-clock seconds
const memoryAt = (now, name = "work") => new KeptTimes(`journal.figure.cooldowns.${name}`, now);

afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
});

describe("the figure's cooldowns", () => {
    it("hold through a reload: an act played, the memory rebuilt as a reload does, and the act still cools down until its time", () => {
        const now = 1_800_000_000;
        const before = memoryAt(now);
        expect(reactionTo("messaged", before, now, () => 0).clip, "the telephone call plays").toBe("phone_call");
        const reloaded = memoryAt(now + 10);
        expect(reloaded.get("messaged"), "read back from the browser's storage").toBe(now);
        expect(reactionTo("messaged", reloaded, now + 10, () => 0), "still cooling down after the reload").toBe(null);
        expect(reactionTo("messaged", memoryAt(now + 91), now + 91, () => 0).clip, "and plays again once its cooldown is over").toBe("phone_call");
    });

    it("keep the thinking act's random cooldown and its parts' through a reload, as wall-clock seconds", () => {
        const now = 1_800_000_000;
        const before = memoryAt(now);
        expect(thinkingAct(before, now, () => 0)).toBe("ponder");
        const reloaded = memoryAt(now + 5);
        for (const key of ["pondering", "thought_cloud", "light_bulb"]) expect(reloaded.get(key), key).toBe(before.get(key));
        expect(thinkingAct(reloaded, now + 5, () => 0), "not again straight after the reload").toBe(null);
    });

    it("are kept for each environment apart, and a time older than a day is let go", () => {
        const now = 1_800_000_000;
        reactionTo("messaged", memoryAt(now, "work"), now, () => 0);
        expect(memoryAt(now + 1, "home").get("messaged"), "another environment's figure is free to play it").toBeUndefined();
        expect(memoryAt(now + 25 * 60 * 60, "work").get("messaged"), "a day on it is forgotten").toBeUndefined();
    });

    it("lose only themselves when the storage throws: the figure works on, keeping its times for the page's life", () => {
        const refusing = {getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); }};
        vi.stubGlobal("localStorage", refusing);
        const now = 1_800_000_000;
        const memory = memoryAt(now);
        expect(memory.size).toBe(0);
        expect(reactionTo("messaged", memory, now, () => 0).clip, "an act still plays").toBe("phone_call");
        expect(reactionTo("messaged", memory, now + 10, () => 0), "and still cools down while the page lives").toBe(null);
        expect(thinkingAct(memory, now, () => 0)).toBe("ponder");
    });
});
