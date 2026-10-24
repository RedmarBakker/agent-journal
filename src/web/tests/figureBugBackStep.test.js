// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, Posing} = await import("../src/figure/figure.js");
const {ACTS, backAt, backPlan, bugShotTimes, wallBugAt} = await import("../src/figure/acts.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "bug_shot");
const {limit} = ACTS.bug_shot.back;
const SIZE = 112;
const WORLD = {left: 0, top: 0, right: 800, bottom: 600};
// a figure mid-floor with its eyes at 300, on a floor across the whole window
const AT = {x: 400, y: 300, left: 0, right: 800};
// a bug that keeps still on its wall: `along` of the way down the left or right wall, or across the top one
const bug = (wall, along) => ({wall, along, way: 0});
const steepness = (at, spot) => (Math.atan2(Math.abs(spot.y - at.y), Math.abs(spot.x - at.x)) * 180) / Math.PI;

test("a bug nearly straight above is backed away from along the floor until its angle is within the limit, before the shot", () => {
    const above = bug("top", 0.5);
    const [leg] = backPlan([above], WORLD, AT, SIZE);
    const spot = wallBugAt(above, WORLD, bugShotTimes(0).shot);
    expect(steepness({...AT, x: AT.x}, spot), "straight above before").toBeGreaterThan(limit);
    expect(leg.to, "it stepped").not.toBe(leg.from);
    expect(steepness({...AT, x: leg.to}, spot), "within the limit once backed").toBeLessThanOrEqual(limit + 0.01);
    expect(Math.abs(spot.x - leg.to), "further from the bug along the floor").toBeGreaterThan(Math.abs(spot.x - leg.from));
    expect(leg.end, "the walk is over before the shot").toBeLessThan(bugShotTimes(0).shot * ACTS.bug_shot.fps);
    expect(leg.begin).toBeLessThan(leg.end);
});

test("a bug nearly straight below is backed away from too, to the far side of the bug", () => {
    const below = bug("left", 0.9);
    const high = {...AT, x: 300, y: 40};
    const [leg] = backPlan([below], WORLD, high, SIZE);
    const spot = wallBugAt(below, WORLD, bugShotTimes(0).shot);
    expect(steepness(high, spot)).toBeGreaterThan(limit);
    expect(leg.to).toBeGreaterThan(leg.from);
    expect(steepness({...high, x: leg.to}, spot)).toBeLessThanOrEqual(limit + 0.01);
});

test("a bug at an easy angle is shot without a step, and one a bug before backed far enough from is not stepped for again", () => {
    const easy = bug("left", 0.5);
    expect(backPlan([easy], WORLD, AT, SIZE).map((leg) => leg.to - leg.from)).toEqual([0]);
    const both = backPlan([bug("top", 0.5), bug("top", 0.52)], WORLD, AT, SIZE);
    expect(both[0].to).not.toBe(both[0].from);
    expect(both[1].to, "the second is already within the limit from where it stands").toBe(both[1].from);
});

test("the figure never backs past the margin from the end of its floor, and never walks toward the bug", () => {
    const margin = 800 - ACTS.bug_shot.back.margin * SIZE;
    const [leg] = backPlan([bug("top", 0.5)], WORLD, {...AT, x: 420, y: 600}, SIZE);
    expect(leg.to, "backed as far as the margin allows, short of the angle").toBe(margin);
    const [past] = backPlan([bug("top", 0.5)], WORLD, {...AT, x: 790, y: 600}, SIZE);
    expect(past.to, "a figure already past the margin stays where it is").toBe(790);
    const [aside] = backPlan([bug("top", 0.02)], WORLD, {...AT, x: 20}, SIZE);
    expect(aside.to, "away from a bug just on its right is away from it").toBeGreaterThan(aside.from);
});

test("it steps back only between the walk and the aim of its bug's turn, one way, its stride growing as it goes", () => {
    const plan = backPlan([bug("top", 0.5)], WORLD, AT, SIZE);
    const [leg] = plan;
    expect(backAt(plan, leg.begin - 1, SIZE)).toEqual({x: leg.from, steps: 0, way: 0});
    const early = backAt(plan, leg.begin + (leg.end - leg.begin) * 0.25, SIZE);
    const late = backAt(plan, leg.begin + (leg.end - leg.begin) * 0.75, SIZE);
    expect(Math.sign(early.x - leg.from)).toBe(early.way);
    expect(Math.abs(late.x - leg.from)).toBeGreaterThan(Math.abs(early.x - leg.from));
    expect(late.steps).toBeGreaterThan(early.steps);
    const after = backAt(plan, leg.end + 5, SIZE);
    expect(after).toMatchObject({x: leg.to, way: 0});
});

test("backing away, the legs step backward and the figure still faces the bug, the rifle held on it", () => {
    const moves = (walkWay, stride) => {
        const pose = new Posing(RIG, "stand", stride);
        pose.walkWay = walkWay;
        pose.target = {x: 0.5, y: -1.6};
        clip.pose(pose, stanceOf(Object.keys(stances)[0]), ACTS.bug_shot.turn[0] + 0.1);
        return pose.moves(0);
    };
    const thigh = (walked) => moves(walked[0], walked[1]).get("thigh_l").elements.join(",");
    expect(thigh([1, -0.25]), "backward is the walk's cycle run the other way").not.toBe(thigh([1, 0.25]));
    expect(thigh([1, -0.25])).not.toBe(thigh([0, -0.25]));
    expect(moves(1, -0.25).get("head").elements.slice(0, 3).map((n) => Math.round(n * 1e4)), "the body is turned as it was").toEqual(moves(0, 0).get("head").elements.slice(0, 3).map((n) => Math.round(n * 1e4)));
});
