// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, HAND, Posing, REACTING, TOOLS, moveProps, propsOf} from "../src/figure/figure.js";
import {BUTLER} from "../src/figure/butler.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
// what lies flat on the palm rather than in the closed fingers: the hand is anywhere under the sheet
const SHEETS = new Set(["papers", "writing_paper", "writing_tablet"]);
// it poses every frame of every clip that holds a prop for every voice, about nine seconds alone and longer beside the other tests, so it
// has a minute of its own
const POSES_EVERY_FRAME = 60_000;

test("every prop a hand holds sits in that hand, in every frame of every clip that holds it, for every voice", () => {
    const held = new Set();
    const props = propsOf();
    const toGlb = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
    for (const voice of Object.keys(stances)) {
        for (const clip of CLIPS.filter((each) => !each.voices || each.voices.includes(voice))) {
            for (const posture of clip.postures ?? ["stand"]) {
                const steps = clip.frames * 2;
                for (let step = 0; step <= steps; step++) {
                    const pose = new Posing(RIG, posture, 0);
                    clip.pose(pose, stanceOf(voice), step / steps);
                    const moves = pose.moves(0);
                    for (const [name, prop] of pose.props) {
                        if (!prop.bone.startsWith("hand_")) continue;
                        held.add(name);
                        if (name === "top_hat") {
                            // The wide hat is held at its curled brim; its model origin is at the center of the crown.
                            const side = prop.bone.slice(-1), angle = THREE.MathUtils.degToRad(REACTING.hatGripAngle);
                            const radius = BUTLER.hat.crown + BUTLER.hat.brim;
                            const contact = new THREE.Vector3((side === "r" ? -1 : 1) * radius * Math.cos(angle), BUTLER.hat.curl * Math.cos(angle) ** 2 + BUTLER.hat.thick / 2, radius * Math.sin(angle));
                            moveProps({propByName: props}, pose, moves);
                            const hat = props.get(name);
                            hat.updateMatrixWorld(true);
                            const fingers = pose.grip(side, [REACTING.hatFingers, 0, 0]).applyMatrix4(moves.get(prop.bone)).applyMatrix4(toGlb);
                            expect(contact.applyMatrix4(hat.matrixWorld).distanceTo(fingers), `${voice} ${clip.name} ${posture} ${step} brim contact`).toBeLessThan(1e-5);
                            continue;
                        }
                        const grip = pose.grip(prop.bone.slice(-1), [0, 0, 0]).applyMatrix4(moves.get(prop.bone));
                        const reach = SHEETS.has(name) ? TOOLS.paper.width / 2 : HAND.grip;
                        expect(prop.at.clone().applyMatrix4(moves.get(prop.bone)).distanceTo(grip), `${voice} ${clip.name} ${posture} ${step} ${name}`).toBeLessThanOrEqual(reach);
                    }
                }
            }
        }
    }
    expect([...held]).toEqual(expect.arrayContaining(["magnifying_glass", "writing_pen", "hand_whistle", "work_hammer"]));
}, POSES_EVERY_FRAME);
