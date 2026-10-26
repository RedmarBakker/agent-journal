// @vitest-environment node
import {expect, test} from "vitest";
import {backAt, backPlan, smashAt, smashPlan} from "../src/figure/acts.js";
import {boxAt, tripTo} from "../src/figure/places.js";
import {clipFor, GROUNDED, TRAVELLING} from "../src/domain/figureState.js";
import {legAt} from "../src/domain/figureMotion.js";

const figure = {size: 112, below: 0.05};
const world = {left: 0, top: 0, right: 900, bottom: 700};
const place = {x: 450, y: 620, posture: "stand"};
const bugs = [{wall: "top", along: 0.5, way: 0}];
const floor = {left: 80, right: 820, top: place.y};

test("the first firing spot is a normal walk before the queued rifle draw, with no jump at either end", () => {
    const [plan] = backPlan(bugs, world, {x: place.x, y: 560, left: floor.left, right: floor.right}, figure.size);
    expect(Math.abs(plan.to - place.x)).toBeGreaterThan(200);
    const spot = {...place, x: plan.to};
    const trip = tripTo(place, spot, figure, {straight: true, random: () => 1});
    const walks = trip.legs.filter((leg) => leg.ms > 0);
    expect(walks).toHaveLength(1);
    expect(walks[0].hopping).not.toBe(true);
    const box = boxAt(place, figure);
    const from = {x: box.left, y: box.top};
    let previous = from;
    for (let elapsed = 0; elapsed <= walks[0].ms + 1000 / 60; elapsed += 1000 / 60) {
        const at = legAt(walks[0], from, elapsed);
        expect(Math.abs(at.x - previous.x), `distance at ${elapsed}ms`).toBeLessThanOrEqual(1.51);
        expect(at.y).toBeCloseTo(from.y, 8);
        previous = at;
    }
    expect(previous.x + figure.size / 2).toBeCloseTo(spot.x, 8);
    const beat = {clip: "bug_shot", facing: 180, onto: true};
    const scene = {mode: GROUNDED, place, beat, state: "idle", doing: "idle"};
    expect(clipFor({...scene, trip}, () => true).clip, "the draw waits even while the trip is being prepared").toBe("idle");
    expect(clipFor({...scene, mode: TRAVELLING, trip: {...trip, started: true, moves: true}}, () => true).clip).toBe("walk");
    expect(clipFor({...scene, place: spot, trip: null}, () => true).clip).toBe("bug_shot");
    const atStart = backAt(backPlan(bugs, world, {...spot, y: 560, left: floor.left, right: floor.right}, figure.size), 0, figure.size);
    expect(atStart.x, "drawing the rifle starts exactly where the walk ended").toBeCloseTo(spot.x, 8);
});

test("combat movement plans preserve their actual starting position even near an end of the floor", () => {
    for (const x of [floor.left + 2, 450, floor.right - 2]) {
        expect(backAt(backPlan(bugs, world, {x, y: 560, left: floor.left, right: floor.right}, figure.size), 0, figure.size).x).toBe(x);
        expect(smashAt(smashPlan(x, floor, figure.size), 0, figure.size).figure + floor.left).toBe(x);
    }
});
