// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, blendedMoves, drawnPose} from "../src/figure/figure.js";
import {CHANGE_SECONDS, POSTURES, drawnIn, leavesSeat} from "../src/figure/places.js";
import {airborneFrame, fallingFrom} from "../src/domain/figureMotion.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);
const IDLE = clipNamed("idle");
const FRAME_MS = 1000 / 30;
// the ease the player gives a change (player.js smooth)
const smooth = (k) => k * k * (3 - 2 * k);
// the soles of the figure standing at rest, in its own units, on the floor line it stands on
const REST_SOLE = Math.min(RIG.heads.get("foot_l").z, RIG.heads.get("foot_r").z);

// How the legs stand in `moves` of `pose`: the most either knee bends, in degrees, and how far the lower sole is above the floor line
function legsOf(pose, moves) {
    const at = (bone) => pose.head(bone, moves.get(bone));
    const knee = (side) => at(`thigh_${side}`).sub(at(`shin_${side}`)).negate().angleTo(at(`foot_${side}`).sub(at(`shin_${side}`)));
    return {
        bent: Math.max(...["l", "r"].map((side) => THREE.MathUtils.radToDeg(knee(side)))),
        sole: Math.min(at("foot_l").z, at("foot_r").z) - REST_SOLE,
    };
}

// The player's changes (player.js show) stepped at 30 frames a second for `voice`: each clip drawn in its posture, eased out of the one
// before over the change, on its feet getting up off a seat (places.js leavesSeat), until the change has settled
function player(voice) {
    let moves = null, blend = null, shape = "", posture = "", ms = 0;
    return (clip, drawn, seconds) => {
        let pose = null;
        for (const end = ms + seconds * 1000; ms < end; ms += FRAME_MS) {
            const now = `${clip.name}/${drawn}`;
            if (now !== shape && moves) blend = {from: moves, began: ms, plant: leavesSeat(posture, drawn) || (Boolean(blend?.plant) && POSTURES[drawn].drop === 0)};
            [shape, posture] = [now, drawn];
            const drew = drawnPose(RIG, stanceOf(voice), clip, Math.floor(((ms - (blend?.began ?? 0)) / 1000) * clip.fps) % clip.frames, 0, {posture: drawn});
            const k = blend ? Math.min((ms - blend.began) / 1000 / CHANGE_SECONDS, 1) : 1;
            const step = {from: blend?.from, previous: moves, k: smooth(k), settled: false, plant: blend?.plant};
            const result = blendedMoves(RIG, drew.pose, drew.turned, blend ? step : null);
            moves = result.moves;
            if (blend && result.settled) blend = null;
            pose = drew.pose;
        }
        return {pose, moves};
    };
}

// the acts the figure gets up from or stands through before idling: each seated posture's own, and a handful of standing acts that bend
// the knees, crouch, tumble or lift the figure
const BEFORE = [["ledge_sit", "sit"], ["idle", "sit"], ["idle", "composed"], ["idle", "lounge"], ["eager", "stand"], ["hand_rub", "stand"], ["pogo", "stand"], ["tumble", "stand"], ["stretch", "stand"]];

test("standing idle after a seated or standing act, the figure stands on straight legs with its soles on the floor line, never bent and sunk", () => {
    for (const [name, posture] of BEFORE) {
        const clip = clipNamed(name);
        expect(clip.postures, name).toContain(posture);
        const play = player("butler");
        play(clip, posture, Math.min(clip.frames / clip.fps, 1));
        const {pose, moves} = play(IDLE, "stand", 0.75);
        const legs = legsOf(pose, moves);
        const label = `idle after ${name} in ${posture}`;
        expect(legs.bent, label).toBeLessThan(12);
        expect(Math.abs(legs.sole), label).toBeLessThan(0.03);
    }
});

test("seated on the docked bar's edge when its floor drops away, landing where there is no edge to sit on, as the floor beside the composer, it lands on its feet and idles standing straight; on an edge it keeps its seat", () => {
    const floors = [
        {id: "home", kind: "compose", left: 300, right: 700, top: 600},
        {id: "foot", kind: "foot", left: 0, right: 1000, top: 760},
    ];
    const fall = (spot) => {
        let step = {airborne: fallingFrom(spot, null, floors, 0), landed: null};
        for (let frame = 1; frame < 600 && !step.landed; frame++) step = airborneFrame(step.airborne, floors, frame * FRAME_MS);
        return step.landed;
    };
    // off the compose box's end, beside the composer: on its feet, drawn standing, its legs straight and on the line
    const beside = fall({x: 800, y: 540, posture: "sit", face: 0, leans: true});
    expect(beside.spot).toMatchObject({y: 760, posture: "stand"});
    expect(beside.standing).toBe(true);
    const {pose, turned} = drawnPose(RIG, stanceOf("butler"), IDLE, 0, 0, {posture: drawnIn({clip: IDLE}, beside.spot.posture)});
    const legs = legsOf(pose, pose.moves(turned));
    expect(legs.bent).toBeLessThan(12);
    expect(Math.abs(legs.sole)).toBeLessThan(0.03);
    // over the compose box, an edge it sits on: seated as it was, and sitting composed on a floor it keeps that too
    expect(fall({x: 500, y: 540, posture: "sit", face: 0}).spot.posture).toBe("sit");
    expect(fall({x: 800, y: 540, posture: "composed", face: 0}).spot.posture).toBe("composed");
});
