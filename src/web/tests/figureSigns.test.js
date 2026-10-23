// @vitest-environment node
import {describe, expect, it} from "vitest";
import {EYE_SHAPES} from "../src/figure/figure.js";
import {SIGN, VISOR, glowTurn, lightOnce, signAt, visorAt, visorFor} from "../src/figure/visor.js";

// a seeded random, the same rolls every run
function seeded(seed) {
    let state = seed;
    return () => {
        state = (state + 0x6d2b79f5) | 0;
        let t = Math.imul(state ^ (state >>> 15), 1 | state);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

// the visor `seconds` after a run ending `tone` lit it, `lit` being how visorFor drew it, lit as the run ended
function shownAt(lit, seconds) {
    const on = lightOnce(lit, true, lit.since);
    return visorAt(on, on.at + seconds, false);
}

describe("a run's end shown in the eyes", () => {
    it("draws, with a seeded random, the crosses for some failures and the ticks for some passes, the plain glow for the rest", () => {
        const random = seeded(2758);
        for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
            const lit = Array.from({length: 60}, (_, index) => visorFor([{tone}], null, index * 10, random));
            const signs = lit.filter((each) => each.sign);
            expect(signs.length, `${tone}: some`).toBeGreaterThan(5);
            expect(signs.length, `${tone}: never every time, most the plain glow`).toBeLessThan(30);
            for (const each of signs) expect(shownAt(each, 1).sign.name).toBe(name);
            for (const each of lit.filter((one) => !one.sign)) {
                const glow = shownAt(each, 1);
                expect(glow.sign).toBeUndefined();
                expect(glow.glow).toBe(1);
            }
        }
    });

    it("shows the sign in the eyes in the run's own colour, the visor dark, turned toward the viewer", () => {
        for (const [tone, name] of [["bad", "cross"], ["good", "tick"]]) {
            const shown = shownAt({tone, at: 0, sign: true}, 1.2);
            expect(shown.colour).toEqual(VISOR.colours[tone]);
            expect([shown.glow, shown.eyes]).toEqual([0, 1]);
            expect(shown.sign.name).toBe(name);
            expect(EYE_SHAPES[name].glows, name).toBe(true);
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
