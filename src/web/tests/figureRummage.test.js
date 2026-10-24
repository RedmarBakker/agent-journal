// @vitest-environment node
import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import * as THREE from "three";
import {CLIPS, Posing, RUMMAGE_THINGS, SIDES} from "../src/figure/figure.js";
import {ACTS, RUMMAGED, flungAt} from "../src/figure/acts.js";
import {choicesFor} from "../src/figure/pile.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
// the figure's picture is 5.4 of its units high, and as wide
const PICTURE = 5.4;
const act = ACTS.rummage;

// the figure rummaging `u` of the way through, its eyes' middle as a share of the picture out from its middle toward the opening, and the pose
function rummagingAt(voice, u) {
    const pose = new Posing(RIG, "stand", 0);
    CLIPS.find((clip) => clip.name === "rummage").pose(pose, stanceOf(voice), u);
    const moves = pose.moves(0);
    const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye.clone().applyMatrix4(moves.get("head"))), new THREE.Vector3()).multiplyScalar(1 / RIG.eyes.length);
    // the free hand's side, where the opening is: the right, unless that hand is busy
    const out = SIDES[stanceOf(voice).busy.has("r") ? "l" : "r"];
    return {pose, moves, out: (out * eyes.x) / PICTURE, eyes};
}

test("rummaging is one of the searches, picked now and then: the other ways to search are each picked at least as often, and all together far more", () => {
    const searches = choicesFor({moment: "held:search", home: true});
    const rummage = searches.find((each) => each.name === "rummage");
    expect(rummage).toBeTruthy();
    const others = searches.filter((each) => each !== rummage);
    expect(others.map((each) => each.name)).toEqual(["search", "binoculars"]);
    for (const other of others) expect(other.weight, other.name).toBeGreaterThanOrEqual(rummage.weight);
    expect(rummage.weight / searches.reduce((sum, each) => sum + each.weight, 0)).toBeLessThan(0.2);
    expect(CLIPS.find((clip) => clip.name === "rummage")).toMatchObject({ownLook: true, postures: ["stand"]});
});

test("it buries its head in the opening and digs about, then pops out of it holding up the key it found", () => {
    for (const voice of Object.keys(stances)) {
        // standing at the start, its head is out of the opening
        expect(rummagingAt(voice, 0).out, voice).toBeLessThan(act.lip);
        // all the while it digs, its head is in the opening, well past its edge and down in it
        for (let u = act.leans[1]; u < act.pops[0]; u += 0.02) {
            const {out, eyes} = rummagingAt(voice, u);
            expect(out, `${voice} ${u}`).toBeGreaterThan(act.lip + 0.04);
            expect(eyes.z, `${voice} ${u}`).toBeLessThan(2.4);
        }
        // popped out, it stands clear of the opening, the key held up over its head
        const popped = rummagingAt(voice, (act.pops[1] + act.lowers[0]) / 2);
        expect(popped.out, voice).toBeLessThan(act.lip - 0.1);
        expect([...popped.pose.props.keys()], voice).toContain("rummage_key");
        const key = popped.pose.props.get("rummage_key");
        // held upright in the raised hand, high by the head, the key's ring up over the eyes
        const grip = key.at.clone().applyMatrix4(popped.moves.get(key.bone)).z;
        expect(key.frame, voice).toBe("root");
        expect(grip, voice).toBeGreaterThan(2.6);
        expect(grip + RUMMAGE_THINGS.key.shaft + 2 * RUMMAGE_THINGS.key.ring[0], voice).toBeGreaterThan(popped.eyes.z + 0.3);
    }
});

test("each thing it pulls out is thrown along the arc gravity gives it, up over its shoulder and down onto the floor behind, spinning, a new throw each rummage", async () => {
    const {THROW, flightSeconds, throwsFor} = await import("../src/figure/acts.js");
    expect(RUMMAGED).toEqual(["rummage_papers", "rummage_boot", "rummage_bone", "rummage_book"]);
    let seed = 11;
    const random = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const rummages = [throwsFor(random), throwsFor(random), throwsFor(random)];
    expect(new Set(rummages.map((throws) => throws[0].velocity[2].toFixed(3))).size, "each rummage throws anew").toBe(3);
    const seconds = (u) => (u * act.frames) / act.fps;
    for (const throws of rummages) {
        for (const [index, out] of act.throws.entries()) {
            const name = RUMMAGED[index];
            expect(flungAt(index, out - 0.01, throws), name).toBe(null);
            const flight = flightSeconds(throws[index], act.from);
            const down = out + (flight * act.fps) / act.frames;
            const path = Array.from({length: 41}, (_, step) => flungAt(index, out + ((down - out) * step) / 40, throws));
            // from the opening in front of it to the floor behind it
            expect(path[0].at[1], name).toBeLessThan(-1);
            expect(path.at(-1).at[1], name).toBeGreaterThan(0);
            expect(path.at(-1).at[2], name).toBeCloseTo(THROW.floor, 5);
            // a true throw: its height a parabola in time, its speed across and back steady, as gravity alone pulls on it
            for (let step = 2; step < path.length; step++) {
                const [a, b, c] = [path[step - 2], path[step - 1], path[step]].map((each) => each.at);
                const dt = seconds((down - out) / 40);
                expect((c[2] - 2 * b[2] + a[2]) / (dt * dt), `${name} ${step}: falling at gravity`).toBeCloseTo(-THROW.gravity, 3);
                expect(c[1] - b[1], `${name} ${step}: steady back`).toBeCloseTo(b[1] - a[1], 6);
            }
            const heights = path.map((each) => each.at[2]);
            expect(Math.max(...heights), `${name}: up over its head`).toBeGreaterThan(3.4);
            expect(Math.abs(path.at(-1).turn), name).toBeGreaterThan(360);
            // down, it lies on the floor and shrinks away, then is gone
            const lies = act.shrinks;
            expect(flungAt(index, down + lies / 2, throws).landed, name).toBeCloseTo(0.5, 1);
            expect(flungAt(index, down + lies / 2, throws).at[2], name).toBeCloseTo(THROW.floor, 5);
            expect(flungAt(index, down + lies + 0.001, throws), name).toBe(null);
        }
        // one after another, each pulled out before the last has landed
        for (let index = 1; index < act.throws.length; index++) {
            expect(act.throws[index]).toBeLessThan(act.throws[index - 1] + (flightSeconds(throws[index - 1], act.from) * act.fps) / act.frames);
        }
    }
    // drawn where it flies, at the size it has left, and not at all once gone
    const [out] = act.throws;
    const flying = rummagingAt("butler", out + 0.02).pose.props.get(RUMMAGED[0]);
    expect(flying).toMatchObject({bone: "root", size: 1});
});
