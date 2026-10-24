// @vitest-environment node
import {expect, test} from "vitest";

const {aimedAt, legAt} = await import("../src/domain/figureMotion.js");
const {tripBetween} = await import("../src/figure/places.js");
const {ACTS} = await import("../src/figure/acts.js");
const {JUMP} = await import("../src/figure/climbs.js");

const SIZE = 112;
// how far up a hop may go past where it was planned to land, the jump's limit, for a figure this tall standing
const MOST = JUMP.most * SIZE * 0.85;
const FRAME = 16;

// A pogo climb from the ground up to a bubble's top, stepped frame by frame as the figure is (VoiceFigure hopOn): the bubble rising
// `rise(share)` pixels by `share` of the stick's act, the climb re-aimed at it every frame; where the figure was each frame, the hop's
// top, where it ended against where the bubble is then, and whether the bubble rose out of its reach
function climb(rise) {
    const from = {x: 300, y: 600};
    const to = {x: 300, y: 200};
    let trip = {to, legs: tripBetween(from, to, SIZE, {pogo: true}).legs};
    let leg = trip.legs.find((each) => each.pogo);
    let start = {...from};
    const ms = leg.ms;
    const heights = [];
    for (let elapsed = 0; elapsed <= ms; elapsed += FRAME) {
        const aimed = aimedAt(trip, leg, start, {...to, y: to.y - rise(elapsed / ms)}, MOST);
        if (aimed.lost) return {heights, lost: true};
        ({trip, leg, from: start} = aimed);
        heights.push(legAt(leg, start, elapsed).y);
    }
    return {heights, top: Math.min(...heights), end: heights.at(-1), bubble: to.y - rise(1), lost: false};
}

test("the pogo stick climbs onto a bubble that rises while it bounces: each hop aimed at where the bubble is now, the last one higher, landing on it and never falling", () => {
    const still = climb(() => 0);
    expect(still.end).toBeCloseTo(still.bubble, 6);
    // the bubble rises 60 pixels as it goes, most of it during the bounces and the throw
    const rising = climb((share) => 60 * Math.min(share / ACTS.pogo.spring[1], 1));
    expect(rising.lost).toBe(false);
    expect(rising.end, "lands on the bubble where it is now, to the re-aim's third of a pixel").toBeCloseTo(rising.bubble, 0);
    expect(rising.top, "its last hop that much higher").toBeCloseTo(still.top - 60, 0);
    // after its top it only comes down onto the bubble: never below it, no fall past
    const after = rising.heights.slice(rising.heights.indexOf(rising.top));
    for (const [index, y] of after.entries()) expect(y, `frame ${index} after the top`).toBeLessThanOrEqual(rising.bubble + 0.3);
    // a bubble rising as it comes down, too late for the throw, is still landed on, the fall over within the act
    const late = climb((share) => (share > 0.9 ? 30 * (share - 0.9) * 10 : 0));
    expect(late.end).toBeCloseTo(late.bubble, 0);
});

test("a bubble rising past the jump's limit above where the hop was aimed is out of reach: the climb is lost, and never thrown past the limit", () => {
    const far = climb((share) => (MOST + 40) * share);
    expect(far.lost).toBe(true);
    const near = climb((share) => (MOST - 10) * Math.min(share / ACTS.pogo.spring[1], 1));
    expect(near.lost).toBe(false);
    expect(near.end).toBeCloseTo(near.bubble, 0);
    expect(climb(() => 0).top - near.top, "never higher than the limit above its planned top").toBeLessThanOrEqual(MOST);
});
