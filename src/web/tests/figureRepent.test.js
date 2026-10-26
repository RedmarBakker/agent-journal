// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, CRUCIFIX, Posing, bodyTurnFor, crucifixOf, lookToward} = await import("../src/figure/figure.js");
const {ACTS} = await import("../src/figure/acts.js");
const {HEAD, LOOKS, headBlend} = await import("../src/figure/looks.js");
const {admiringLook} = await import("../src/figure/admire.js");
const {playsSeated} = await import("../src/figure/perches.js");
const {turnStep} = await import("../src/figure/places.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "repent");
const act = ACTS.repent;
const VOICES = Object.keys(stances);

function posed(u, voice) {
    const pose = new Posing(RIG, "stand", 0);
    clip.pose(pose, stanceOf(voice), u);
    const moves = pose.moves(0);
    return {pose, at: (bone) => RIG.heads.get(bone).clone().applyMatrix4(moves.get(bone))};
}

test("the confession stands first, then drops onto both knees", () => {
    for (const voice of VOICES) {
        const standing = posed((act.stand[0] + act.stand[1]) / 2, voice);
        const kneeling = posed((act.kneel[1] + act.out[1]) / 2, voice);
        expect(standing.at("root").z, `${voice} stands`).toBeGreaterThan(-0.05);
        expect(kneeling.at("root").z, `${voice} down`).toBeLessThan(-0.5);
        // both feet end up behind the shins, both knees on the floor
        for (const side of ["l", "r"]) {
            expect(kneeling.at(`foot_${side}`).y - kneeling.at(`shin_${side}`).y, `${voice} ${side} knee down`).toBeGreaterThan(0.3);
            expect(standing.at(`foot_${side}`).y - standing.at(`shin_${side}`).y, `${voice} ${side} standing`).toBeLessThan(0.1);
        }
        let last = 0;
        for (let u = act.stand[0]; u <= act.kneel[1]; u += 0.01) {
            const z = posed(u, voice).at("root").z;
            expect(z, `${voice} goes down and never up before it kneels`).toBeLessThanOrEqual(last + 1e-6);
            last = z;
        }
    }
});

test("from a seat the figure is drawn standing for it at once, never waiting out its stay, and stands before it kneels", () => {
    expect(clip.postures, "no seated posture, so a seated figure stands up for it").toEqual(["stand"]);
    const perched = {seated: true, until: 1000};
    expect(playsSeated(clip, "sit", perched, 10), "it does not wait for the seat's stay").toBe(true);
    const standing = CLIPS.find((each) => each.name === "bug_shot");
    expect(standing.postures, "an ordinary act that only stands").not.toContain("sit");
    expect(playsSeated(standing, "sit", perched, 10), "an ordinary standing act still waits").toBe(false);
    expect(turnStep({posture: "sit", facing: 0}, {posture: "stand", facing: 0})).toEqual({posture: "stand", facing: 0});
    expect(act.stand[1], "it holds standing before it kneels").toBeLessThanOrEqual(act.kneel[0]);
    expect(act.stand[1] - act.stand[0]).toBeGreaterThan(0);
});

test("the confession keeps its bowed head while remaining aware of the sin's mark", () => {
    expect(LOOKS.confession).toBeGreaterThan(LOOKS.picture);
    expect(headBlend({kind: "confession"}, clip), "the external gaze leaves the remorseful bow readable").toBeLessThan(0.2);
    expect(clip.head).toBe(HEAD.holds);
    const box = {left: 100, top: 50, width: 40, height: 20, right: 140, bottom: 70};
    expect(admiringLook(box)).toMatchObject({faces: true, behind: true, mood: "admiring"});
    const turned = (x) => {
        const pose = new Posing(RIG, "stand", 0);
        CLIPS.find((each) => each.name === "idle").pose(pose, stanceOf(VOICES[0]), 0);
        return lookToward(pose, {x, y: 0.3, faces: true, behind: true, mood: "admiring"}, 0);
    };
    expect(turned(0.05) * turned(0.95), "a mark on the left and one on the right turn it opposite ways").toBeLessThan(0);
    const body = (x, most) => {
        const pose = new Posing(RIG, "stand", 0);
        CLIPS.find((each) => each.name === "idle").pose(pose, stanceOf(VOICES[0]), 0);
        return bodyTurnFor("stand", lookToward(pose, {x, y: 0.3, faces: true, behind: true, mood: "admiring", most}, 0), most);
    };
    expect(Math.abs(body(-2, undefined)), "turned all the way round to what it admires").toBeGreaterThan(60);
    expect(Math.abs(body(-2, 45)), "three-quarter to the mark it confesses to").toBeLessThanOrEqual(45);
    expect(Math.abs(body(3, 45))).toBeLessThanOrEqual(45);
});

test("the token stays within the clasp and below the bowed face", () => {
    expect(CRUCIFIX.long, "the token supports the body acting").toBeLessThan(0.9);
    const root = new THREE.Group();
    crucifixOf(root);
    root.updateMatrixWorld(true);
    // built in the pose's own axes, turned upright by poseSpace: the upright runs along y here, the crossbar along x
    const size = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    expect(size.y, "its upright").toBeGreaterThanOrEqual(CRUCIFIX.long - 1e-3);
    expect(size.x, "its crossbar").toBeGreaterThanOrEqual(CRUCIFIX.across - 1e-3);
    for (const voice of VOICES) {
        const {pose, at} = posed((act.hold[0] + act.hold[1]) / 2, voice);
        expect(pose.props.get("crucifix"), voice).toMatchObject({bone: "hand_r"});
        expect(at("hand_l").distanceTo(at("hand_r")), `${voice} both hands on the cross`).toBeLessThan(1);
        expect(at("hand_l").z, `${voice} the left hand above the right`).toBeGreaterThanOrEqual(at("hand_r").z - 0.01);
        const grips = ["l", "r"].map((side) => pose.grip(side, [0, 0, 0]).applyMatrix4(pose.matrix(`hand_${side}`)));
        expect(grips[0].distanceTo(grips[1]), `${voice} fingers meet in the clasp`).toBeLessThan(0.16);
        expect(grips[1].z + CRUCIFIX.long * 0.7, `${voice} the cross stays below the face`).toBeLessThan(at("head").z + 0.3);
    }
});


test("kneeling carries the torso down and bows the head instead of leaving the shoulders standing", () => {
    for (const voice of VOICES) {
        const standing = posed(0, voice);
        const {pose, at} = posed(0.6, voice);
        expect(at("chest").z, `${voice} chest descends with the hips`).toBeLessThan(standing.at("chest").z - 0.6);
        expect(at("head").z, `${voice} head follows the weighted descent`).toBeLessThan(standing.at("head").z - 0.65);
        expect(new THREE.Vector3(0, -1, 0).transformDirection(pose.matrix("head")).z, `${voice} looks down`).toBeLessThan(-0.55);
        for (const side of ["l", "r"]) {
            expect(at(`shin_${side}`).z, `${voice} knee clears the floor`).toBeGreaterThan(0.09);
            expect(at(`shin_${side}`).z, `${voice} knee rests near the floor`).toBeLessThan(0.25);
        }
    }
});

test("the held confession breathes quietly and finishes with both feet and empty hands back at rest", () => {
    for (const voice of VOICES) {
        const first = posed(0, voice);
        const last = posed((clip.frames - 1) / clip.frames, voice);
        for (const bone of ["root", "chest", "head", "foot_l", "foot_r", "hand_l", "hand_r"]) {
            expect(last.at(bone).distanceTo(first.at(bone)), `${voice} ${bone} returns without a snap`).toBeLessThan(1e-7);
        }
        expect(last.pose.props.has("crucifix"), `${voice} puts the token away`).toBe(false);
        const beforeBreath = posed(0.54, voice).at("head");
        const afterBreath = posed(0.65, voice).at("head");
        expect(beforeBreath.distanceTo(afterBreath), `${voice} the hold is alive`).toBeGreaterThan(1e-5);
        expect(beforeBreath.distanceTo(afterBreath), `${voice} breathing does not bob the body`).toBeLessThan(0.02);
    }
});
