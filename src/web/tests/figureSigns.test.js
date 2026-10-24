// @vitest-environment node
import {describe, expect, it} from "vitest";
import {PICTURES} from "../src/figure/visorPixels.js";
import {SIGN, VISOR, glowTurn, lightOnce, signAt, visorAt, visorFor} from "../src/figure/visor.js";

// the visor `seconds` after a run ending `tone` lit it, `lit` being how visorFor drew it, lit as the run ended
function shownAt(lit, seconds) {
    const on = lightOnce(lightOnce(lit, true, lit.since), true, lit.since + VISOR.looks);
    return visorAt(on, on.at + seconds, false);
}

describe("a run's end shown in the eyes", () => {
    it("shows every run's end as its sign, the crosses for every failure and the ticks for every pass, never a lit visor", () => {
        for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
            for (let index = 0; index < 20; index++) {
                const shown = shownAt(visorFor([{tone}], null, index * 10), 1);
                expect(shown.sign.name).toBe(name);
                expect(shown.glow).toBe(0);
            }
        }
    });

    it("shows the sign in the eyes in the run's own colour, the visor dark, turned toward the viewer", () => {
        for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
            const shown = shownAt({tone, at: 0, sign: true}, 1.2);
            expect(shown.colour).toEqual(VISOR.colours[tone]);
            expect([shown.glow, shown.eyes]).toEqual([0, 1]);
            expect(shown.sign.name).toBe(name);
            expect(PICTURES[name], name).toBeTruthy();
            expect(glowTurn(shown)).toBe(1);
        }
    });

    it("flickers on and off like an old CRT warming up, then flashes white and bright, settles, and fades back to the usual eyes", () => {
        const steps = Array.from({length: 240}, (_, index) => signAt((index / 240) * SIGN.flicker[1]));
        const flickering = steps.map((step) => step.lit > SIGN.dim);
        const switches = flickering.slice(1).filter((on, index) => on !== flickering[index]).length;
        expect(switches, "on and off a few times").toBeGreaterThanOrEqual(2 * SIGN.flickers - 1);
        expect(steps.every((step) => step.white === 0 && step.strength === 1), "no flash before the flicker is done").toBe(true);
        expect(Math.max(...steps.map((step) => step.lit))).toBeLessThan(1);
        const flash = signAt(SIGN.flash[0]);
        expect([flash.lit, flash.white]).toEqual([1, 1]);
        const settled = signAt((SIGN.flash[1] + SIGN.fade[0]) / 2);
        expect([settled.lit, settled.white, settled.strength]).toEqual([1, 0, 1]);
        const fading = signAt((SIGN.fade[0] + SIGN.fade[1]) / 2);
        expect(fading.strength).toBeGreaterThan(0);
        expect(fading.strength).toBeLessThan(1);
        expect(signAt(SIGN.seconds)).toBe(null);
        expect(visorAt({tone: "bad", at: 0, sign: true}, 1, true), "never while it sleeps").toBe(null);
    });
});
