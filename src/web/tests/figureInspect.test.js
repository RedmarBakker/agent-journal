// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {describe, expect, it} from "vitest";
import {CLIPS, GLASS, INSPECTING, Posing, SEARCHING, boxSeen} from "../src/figure/figure.js";
import {INSPECT, PARCEL} from "../src/figure/parcels.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "inspect");
const searchClip = CLIPS.find((each) => each.name === "search");
const radians = THREE.MathUtils.degToRad;
const VIEWER = new THREE.Vector3(0, -1, 0);
// the picture is FRAMED_HEIGHT units high at the chat's 112 pixels
const PIXELS_A_UNIT = 112 / 5.4;

// `clip` posed at `t` for `voice`: where its eyes are, the glass as it is held, the middle of its lens and the way its lens faces, placed
// as the figure's renderer places it (heldPropOf), the handle along the glass's up and the lens facing the viewer before it is turned
function posed(clip, t, voice) {
    const pose = new Posing(RIG, "stand", 0);
    const stance = stanceOf(voice);
    clip.pose(pose, stance, t);
    const moves = pose.moves(0);
    const glass = pose.props.get("magnifying_glass");
    const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
    if (!glass) return {stance, eyes, glass: null};
    const turned = new THREE.Matrix4().extractRotation(moves.get(glass.frame))
        .multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(glass.turn.x), radians(glass.turn.y), radians(glass.turn.z), "ZYX")));
    const up = new THREE.Vector3(0, 0, 1).transformDirection(turned);
    const lens = glass.at.clone().applyMatrix4(moves.get(glass.bone)).addScaledVector(up, (GLASS.handle / 2 + GLASS.radius) * glass.size);
    return {stance, eyes, glass, lens, faces: VIEWER.clone().transformDirection(turned)};
}

// the inspection posed at `t` of its loop for `voice`, with the top of the box it inspects
function inspecting(t, voice = "butler") {
    const held = posed(clip, t, voice);
    return {...held, box: boxSeen(held.stance.busy.has("r") ? 1 : -1)};
}

// how far the lens is turned from facing the viewer, in degrees: 0 seen face-on as a round disc, 90 seen edge-on
const slantOf = (faces) => THREE.MathUtils.radToDeg(Math.acos(Math.abs(faces.dot(VIEWER))));

