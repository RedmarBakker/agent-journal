import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, REACTING, SIDES, drawnPose, moveProps, propsOf} from "../src/figure/figure.js";
import {BUTLER, topHatGeometry} from "../src/figure/butler.js";
import {FRAMED} from "../src/figure/frame.js";

const {rig, stances} = JSON.parse(readFileSync("tests/figureRig.json"));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clips = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));
const top = FRAMED.middle + FRAMED.height / 2;
const outline = 0.07;
const geometry = topHatGeometry().attributes.position;
const hat = Array.from({length: geometry.count}, (_, index) => new THREE.Vector3(geometry.getX(index), -geometry.getZ(index), geometry.getY(index) + BUTLER.hat.base));

function posed(name, frame, voice, props, posture = "stand", facing = 0) {
    const {pose, turned} = drawnPose(RIG, stanceOf(voice), clips[name], frame, facing, {posture});
    const moves = pose.moves(turned);
    moveProps({propByName: props}, pose, moves);
    return {pose, moves};
}

test("the entire halo clears the camera and the Butler's actual top-hat mesh throughout its hover", () => {
    const props = propsOf();
    const halo = props.get("halo");
    let highest = -Infinity, gap = Infinity;
    for (const voice of Object.keys(stances)) {
        for (let frame = 0; frame < clips.halo.frames; frame += 0.25) {
            const {pose, moves} = posed("halo", frame, voice, props);
            halo.updateMatrixWorld(true);
            const bounds = new THREE.Box3().setFromObject(halo, true);
            highest = Math.max(highest, bounds.max.y);
            if (voice === "butler" && pose.props.get("halo").size >= 0.999) {
                const hatTop = Math.max(...hat.map((vertex) => vertex.clone().applyMatrix4(moves.get("head")).z));
                gap = Math.min(gap, bounds.min.y - hatTop);
            }
        }
    }
    expect(highest, "ring plus outline remains below the canvas ceiling").toBeLessThan(top - outline);
    expect(gap, "the fully grown halo floats above the crown rather than through it").toBeGreaterThan(0.02);
});

test("the lifted top hat remains inside the camera through its whole tip and return", () => {
    const props = propsOf();
    const held = props.get("top_hat");
    const extent = {left: Infinity, right: -Infinity, top: -Infinity};
    for (const posture of clips.hat_tip.postures) {
        for (let frame = 0; frame < clips.hat_tip.frames; frame += 0.25) {
            posed("hat_tip", frame, "butler", props, posture);
            if (!held.visible) continue;
            held.updateMatrixWorld(true);
            const box = new THREE.Box3().setFromObject(held, true);
            extent.left = Math.min(extent.left, box.min.x);
            extent.right = Math.max(extent.right, box.max.x);
            extent.top = Math.max(extent.top, box.max.y);
        }
    }
    expect(extent.left).toBeGreaterThan(-FRAMED.height / 2 + outline);
    expect(extent.right).toBeLessThan(FRAMED.height / 2 - outline);
    expect(extent.top).toBeLessThan(top - outline);
});

test("the same fingers remain attached to the hat's brim throughout its held tip", () => {
    const props = propsOf();
    const hat = props.get("top_hat");
    const side = stanceOf("butler").busy.has("r") ? "l" : "r";
    const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
    for (const posture of clips.hat_tip.postures) {
        for (let sample = 0; sample <= 40; sample++) {
            const frame = (0.3 + 0.4 * sample / 40) * (clips.hat_tip.frames - 1);
            const {pose, moves} = posed("hat_tip", frame, "butler", props, posture);
            hat.updateMatrixWorld(true);
            const brim = new THREE.Vector3(SIDES[side] * (BUTLER.hat.crown + BUTLER.hat.brim), 0, 0).applyMatrix4(hat.matrixWorld);
            const grip = pose.grip(side, [REACTING.hatFingers, 0, 0]).applyMatrix4(moves.get(`hand_${side}`)).applyMatrix4(toGlb);
            expect(brim.distanceTo(grip), `${posture} brim contact at ${frame}`).toBeLessThan(1e-7);
        }
    }
});
