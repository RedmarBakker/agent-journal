// @vitest-environment node
import {expect, test} from "vitest";

const {EAGER, eagerFor, secondsLeft} = await import("../src/figure/reactions.js");

// a bar `elapsed` seconds into a run whose projected end is `left` seconds away at its pace
const bar = (left, began = 100) => {
    const elapsed = 120;
    return {began, share: elapsed / (elapsed + left), ended: "", element: null};
};

test("the anticipation begins in the last ten seconds projected from the run's pace, not at a share of the bar", () => {
    expect(EAGER.lead).toBe(10);
    expect(secondsLeft(120, bar(12).share)).toBeCloseTo(12, 6);
    expect(eagerFor(bar(12), null, () => 0, 220).eager, "twelve seconds out it has not begun").toEqual(null);
    expect(eagerFor(bar(9), null, () => 0, 220).eager.on, "nine seconds out it has").toBe(true);
});

test("it calms down when the projection moves back past ten seconds and a grace period, and takes up again when the end is near", () => {
    const on = eagerFor(bar(9), null, () => 0, 220).eager;
    expect(eagerFor(bar(EAGER.lead + EAGER.grace - 1), on, () => 0, 221).eager.on, "within the grace it holds").toBe(true);
    const calm = eagerFor(bar(EAGER.lead + EAGER.grace + 5), on, () => 0, 222).eager;
    expect(calm.on).toBe(false);
    expect(eagerFor(bar(EAGER.lead + EAGER.grace + 5), calm, () => 0, 223).eager.on, "it stays calm while the end is far").toBe(false);
    expect(eagerFor(bar(8), calm, () => 0, 224).eager.on, "the end near again, it is eager again").toBe(true);
});