describe("inspecting a box with the magnifying glass", () => {
    it("holds the glass between its eyes and the box as the viewer sees them, all the while it looks, for every voice", () => {
        const {along, pause} = INSPECTING;
        for (const voice of Object.keys(stances)) {
            for (let step = 0; step <= 10; step++) {
                const t = along[0] + (step / 10) * (pause[1] - along[0]);
                const {eyes, lens, box, glass} = inspecting(t, voice);
                expect(glass, `${voice} ${t}`).not.toBe(null);
                const [from, to, at] = [eyes, box, lens].map((point) => new THREE.Vector2(point.x, point.z));
                const line = to.clone().sub(from);
                const share = at.clone().sub(from).dot(line) / line.lengthSq();
                const off = at.clone().sub(from.clone().add(line.clone().multiplyScalar(share))).length();
                expect(share, `${voice} ${t}: past the eyes, short of the box`).toBeGreaterThan(0.3);
                expect(share, `${voice} ${t}`).toBeLessThan(1);
                expect(off, `${voice} ${t}: on the line from the eyes to the box`).toBeLessThan(GLASS.radius * glass.size);
                expect(lens.y, `${voice} ${t}: before the figure, toward the viewer`).toBeLessThan(-0.5);
                expect(glass.magnifies, `${voice} ${t}: showing the box magnified`).toBeGreaterThan(0.5);
            }
        }
    });

    it("draws the glass large enough to read at the figure's size, sweeps it slowly along the box, and pauses with a nod before putting it away", () => {
        const lensPixels = 2 * GLASS.radius * INSPECTING.size * PIXELS_A_UNIT;
        expect(lensPixels, "the lens wider than the box it looks at").toBeGreaterThan(PARCEL.width);
        const across = Array.from({length: 20}, (_, step) => inspecting(INSPECTING.along[0] + (step / 20) * (INSPECTING.along[1] - INSPECTING.along[0])).lens.x);
        expect(Math.max(...across) - Math.min(...across), "it sweeps along the box, a fifth of its lens's width or more").toBeGreaterThan((2 * GLASS.radius * INSPECTING.size) / 5);
        const seconds = (INSPECTING.along[1] - INSPECTING.along[0]) * (clip.frames / clip.fps);
        expect(seconds, "slowly").toBeGreaterThan(1);
        expect(clip.frames / clip.fps * 1000, "its whole play fits the inspection's time").toBeLessThanOrEqual(INSPECT.ms);
        const head = (t) => {
            const pose = new Posing(RIG, "stand", 0);
            clip.pose(pose, stanceOf("butler"), t);
            return new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(0).get("head")).z;
        };
        expect(head((INSPECTING.pause[0] + INSPECTING.pause[1]) / 2), "a nod deeper in the pause").toBeLessThan(head(INSPECTING.along[0]));
        expect(inspecting(0).glass, "put away as it ends and begins").toBe(null);
    });

    it("holds the glass slanted, its rim skewed from the viewer so it reads as a magnifying glass and never as a flat disc or an edge", () => {
        for (const voice of Object.keys(stances)) {
            for (let step = 0; step <= 10; step++) {
                const t = INSPECTING.along[0] + (step / 10) * (INSPECTING.pause[1] - INSPECTING.along[0]);
                const {faces} = inspecting(t, voice);
                expect(slantOf(faces), `${voice} ${t}: skewed from the viewer`).toBeGreaterThan(40);
                expect(slantOf(faces), `${voice} ${t}: its lens still seen`).toBeLessThan(70);
            }
        }
    });
});

describe("searching the ground with the magnifying glass", () => {
    it("bows over the floor with the glass held before its eyes, on its line of sight to the floor ahead, the floor magnified behind the lens as it sweeps along", () => {
        for (const voice of Object.keys(stances)) {
            const across = [];
            for (let step = 0; step < 20; step++) {
                const t = step / 20;
                const {eyes, glass, lens, faces} = posed(searchClip, t, voice);
                expect(glass, `${voice} ${t}`).toMatchObject({shows: "ground", size: SEARCHING.size});
                expect(glass.magnifies, `${voice} ${t}`).toBeGreaterThan(0.5);
                // the line from the eyes through the lens comes down on the floor just ahead of the figure: the lens is before its eyes
                const sight = lens.clone().sub(eyes);
                expect(sight.z, `${voice} ${t}: below the eyes`).toBeLessThan(-0.2);
                expect(sight.length(), `${voice} ${t}: close before the eyes`).toBeLessThan(1.4);
                const floor = eyes.clone().addScaledVector(sight, -eyes.z / sight.z);
                const reach = Math.hypot(floor.x, floor.y);
                expect(reach, `${voice} ${t}: looking at the floor ahead of its feet`).toBeGreaterThan(0.5);
                expect(reach, `${voice} ${t}: near the figure`).toBeLessThan(3);
                expect(faces.z, `${voice} ${t}: the lens facing down at the ground`).toBeLessThan(-0.5);
                expect(slantOf(faces), `${voice} ${t}: skewed from the viewer`).toBeGreaterThan(40);
                expect(slantOf(faces), `${voice} ${t}: its lens still seen`).toBeLessThan(80);
                across.push(lens.clone().setZ(0));
            }
            const spread = Math.max(...across.flatMap((a) => across.map((b) => a.distanceTo(b))));
            expect(spread, `${voice}: it sweeps the glass along the floor`).toBeGreaterThan(0.25);
        }
    });

    it("shows the box behind the lens while it inspects the box, and the ground while it searches", () => {
        expect(inspecting((INSPECTING.along[0] + INSPECTING.along[1]) / 2).glass.shows).toBe("box");
        expect(posed(searchClip, 0.5, "butler").glass.shows).toBe("ground");
    });
});
