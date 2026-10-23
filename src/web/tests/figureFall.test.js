import {describe, expect, it} from "vitest";
import {FALLS, GRAVITY, fallOf, fallStep} from "../src/domain/falls.js";

describe("a voice's fall", () => {
    it("gives every voice a landing of its own, and a voice without one the butler's", () => {
        expect(Object.keys(FALLS).sort()).toEqual(["butler", "coach", "colleague", "homie", "squire"]);
        expect(new Set(Object.values(FALLS).map((fall) => JSON.stringify(fall))).size).toBe(Object.keys(FALLS).length);
        expect(fallOf("nobody")).toBe(FALLS.butler);
    });
});

describe("a figure whose ground drops away", () => {
    it("falls faster each frame and lands on the floor the moment it touches, never below it", () => {
        let state = {y: 0, speed: 0};
        const ys = [];
        for (let frame = 0; frame < 60 && !state.landed; frame++) {
            state = fallStep(state, 100, 1 / 60);
            ys.push(state.y);
        }
        const steps = ys.slice(1).map((y, i) => y - ys[i]);
        expect(state).toEqual({y: 100, speed: 0, landed: true});
        expect(Math.max(...ys)).toBe(100);
        expect(steps.slice(0, -1).every((step, i) => i === 0 || step >= steps[i - 1])).toBe(true);
    });

    it("falls at a real fall's speed: its own height in about a third of a second, as a body drops, and a frame missed while away does not drop it through the floor", () => {
        let state = {y: 0, speed: 0};
        let seconds = 0;
        while (!state.landed) {
            state = fallStep(state, 112, 1 / 60);
            seconds += 1 / 60;
        }
        expect(seconds).toBeCloseTo(Math.sqrt((2 * 112) / GRAVITY), 1);
        expect(seconds).toBeLessThan(0.35);
        expect(fallStep({y: 0, speed: 0}, 500, 5).y).toBeLessThan(10);
    });

    it("lands with a quick bounce: every voice's landing squash is over in a quarter of a second", () => {
        // VoiceFigure.vue plays the landing over half the voice's landing time
        for (const fall of Object.values(FALLS)) expect(fall.ms * 0.5).toBeLessThanOrEqual(250);
    });
});
