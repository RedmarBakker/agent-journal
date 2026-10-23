// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, lookToward} from "../src/figure/figure.js";
import {progressEdge} from "../src/figure/places.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the docked bars, with a progress bar's fill running on them or none
const docks = (fill) => ({querySelector: (selector) => (selector === "[data-figure-progress]" ? fill : null)});
const fillTo = (right) => ({getBoundingClientRect: () => ({left: 300, right, top: 700, bottom: 702, width: right - 300, height: 2})});

test("the figure finds the leading edge of a progress bar running on the docked bars it stands on, and none once the bar has ended", () => {
    expect(progressEdge(docks(fillTo(420)))).toEqual({x: 420, y: 701});
    expect(progressEdge(docks(fillTo(610)))).toEqual({x: 610, y: 701});
    expect(progressEdge(docks(null))).toBe(null);
});

test("looking at a bar's edge below its feet, the head turns down and follows the edge as it moves along", () => {
    for (const voice of Object.keys(stances)) {
        for (const clip of CLIPS.filter((each) => ["idle", "waiting", "think"].includes(each.name))) {
            const lookedAt = (at, facing = 0) => {
                const pose = new Posing(RIG, "stand", 0);
                clip.pose(pose, stanceOf(voice), 0);
                lookToward(pose, at, facing);
                return new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(facing).get("head"));
            };
            // an edge just below the feet, early on the bar to the left and later to the right
            const early = lookedAt({x: 0.25, y: 1.05});
            const later = lookedAt({x: 0.75, y: 1.05});
            expect(early.z, `${voice} ${clip.name}`).toBeLessThan(-0.3);
            expect(later.z, `${voice} ${clip.name}`).toBeLessThan(-0.3);
            expect(early.x, `${voice} ${clip.name}`).toBeLessThan(0);
            expect(later.x, `${voice} ${clip.name}`).toBeGreaterThan(0);
            // turned toward the viewer's left, it still looks where the edge is in its picture
            expect(lookedAt({x: 0.75, y: 1.05}, 30).x, `${voice} ${clip.name}`).toBeGreaterThan(0);
        }
    }
});
