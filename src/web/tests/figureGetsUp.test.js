// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, GROUND, blendedMoves, drawnPose} from "../src/figure/figure.js";
import {CHANGE_SECONDS, SEATED, boxAt, leavesSeat} from "../src/figure/places.js";
import {FRAMED} from "../src/figure/frame.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);

const FIGURE = {size: 112, below: GROUND};
// the line the figure sits on and gets up onto, an edge's top or a floor's, in page pixels
const LINE = {x: 500, y: 600};
// the ease the player gives a change (player.js smooth)
const smooth = (k) => k * k * (3 - 2 * k);

// where on the page the lower sole of `moves` is, drawn in the picture whose top is `top`
const soleAt = (pose, moves, top) => {
    const z = Math.min(...["l", "r"].map((side) => pose.head(`foot_${side}`, moves.get(`foot_${side}`)).z));
    return top + FIGURE.size * (1 - FIGURE.below) - (z / FRAMED.height) * FIGURE.size;
};

test("seated on an edge or composed, then playing any standing act, the eagerness for a run's end among them, the figure's feet are on the floor line from the act's first frame, never sunk through it nor floating over it", () => {
    const standing = CLIPS.filter((clip) => clip.postures.includes("stand") && !clip.postures.some((posture) => SEATED.has(posture)));
    expect(standing.map((clip) => clip.name)).toContain("eager");
    for (const voice of Object.keys(stances)) {
        const stance = stanceOf(voice);
        for (const seat of ["sit", "composed"]) {
            const place = {...LINE, posture: seat};
            const seated = drawnPose(RIG, stance, clipNamed("idle"), 0, 0, {posture: seat});
            // getting up the seat's drop goes at once: the picture stands on the line from the first frame (VoiceFigure rest)
            expect(leavesSeat(seat, "stand"), seat).toBe(true);
            const top = boxAt(place, FIGURE, "stand").top;
            for (const clip of standing) {
                let previous = seated.pose.moves(seated.turned);
                const from = previous;
                // its first frames, a twelfth of a second apart, while the body eases out of the seat and after
                for (let frame = 0; frame < Math.min(clip.frames, 6); frame++) {
                    const label = `${voice} ${seat} then ${clip.name} frame ${frame}`;
                    const k = Math.min(frame / clip.fps / CHANGE_SECONDS, 1);
                    const {pose, turned} = drawnPose(RIG, stance, clip, frame, 0, {posture: "stand"});
                    const blend = {from, previous, k: smooth(k), plant: leavesSeat(seat, "stand")};
                    const {moves} = blendedMoves(RIG, pose, turned, blend);
                    previous = moves;
                    // the feet where the act alone puts them, standing on the line
                    const own = soleAt(pose, pose.moves(turned), top);
                    expect(Math.abs(soleAt(pose, moves, top) - own), label).toBeLessThan(0.5);
                }
            }
        }
    }
});
