// @vitest-environment node
import {describe, expect, it} from "vitest";
import {EYES, EYE_SHAPES, LOOK_EASE, lookStrength} from "../src/figure/figure.js";
import {LOOK_SECONDS, reactionTo, workMoments} from "../src/figure/reactions.js";

// the look the eyes take on at `moment`, on any of a hundred rolls through its tickets, or none
const looksAt = (moment) => new Set(Array.from({length: 100}, (_, index) => reactionTo(moment, new Map(), 0, () => (index + 0.5) / 100)?.look).filter(Boolean));

// the moments of the agent's work, by name, while the agent is in `state`
const momentsIn = (state) => workMoments(state, false, 0, 1).moments.map((moment) => moment.beat);

const LOOKS = {working: "focused", failing: "narrowed", passing: "bright", resting: "calm", glancing: "eyeing"};

describe("the eyes' looks", () => {
    it("has a shape of its own for working, failing, passing, resting and glancing", () => {
        const shapes = Object.values(LOOKS).map((mood) => EYES[mood].shape);
        expect(shapes).toEqual(Object.values(LOOKS));
        for (const shape of shapes) expect(EYE_SHAPES[shape], shape).toBeDefined();
        const drawn = shapes.map((shape) => {
            const {geometry, size, aside, up, mirrored} = EYE_SHAPES[shape];
            return JSON.stringify([geometry.uuid, size, aside, up, Boolean(mirrored)]);
        });
        expect(new Set(drawn).size, "no two drawn alike").toBe(shapes.length);
    });

    it("plays each at its moment: focused while the agent works, narrowed at a failure, bright at a pass, calm at rest, eyeing at a new card", () => {
        for (const state of ["writing", "reading", "searching", "building"]) expect(momentsIn(state), state).toContain("working");
        expect(momentsIn("thinking"), "thinking keeps its own round eyes").not.toContain("working");
        expect(momentsIn("idle")).toContain("resting");
        expect(looksAt("working")).toEqual(new Set(["focused"]));
        expect(looksAt("tests_failed")).toEqual(new Set(["narrowed"]));
        expect(looksAt("failed")).toEqual(new Set(["narrowed"]));
        expect(looksAt("tests_passed")).toEqual(new Set(["bright"]));
        expect(looksAt("check_passed")).toEqual(new Set(["bright"]));
        expect(looksAt("resting")).toEqual(new Set(["calm"]));
        expect(looksAt("card_arrived")).toEqual(new Set(["eyeing"]));
    });

    it("comes and goes, not a fixed face: each look now and then, with a cooldown between", () => {
        for (const moment of ["working", "resting"]) {
            expect(reactionTo(moment, new Map(), 0, () => 0.99), `${moment} not every time`).toBe(null);
            const memory = new Map();
            expect(reactionTo(moment, memory, 100, () => 0)?.look, moment).toBeDefined();
            expect(reactionTo(moment, memory, 105, () => 0), `${moment} not again at once`).toBe(null);
        }
    });

    it("eases into the shape and back to the usual eyes", () => {
        const at = (seconds) => lookStrength({seconds, lasts: LOOK_SECONDS});
        expect(at(0)).toBe(0);
        expect(at(LOOK_EASE.into / 2)).toBeGreaterThan(0);
        expect(at(LOOK_EASE.into / 2)).toBeLessThan(1);
        expect(at(LOOK_SECONDS / 2)).toBe(1);
        expect(at(LOOK_SECONDS - LOOK_EASE.out / 2)).toBeGreaterThan(0);
        expect(at(LOOK_SECONDS - LOOK_EASE.out / 2)).toBeLessThan(1);
        expect(at(LOOK_SECONDS)).toBe(0);
        const steps = Array.from({length: 31}, (_, index) => at((index / 30) * LOOK_SECONDS));
        const rising = steps.slice(0, 16);
        rising.slice(1).forEach((each, index) => expect(each).toBeGreaterThanOrEqual(rising[index]));
        const falling = steps.slice(15);
        falling.slice(1).forEach((each, index) => expect(each).toBeLessThanOrEqual(falling[index]));
    });
});
