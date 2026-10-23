// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {describe, expect, it} from "vitest";
import {CLIPS, GLASS, INSPECTING, Posing, boxSeen} from "../src/figure/figure.js";
import {INSPECT, PARCEL} from "../src/figure/parcels.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clip = CLIPS.find((each) => each.name === "inspect");
// the picture is FRAMED_HEIGHT units high at the chat's 112 pixels
const PIXELS_A_UNIT = 112 / 5.4;

// the inspection posed at `t` of its loop for `voice`: where its eyes are, where the glass's lens is, and the glass as it is held
function inspecting(t, voice = "butler") {
    const pose = new Posing(RIG, "stand", 0);
    const stance = stanceOf(voice);
    clip.pose(pose, stance, t);
    const moves = pose.moves(0);
    const glass = pose.props.get("magnifying_glass");
    const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
    if (!glass) return {eyes, glass: null};
    const grip = glass.at.clone().applyMatrix4(moves.get(glass.bone));
    const roll = THREE.MathUtils.degToRad(glass.turn.y);
    const lens = grip.clone().add(new THREE.Vector3(Math.sin(roll), 0, Math.cos(roll)).multiplyScalar((GLASS.handle / 2 + GLASS.radius) * glass.size));
    return {eyes, glass, lens, box: boxSeen(stance.busy.has("r") ? 1 : -1)};
}

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
        expect(Math.max(...across) - Math.min(...across), "it sweeps along the box").toBeGreaterThan(INSPECTING.sweep);
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
});
