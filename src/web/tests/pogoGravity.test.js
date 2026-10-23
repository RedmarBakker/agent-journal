import {expect, test} from "vitest";
import {ACTS, pogoBounces, pogoHop} from "../src/figure/acts.js";
import {pogoAt, pogoFall} from "../src/domain/figureMotion.js";

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

test("the throw rises past the bubble's edge and slows to its top, where the figure lets the stick go and falls onto the bubble on its own feet, with no bounce after", () => {
    const {spring, release, drop, over} = ACTS.pogo;
    // the top of the throw is where the spring ends, past the edge by `over`, and the hands let go and the stick falls from there
    const rise = [...Array(400).keys()].map((n) => spring[0] + ((spring[1] - spring[0]) * n) / 399).map(at);
    expect(Math.min(...rise.map((point) => point.y))).toBeCloseTo(leg.y - over * SIZE, 0);
    expect(at(spring[1]).y).toBeCloseTo(leg.y - over * SIZE, 6);
    expect(release[0]).toBe(spring[1]);
    expect(drop[0]).toBe(spring[1]);
    // it slows to the top: the last tenth of the rise covers less than the first
    expect(rise[0].y - rise[40].y).toBeGreaterThan(3 * (rise[359].y - rise[399].y));
    // from the top it only falls, faster and faster, onto the bubble, and stays there: never up again, no hop on the stick
    const falls = pogoFall(leg, from);
    expect(falls[1]).toBeLessThan(1);
    const after = [...Array(400).keys()].map((n) => at(spring[1] + ((1 - spring[1]) * n) / 399));
    for (const [index, point] of after.entries()) if (index) expect(point.y).toBeGreaterThanOrEqual(after[index - 1].y);
    expect(at(falls[1])).toEqual({x: leg.x, y: leg.y});
    for (const u of [falls[1], (falls[1] + 1) / 2, 1]) expect(at(u)).toEqual({x: leg.x, y: leg.y});
    // the fall takes as long against the rise as one gravity has it: the square root of its height against the rise's
    const ratio = (falls[1] - falls[0]) / (spring[1] - spring[0]);
    expect(ratio).toBeCloseTo(Math.sqrt((over * SIZE) / (from.y - leg.y + over * SIZE)), 6);
});
