import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, LEGS, Posing} = await import("../src/figure/figure.js");
const {POSTURES, bodyAcross} = await import("../src/figure/places.js");
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

// how thick the legs are about their bones, as every voice's model has them, in the figure's units
const LEG = 0.28;

// the figure seated on an edge playing `name` at `u` of it for `voice`, turned `facing` degrees, posed as the page draws it seated
// (figure.js Stage.draw)
function seated(name, u, voice, facing = 0) {
    const pose = new Posing(RIG, "sit", 0);
    LEGS.sit.under(pose);
    CLIPS.find((each) => each.name === name).pose(pose, stanceOf(voice), u);
    LEGS.sit.over(pose);
    const moves = pose.moves(facing);
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

test("seated turned along an edge, as at either corner, its legs stay inside the body box it is kept inside the pane by", () => {
    for (const facing of [60, 70, 290, 300]) {
        const across = bodyAcross({posture: "sit", face: facing});
        for (const voice of Object.keys(stances)) {
            for (const name of ["idle", "ledge_sit", "doze", "type"]) {
                for (const u of [0, 0.25, 0.5, 0.75]) {
                    const at = seated(name, u, voice, facing);
                    for (const bone of ["shin_l", "shin_r", "foot_l", "foot_r"]) {
                        // across the picture, which frames FRAMED.height of the figure's units about its middle, the leg's thickness counted
                        const x = at(bone).x;
                        const label = `${voice} ${name} ${u} turned ${facing} ${bone}`;
                        expect(0.5 + (x + LEG) / FRAMED.height, label).toBeLessThanOrEqual(across.right);
                        expect(0.5 + (x - LEG) / FRAMED.height, label).toBeGreaterThanOrEqual(across.left);
                    }
                }
            }
        }
    }
});

test("seated facing the viewer, the thighs show on screen at least half their standing length, the knees forward of the hips and apart", () => {
    // the length of a thigh as the viewer sees it, the camera looking along the figure's forward line: across and up the picture alone
    const shown = (hip, knee) => Math.hypot(knee.x - hip.x, knee.z - hip.z);
    for (const voice of Object.keys(stances)) {
        for (const name of ["idle", "ledge_sit", "doze"]) {
            for (const u of [0, 0.25, 0.5, 0.75]) {
                for (const facing of [0, 15, 345]) {
                    const at = seated(name, u, voice, facing);
                    const label = `${voice} ${name} ${u} turned ${facing}`;
                    const shares = ["l", "r"].map((side) => {
                        const standing = RIG.heads.get(`thigh_${side}`).distanceTo(RIG.heads.get(`shin_${side}`));
                        const [hip, knee] = [at(`thigh_${side}`), at(`shin_${side}`)];
                        expect(hip.y - knee.y, `${label} ${side} knee in front of the hip`).toBeGreaterThan(0.2);
                        return shown(hip, knee) / standing;
                    });
                    // square to the viewer each thigh shows half its length or more; turned a little, the thigh turned toward the viewer
                    // shows less and the other more, so the two together still do
                    if (facing === 0) for (const share of shares) expect(share, `${label} thigh shown`).toBeGreaterThanOrEqual(0.5);
                    expect((shares[0] + shares[1]) / 2, `${label} thighs shown`).toBeGreaterThanOrEqual(0.5);
                    expect(Math.abs(at("shin_l").x - at("shin_r").x), `${label} knees apart`).toBeGreaterThan(Math.abs(at("thigh_l").x - at("thigh_r").x));
                }
            }
        }
    }
});
