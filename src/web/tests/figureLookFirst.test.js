// @vitest-environment node
import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import * as THREE from "three";
import {CLIPS, Posing, lookToward} from "../src/figure/figure.js";
import {LOOK_FACES, LOOK_TURN_SPEED, faces, gazeAfter} from "../src/figure/reactions.js";
import {VISOR, lightOnce, visorAt, visorFor} from "../src/figure/visor.js";
import {headYaw} from "./support/headYaw.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the figure's 112-pixel picture with its top left at the page's origin, its head's middle 0.3 of the way down, as chat/VoiceFigure.vue has it
const SIZE = 112;
const HEAD = {x: SIZE / 2, y: SIZE * 0.3};
const FRAME_MS = 1000 / 60;

test("a run ends with its mark behind the figure: the head turns to the mark at the look's own pace, and only once it faces it does the visor glow", () => {
    // turned to its right, looking along the box it hammers there, and the run's mark up on the chat to its left, behind it
    const facing = 90;
    const mark = {x: -260, y: -80};
    let gaze = {point: {x: 400, y: 70}, amount: 1, at: 1};
    let lit = visorFor([{tone: "good", card: "messages:7"}], null, 0, () => 0.99);
    const turnedFirst = Math.abs(Math.atan2(mark.y - HEAD.y, mark.x - HEAD.x) - Math.atan2(gaze.point.y - HEAD.y, gaze.point.x - HEAD.x));
    let glowedAt = null;
    for (let frame = 1; frame < 120 && glowedAt === null; frame++) {
        const ms = 1 + frame * FRAME_MS;
        const before = gaze.point;
        // as the page draws a frame: the visor lit once the look faces the mark, the look turned toward the mark while the glow waits
        lit = lightOnce(lit, gaze.amount === 1 && faces(gaze.point, mark, HEAD), ms / 1000);
        gaze = gazeAfter(gaze, lit.at === null ? mark : null, HEAD, ms);
        const swung = Math.abs(Math.atan2(gaze.point.y - HEAD.y, gaze.point.x - HEAD.x) - Math.atan2(before.y - HEAD.y, before.x - HEAD.x));
        expect(Math.min(swung, 2 * Math.PI - swung), `${frame}`).toBeLessThanOrEqual((LOOK_TURN_SPEED * FRAME_MS) / 1000 + 1e-9);
        const shown = visorAt(lit, ms / 1000 + 0.5, false);
        if (lit.at === null) expect(shown, `${frame}: no glow while it turns`).toBe(null);
        else glowedAt = {frame, gaze: before};
    }
    // it glowed, as soon as the turn could bring the head round and not later, and facing the mark when it did, long before the wait ran out
    expect(glowedAt).not.toBe(null);
    expect(glowedAt.frame * FRAME_MS).toBeGreaterThanOrEqual(((turnedFirst - LOOK_FACES) / LOOK_TURN_SPEED) * 1000 - FRAME_MS);
    expect(glowedAt.frame * FRAME_MS).toBeLessThan(VISOR.waits * 1000);
    expect(faces(glowedAt.gaze, mark, HEAD)).toBe(true);
    // the figure drawn with that look, still at its work: its head, with its body turned a little after it, faces back over its shoulder at the mark
    const work = CLIPS.find((clip) => clip.name === "work");
    for (const voice of Object.keys(stances)) {
        const pose = new Posing(RIG, "stand", 0);
        work.pose(pose, stanceOf(voice), 0.5);
        const body = lookToward(pose, {x: glowedAt.gaze.x / SIZE, y: glowedAt.gaze.y / SIZE, amount: 1}, facing);
        expect(Math.abs(body), voice).toBeGreaterThan(0);
        // round from facing the box on its right to looking left across the picture
        expect(headYaw(pose.moves(0)) + body + facing, voice).toBeLessThan(-30);
    }
});

test("a run whose mark the figure cannot turn to glows anyway, once the wait is over", () => {
    let lit = visorFor([{tone: "bad", card: "messages:8"}], null, 10, () => 0.99);
    lit = lightOnce(lit, false, 10 + VISOR.waits - 0.01);
    expect(lit.at).toBe(null);
    lit = lightOnce(lit, false, 10 + VISOR.waits);
    expect(lit.at).toBe(10 + VISOR.waits);
    expect(visorAt(lit, 10 + VISOR.waits + 1, false)).not.toBe(null);
});
