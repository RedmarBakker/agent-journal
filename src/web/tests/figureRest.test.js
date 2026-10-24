// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, REST} from "../src/figure/figure.js";
import {pastimeFor} from "../src/figure/reactions.js";
import {PILE} from "../src/figure/pile.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);

function posed(clip, voice, t) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), t);
    return pose;
}

const movesOf = (pose) => [...pose.moves(0)].map(([name, move]) => [name, move.elements.map((n) => Math.round(n * 1e4) / 1e4 + 0)]);

test("every voice lies on its back on the floor, a straw in its mouth and a foot crossed over the other knee, and gets up as it stood", () => {
    const rest = clipNamed("rest");
    expect(rest.postures).toEqual(["stand"]);
    for (const voice of Object.keys(stances)) {
        const standing = movesOf(posed(clipNamed("idle"), voice, 0));
        expect(movesOf(posed(rest, voice, 0)), voice).toEqual(standing);
        expect(movesOf(posed(rest, voice, (rest.frames - 1) / rest.frames)), voice).toEqual(standing);
        const steps = rest.frames * 2;
        for (let step = 0; step <= steps; step++) {
            const t = step / steps;
            const pose = posed(rest, voice, t);
            const u = t * rest.frames / (rest.frames - 1);
            if (u < REST.down[1] || u > REST.up[0]) continue;
            const moves = pose.moves(0);
            const at = (name) => pose.head(name, moves.get(name));
            const label = `${voice} ${step}`;
            // lying: nothing stands up off the floor, nothing sinks under it, and the head and the feet lie apart across the picture
            for (const name of RIG.order) expect(at(name).z, `${label} ${name}`).toBeGreaterThan(-0.1);
            for (const name of RIG.order) expect(at(name).z, `${label} ${name}`).toBeLessThan(1.8);
            expect(at("foot_l").x - at("head").x, label).toBeGreaterThan(1.4);
            // the near ankle rests on the far knee
            expect(at("foot_r").distanceTo(at("shin_l")), label).toBeLessThan(0.3);
            // the straw is held in the mouth: on the face's front, below the eyes
            const straw = pose.props.get("straw");
            expect(straw.bone, label).toBe("head");
            const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length);
            expect(straw.at.z, label).toBeLessThan(eyes.z);
            expect(straw.at.y, label).toBeLessThanOrEqual(eyes.y);
            // what the hands carry is put away while they are behind the head
            for (const side of stanceOf(voice).carried) expect(pose.stowed.size, `${label} ${side}`).toBeGreaterThan(0);
        }
    }
});

test("the rest is a pastime of every voice after a long quiet, played only where the figure stands on a floor", () => {
    const pastime = PILE.find((each) => each.when.moment === "pastime" && each.name === "rest");
    expect(pastime.when.voices).toBeUndefined();
    for (const voice of Object.keys(stances)) {
        for (const [posture, played] of [["stand", {clip: "rest", card: "", flies: false}], ["sit", null]]) {
            const scene = {voice, place: {posture}, beats: 0, arriving: false, leaving: false, moving: false, room: Infinity};
            const has = (name) => name === "rest" && clipNamed(name).postures.includes(posture);
            expect(pastimeFor(scene, {state: "idle", lasted: pastime.when.lasted - 1}, new Map(), 0, () => 0, has), voice).toBe(null);
            expect(pastimeFor(scene, {state: "idle", lasted: pastime.when.lasted}, new Map(), 0, () => 0, has), `${voice} ${posture}`).toEqual(played);
        }
    }
});

test("the resting figure whistles now and then, the notes drawn over its head only while it does", () => {
    const rest = clipNamed("rest");
    const whistling = (frame) => rest.marks.frames.some(([from, to]) => frame >= from && frame < to);
    expect(rest.marks.mark).toBe("♪");
    const frames = Array.from({length: rest.frames}, (_, frame) => frame);
    expect(frames.filter(whistling).length).toBeGreaterThan(rest.frames / 5);
    expect(frames.filter((frame) => !whistling(frame)).length).toBeGreaterThan(rest.frames / 2);
});
