import {describe, expect, it} from "vitest";
import {revealOffset} from "../src/composables/revealPressed.js";

describe("a bubble that opens near the foot", () => {
    const pane = {top: 0, bottom: 600};

    it("scrolls the pane up until the bubble is seen whole above the docks and the composer", () => {
        expect(revealOffset({top: 400, bottom: 700}, pane)).toBe(108);
    });

    it("brings a bubble taller than the pane only as far as its top", () => {
        expect(revealOffset({top: 300, bottom: 1200}, pane)).toBe(292);
    });

    it("leaves a bubble already in view where it is", () => {
        expect(revealOffset({top: 100, bottom: 500}, pane)).toBe(0);
    });
});
