import {expect, test} from "vitest";
import {ACTS, pogoBounces, pogoHop} from "../src/figure/acts.js";
import {pogoAt} from "../src/domain/figureMotion.js";

const SIZE = 100;
const from = {x: 100, y: 600};
const leg = {x: 160, y: 380, ms: (ACTS.pogo.frames / ACTS.pogo.fps) * 1000, size: SIZE, pogo: true};
const at = (u) => pogoAt(leg, from, u * leg.ms);

test("each bounce on the pogo stick is a parabola under one gravity: fast off the ground, slow at the top, and a higher one lasting longer", () => {
    const [first, , last] = pogoBounces();
    // within one hop, the height covered in the first tenth beats the height covered in the tenth before its top
    const hop = (s) => pogoHop([1], s).height;
    expect(hop(0.1) - hop(0)).toBeGreaterThan(3 * (hop(0.5) - hop(0.4)));
    expect(hop(0.5)).toBeCloseTo(1, 6);
    // a higher bounce takes longer, as the square root of its height
    const lengths = (share) => pogoHop(pogoBounces(), share).index;
    const starts = [0, 1, 2].map((index) => [...Array(1001).keys()].map((n) => n / 1000).find((share) => lengths(share) === index));
    expect((starts[2] - starts[1]) / (starts[1] - starts[0])).toBeCloseTo(Math.sqrt(2 * first / first), 1);
    expect(last).toBeGreaterThan(first);
});

test("the throw onto the place rises past its edge, slows at the top, falls back onto it and settles there in small hops", () => {
    const {spring, settling, over} = ACTS.pogo;
    const landed = spring[0] + (spring[1] - spring[0]) * (1 - settling);
    const samples = [...Array(400).keys()].map((n) => spring[0] + ((landed - spring[0]) * n) / 399).map(at);
    const highest = Math.min(...samples.map((point) => point.y));
    expect(highest).toBeCloseTo(leg.y - over * SIZE, 0);
    // it falls back from above the edge onto it: the last part of the throw comes down, not up
    expect(samples.at(-1).y).toBeCloseTo(leg.y, 0);
    expect(samples.at(-2).y).toBeLessThan(samples.at(-1).y);
    // it settles on the place with a hop smaller than the overshoot, then stands on it while the stick falls away
    const settled = [...Array(100).keys()].map((n) => at(landed + ((spring[1] - landed) * n) / 99));
    expect(Math.min(...settled.map((point) => point.y))).toBeGreaterThan(leg.y - over * SIZE);
    expect(Math.min(...settled.map((point) => point.y))).toBeLessThan(leg.y);
    expect(at(0.95)).toEqual({x: leg.x, y: leg.y});
});
