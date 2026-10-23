// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {ACTING, CLIPS, Posing, WAIT} from "../src/figure/figure.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the way each arm points, from the shoulder to the elbow and from the elbow to the wrist
function armsOf(clip, voice, t) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), t);
    const moves = pose.moves(0);
    const at = (name) => pose.head(name, moves.get(name));
    return ["l", "r"].flatMap((side) => [at(`forearm_${side}`).sub(at(`upper_arm_${side}`)).normalize(), at(`hand_${side}`).sub(at(`forearm_${side}`)).normalize()]);
}

// the widest angle, in degrees, between the same parts of two arms
const apart = (a, b) => Math.max(...a.map((way, index) => THREE.MathUtils.radToDeg(way.angleTo(b[index]))));

test("the waiting figure keeps both arms as it stands idle all through the wait, for every voice, and whistles toward the end", () => {
    const waiting = CLIPS.find((each) => each.name === "waiting");
    const idle = CLIPS.find((each) => each.name === "idle");
    expect(waiting.frames).toBe(WAIT.intro + WAIT.hold + WAIT.outro);
    expect((WAIT.whistleSpan[1] - WAIT.whistleSpan[0]) * WAIT.hold / ACTING.fps).toBeGreaterThan(2);
    for (const voice of Object.keys(stances)) {
        const standing = armsOf(idle, voice, 0);
        for (let frame = 0; frame < waiting.frames; frame++) {
            expect(apart(armsOf(waiting, voice, frame / waiting.frames), standing), `${voice} ${frame}`).toBeLessThan(5);
            const pose = new Posing(RIG, "stand", 0);
            waiting.pose(pose, stanceOf(voice), frame / waiting.frames);
            expect([pose.props.size, pose.stowed.size], `${voice} ${frame}`).toEqual([0, 0]);
        }
    }
});
