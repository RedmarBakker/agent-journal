import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, LEGS, Posing} = await import("../src/figure/figure.js");
const {POSTURES} = await import("../src/figure/places.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync("tests/figureRig.json"));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// the edge a seated figure sits on, in its own units: where its picture puts the line it rests on (places.js POSTURES sit)
const EDGE = POSTURES.sit.drop * FRAMED.height;
// how far below the hips the ankles hung when the figure sat with its thighs level and its knees bent 66 degrees, which folded the shins
// up forward under it, in its own units
const FOLDED = 0.47;

// the figure seated on an edge playing `name` at `u` of it for `voice`, posed as the page draws it seated (figure.js Stage.draw)
function seated(name, u, voice) {
    const pose = new Posing(RIG, "sit", 0);
    LEGS.sit.under(pose);
    CLIPS.find((each) => each.name === name).pose(pose, stanceOf(voice), u);
    LEGS.sit.over(pose);
    const moves = pose.moves(0);
    return (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone));
}

test("sitting on an edge, the thighs slope a little down over it and the shins hang straight down past it, the feet lower than when folded", () => {
    for (const voice of Object.keys(stances)) {
        for (const name of ["idle", "ledge_sit", "doze"]) {
            for (const u of [0, 0.25, 0.5, 0.75]) {
                const at = seated(name, u, voice);
                const label = `${voice} ${name} ${u}`;
                for (const side of ["l", "r"]) {
                    const [hip, knee, ankle] = [at(`thigh_${side}`), at(`shin_${side}`), at(`foot_${side}`)];
                    // the thigh out forward over the edge, sloping down to the knee, never folded up
                    const slope = (Math.atan2(hip.z - knee.z, hip.y - knee.y) * 180) / Math.PI;
                    expect(slope, `${label} ${side} thigh slopes down`).toBeGreaterThan(10);
                    expect(slope, `${label} ${side} thigh out forward`).toBeLessThan(40);
                    // the shin hangs within a few degrees of straight down, seen from the side
                    const lean = (Math.atan2(ankle.y - knee.y, knee.z - ankle.z) * 180) / Math.PI;
                    expect(Math.abs(lean), `${label} ${side} shin hangs straight`).toBeLessThan(15);
                    // the feet lower than they hung folded, and well below the edge it sits on
                    expect(hip.z - ankle.z, `${label} ${side} lower than folded`).toBeGreaterThan(FOLDED + 0.15);
                    expect(ankle.z, `${label} ${side} feet below the edge`).toBeLessThan(EDGE - 0.5);
                }
            }
        }
    }
});
