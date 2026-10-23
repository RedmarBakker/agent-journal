// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {ACTING, CLIPS, Posing} from "../src/figure/figure.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// where the arm on `side` points from the shoulder to the hand
function armOf(pose, side) {
    const moves = pose.moves(0);
    const at = (name) => pose.head(name, moves.get(name));
    return at(`hand_${side}`).sub(at(`upper_arm_${side}`)).normalize();
}

test("the butler's arms, with nothing in either since his tray is gone, hang and swing alike while he walks and stands", () => {
    const butler = stanceOf("butler");
    expect([...butler.level, ...butler.busy, ...butler.carried]).toEqual([]);
    const walk = CLIPS.find((clip) => clip.name === "walk");
    const forward = {l: [], r: []};
    for (let frame = 0; frame < walk.frames; frame++) {
        const pose = new Posing(RIG, "stand", 0);
        walk.pose(pose, butler, frame / walk.frames);
        for (const side of ["l", "r"]) {
            const arm = armOf(pose, side);
            expect(arm.z, `${side} ${frame}`).toBeLessThan(-0.7);
            forward[side].push(-arm.y);
        }
    }
    const swing = (side) => Math.max(...forward[side]) - Math.min(...forward[side]);
    expect(swing("l")).toBeGreaterThan(0.3);
    expect(swing("l")).toBeCloseTo(swing("r"), 2);
    // the arms swing against each other about the same middle, as a walker's do
    const middle = (side) => forward[side].reduce((sum, ahead) => sum + ahead, 0) / walk.frames;
    expect(middle("l")).toBeCloseTo(middle("r"), 2);
    forward.l.forEach((ahead, frame) => expect(ahead - middle("l") + forward.r[frame] - middle("r"), `${frame}`).toBeCloseTo(0, 1));
    const idle = new Posing(RIG, "stand", 0);
    CLIPS.find((clip) => clip.name === "idle").pose(idle, butler, 0);
    expect(armOf(idle, "l").z).toBeCloseTo(armOf(idle, "r").z, 6);
    expect(armOf(idle, "l").z).toBeLessThan(-0.7);
});

test("in every resting and default pose both arms hang beside the body as they do standing idle, for every voice", () => {
    const idle = CLIPS.find((clip) => clip.name === "idle");
    const armsOf = (clip, voice, t, posture) => {
        const pose = new Posing(RIG, posture, 0);
        clip.pose(pose, stanceOf(voice), t);
        return ["l", "r"].map((side) => armOf(pose, side));
    };
    // thinking, waiting, paused and asleep after its yawn, standing and seated
    const resting = [["think", 0], ["waiting", 0], ["idle", 0], ["sleep", ACTING.yawnFrames]];
    for (const voice of Object.keys(stances)) {
        for (const posture of ["stand", "sit"]) {
            const standing = armsOf(idle, voice, 0, posture);
            for (const [name, from] of resting) {
                const clip = CLIPS.find((each) => each.name === name);
                for (let frame = from; frame < clip.frames; frame++) {
                    armsOf(clip, voice, frame / clip.frames, posture).forEach((arm, index) =>
                        expect(THREE.MathUtils.radToDeg(arm.angleTo(standing[index])), `${name} ${voice} ${posture} ${frame}`).toBeLessThan(5)
                    );
                }
            }
        }
    }
});
