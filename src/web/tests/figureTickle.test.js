// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";
import {SHOWPIECES, choicesFor, draw} from "../src/figure/pile.js";
import {TICKLE, UNTICKLED, movedTo, tickling} from "../src/figure/tickle.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the pointer moved along `xs`, one move every `ms` milliseconds from `start`, as the page hands them over the figure's body
const moved = (xs, ms = 40, start = 1000) => xs.reduce((pointer, x, index) => movedTo(pointer, x, start + index * ms), UNTICKLED);

test("the mouse pointer moved back and forth over the figure tickles it, a single pass does not, and it ends as the pointer leaves or stops", () => {
    // back and forth across it three times in quick succession: tickled
    const xs = [400, 420, 440, 460, 440, 420, 400, 420, 440, 460, 440, 420];
    const tickled = moved(xs);
    expect(tickling(tickled, tickled.at)).toBe(true);
    // one pass over it, however long: not tickled
    const pass = moved([380, 400, 420, 440, 460, 480, 500, 520, 540]);
    expect(tickling(pass, pass.at)).toBe(false);
    // a wiggle too small to count is no tickle
    const jitter = moved([400, 403, 400, 403, 400, 403, 400, 403]);
    expect(tickling(jitter, jitter.at)).toBe(false);
    // slow turns, each further apart than the tickle's span, are no tickle
    const slow = moved(xs, 700);
    expect(tickling(slow, slow.at)).toBe(false);
    // the pointer leaving ends it at once, and stopping still on it ends it a moment later
    expect(tickling(UNTICKLED, tickled.at)).toBe(false);
    expect(tickling(tickled, tickled.at + TICKLE.lingers + 1)).toBe(false);
});

test("a tickle starts the swat every time, from the pile with no cooldown, the hands swatting at the pointer and the eyes squeezed shut laughing, for every voice", () => {
    const memory = new Map();
    for (const now of [0, 1, 2]) expect(draw({moment: "tickled", memory, now}, () => 0.5).name, String(now)).toBe("tickle_swat");
    expect(SHOWPIECES.tickle_swat).toBe(0);
    expect(choicesFor({moment: "pastime", free: true, lasted: 1000}).some((entry) => entry.name === "tickle_swat")).toBe(false);
    const swat = CLIPS.find((clip) => clip.name === "tickle_swat");
    for (const voice of Object.keys(stances)) {
        const raised = [];
        for (let frame = 0; frame < swat.frames; frame++) {
            const pose = new Posing(RIG, "stand", 0);
            swat.pose(pose, stanceOf(voice), frame / swat.frames);
            expect(pose.squeezed, `${voice} ${frame}`).toBe(1);
            const moves = pose.moves(0);
            raised.push(Object.fromEntries(["l", "r"].map((side) => [side, pose.head(`hand_${side}`, moves.get(`hand_${side}`)).z])));
        }
        // each hand comes up at the pointer in its turn
        for (const side of ["l", "r"]) expect(Math.max(...raised.map((each) => each[side])), `${voice} ${side}`).toBeGreaterThan(2.2);
    }
});
