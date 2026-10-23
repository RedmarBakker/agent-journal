// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, TELEPHONE, phoneArrival, telephoneOf} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import {PILE, choicesFor} from "../src/figure/pile.js";
import {reactionTo} from "../src/figure/reactions.js";
import {beatsAfter, withSystemCards} from "../src/domain/figureState.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const call = CLIPS.find((clip) => clip.name === "phone_call");
const act = ACTS.phone_call;

// the call posed at `u` of its way through, for `voice`
function posed(u, voice = "butler") {
    const pose = new Posing(RIG, "stand", 0);
    call.pose(pose, stanceOf(voice), (u * (call.frames - 1)) / call.frames);
    const moves = pose.moves(0);
    return {pose, moves, at: (name) => pose.head(name, moves.get(name))};
}

test("the dove act is gone, and so is the whistle and runner of a dispatch: a send-off is the telephone call alone", () => {
    for (const name of ["post_dove", "whistle_runner"]) {
        expect(CLIPS.some((clip) => clip.name === name), name).toBe(false);
        expect(ACTS[name], name).toBeUndefined();
        expect(PILE.some((entry) => entry.name === name), name).toBe(false);
    }
    expect(PILE.some((entry) => entry.when.moment === "worker_sent")).toBe(false);
    expect(choicesFor({moment: "messaged"}).map((entry) => entry.name)).toEqual(["phone_call"]);
});

test("a worker's dispatch, its next job, its start again, a message sent it and a message to another session each start the call", () => {
    const card = (id, text, data) => ({table: "messages", id, author: "system", text, data, session: null, created_at: new Date((10 + id) * 1000).toISOString()});
    const messages = [
        card(1, "Worker 57, Mr. Muybridge, motion photographer: started on claude opus", {kind: "card", icon: "agents", tone: ""}),
        card(2, "Worker 57, Mr. Muybridge, motion photographer: sent its next job", {kind: "card", icon: "agents", tone: ""}),
        card(3, "Worker 57, Mr. Muybridge, motion photographer: started again in its last session", {kind: "card", icon: "agents", tone: ""}),
        card(4, "Worker 57, Mr. Muybridge, motion photographer: sent a message in its session", {kind: "card", icon: "agents", tone: ""}),
        card(5, "From the main agent, about the output", {kind: "peer", sent_to: "45-mr-faraday", address: "45-mr-faraday"}),
        // a worker's own standing is no send-off
        card(6, "Worker 57, Mr. Muybridge, motion photographer: merged", {kind: "card", icon: "agents", tone: ""}),
    ];
    const beats = beatsAfter(withSystemCards({session: "s", data: {}}, messages), 0);
    expect(beats.map((fire) => [fire.beat, fire.card])).toEqual([1, 2, 3, 4, 5].map((id) => ["messaged", `messages:${id}`]));
    // every one of them calls, whatever the roll, but not twice in one burst
    for (const roll of [0, 0.5, 0.99]) expect(reactionTo("messaged", new Map(), 1000, () => roll).clip).toBe("phone_call");
    const memory = new Map();
    reactionTo("messaged", memory, 1000, () => 0);
    expect(reactionTo("messaged", memory, 1010, () => 0)).toBe(null);
});

test("the call goes in order: the telephone appears, the handset comes up to the ear, the dial turns and springs back, it talks, the handset goes down, the telephone goes", () => {
    const order = [act.poof, act.drop, act.settle, act.reach, act.lift, act.finger, act.dial, act.back, act.talk, act.hang, act.goes];
    for (let index = 1; index < order.length; index++) expect(order[index][0], `${index}`).toBeGreaterThanOrEqual(order[index - 1][0]);
    expect(act.back[0]).toBe(act.dial[1]);
    for (const voice of Object.keys(stances)) {
        const side = stanceOf(voice).busy.has("r") ? "l" : "r";
        const steps = Array.from({length: 97}, (_, index) => ({u: index / 96, ...posed(index / 96, voice)}));
        const prop = (step, name) => step.pose.props.get(name);
        // it is there from the first frame and gone at the end
        expect(prop(steps[0], "telephone"), voice).toBeTruthy();
        expect(prop(steps.at(-1), "telephone"), voice).toBeUndefined();
        expect(prop(steps.at(-1), "telephone_handset"), voice).toBeUndefined();
        // the handset on the cradle, then in the free hand from the reach to the hang, then on the cradle again
        for (const step of steps.filter((each) => phoneArrival(each.u).here)) {
            const inHand = step.u >= act.reach[1] && step.u < act.hang[1];
            expect(prop(step, "telephone_handset").bone, `${voice} ${step.u}`).toBe(inHand ? `hand_${side}` : "root");
        }
        // up at the head while it talks, standing straight
        for (const step of steps.filter((each) => each.u > act.talk[0] && each.u < act.talk[1])) {
            expect(step.at(`hand_${side}`).z, `${voice} ${step.u}`).toBeGreaterThan(2.2);
            expect(step.at("root").z, `${voice} ${step.u}`).toBe(0);
        }
        // the dial turns round to its stop while the finger is in it, and springs back to rest after
        const dial = (u) => prop(steps[Math.round(u * 96)], "telephone").dial;
        expect(dial(act.dial[0] - 0.02), voice).toBe(0);
        expect(dial(act.dial[1]), voice).toBeGreaterThan(act.turn * 0.95);
        expect(dial((act.dial[0] + act.dial[1]) / 2), voice).toBeGreaterThan(0);
        expect(dial(act.back[1] + 0.02), voice).toBe(0);
        // it bends down to the telephone to take the handset, to dial and to put it back
        for (const u of [act.reach[1], (act.dial[0] + act.dial[1]) / 2, (act.hang[0] + act.hang[1]) / 2]) {
            expect(steps[Math.round(u * 96)].at("root").z, `${voice} ${u}`).toBeLessThan(-0.3);
        }
    }
});

// the telephone's props built as the figure builds them, its body at rest
function telephone() {
    const [set, handset, cord, poof] = ["telephone", "telephone_handset", "telephone_cord", "telephone_poof"].map((name) => Object.assign(new THREE.Group(), {name}));
    telephoneOf(set, handset, cord, poof);
    set.userData.shape({squash: 0, dial: 0});
    cord.userData.shape({from: new THREE.Vector3(0, 0, 0.3), to: new THREE.Vector3(0.6, -0.4, 1.2)});
    poof.userData.shape({puff: 0.5});
    set.updateMatrixWorld(true);
    return {set, handset, cord, poof};
}

test("the telephone is solid: every part has depth, is shaded light and dark as the figure is and outlined, a touch larger than true and near square", () => {
    const {set, handset, cord, poof} = telephone();
    const parts = [set, handset, cord, poof].flatMap((group) => {
        const found = [];
        group.traverse((node) => node.isMesh && node.material.side !== THREE.BackSide && found.push(node));
        return found;
    });
    expect(parts.length).toBeGreaterThan(15);
    for (const part of parts) {
        // shaded by the figure's own light into a lit side and a shaded one, never one flat colour
        expect(part.material.uniforms?.light, part.name).toBeTruthy();
        expect(part.material.uniforms?.shade, part.name).toBeTruthy();
        // outlined as the figure is
        expect(part.children.some((child) => child.isMesh && child.material.side === THREE.BackSide), part.name).toBe(true);
        // a solid with extent every way, never a flat shape
        part.geometry.computeBoundingBox();
        const extent = part.geometry.boundingBox.getSize(new THREE.Vector3());
        expect(Math.min(extent.x, extent.y, extent.z), part.name).toBeGreaterThan(0.02);
    }
    // the set alone, without its handset: its footprint near square, where the set before was half again as wide as deep (1.75 by 1.15),
    // and smaller than it was, a fifth or so of the figure's 5.4 units across, a touch more than a real one's tenth and a bit
    const body = new THREE.Box3().setFromObject(set.getObjectByName("telephone_base")).getSize(new THREE.Vector3());
    expect(body.x / body.z).toBeLessThan(1.25);
    expect(body.x / body.z).toBeLessThan(1.75 / 1.15);
    expect(body.x).toBeLessThan(1.75);
    expect(body.x / 5.4).toBeGreaterThan(0.15);
    expect(body.x / 5.4).toBeLessThan(0.26);
    expect(body.y).toBeGreaterThan(0.4);
});

test("the set has the classic desk shape: wider at the floor, its front face sloping back with the dial in it, round over the top, and the handset across the prongs with its pieces past the sides", () => {
    const {set, handset} = telephone();
    const named = (name) => set.getObjectByName(`telephone_${name}`);
    const body = named("base").geometry.attributes.position;
    const points = Array.from({length: body.count}, (_, index) => new THREE.Vector3().fromBufferAttribute(body, index));
    const {base} = TELEPHONE;
    // wider at the floor than at the top
    const across = (low, high) => Math.max(...points.filter((point) => point.y >= low && point.y <= high).map((point) => Math.abs(point.x)));
    expect(across(base.height - 0.05, base.height + 0.3)).toBeLessThan(across(-0.01, 0.05) * 0.88);
    // the front face slopes back: its foot well forward of its brow
    const forward = (low, high) => Math.max(...points.filter((point) => point.y >= low && point.y <= high).map((point) => point.z));
    expect(forward(-0.01, 0.05)).toBeGreaterThan(forward(base.brow[1] - 0.02, base.brow[1] + 0.02) + 0.2);
    // round over the top: between the brow and the top's flat, heights between the two
    expect(points.some((point) => point.y > base.brow[1] + 0.03 && point.y < base.height - 0.02 && point.z > base.brow[0] - 0.2)).toBe(true);
    // the dial set in that face, facing out of it, forward and up
    const dial = named("dial_face");
    const middle = dial.getWorldPosition(new THREE.Vector3());
    const facing = new THREE.Vector3(0, 1, 0).applyQuaternion(dial.getWorldQuaternion(new THREE.Quaternion()));
    expect(middle.z).toBeGreaterThan(base.brow[0]);
    expect(middle.y).toBeLessThan(base.brow[1]);
    expect(facing.z).toBeGreaterThan(0.4);
    expect(facing.y).toBeGreaterThan(0.4);
    // two prongs on top; the handset rests above them, longer than the top is wide, so its ear and mouth pieces hang past its sides
    for (const sign of [1, -1]) expect(named(`prong_${sign}`).position.y).toBeGreaterThan(base.height - 0.05);
    expect(TELEPHONE.handset.length / 2).toBeGreaterThan(across(base.height - 0.05, base.height + 0.3) + TELEPHONE.handset.cup[1] / 2);
    expect(handset.getObjectByName("telephone_handset_ear_piece")).toBeTruthy();
    expect(handset.getObjectByName("telephone_handset_mouth_piece")).toBeTruthy();
});

test("the handset rests on its cradle a moment before it is taken up and again after it is put down, the set standing whole", () => {
    const {set} = telephone();
    const prong = set.getObjectByName("telephone_prong_1");
    const cradle = prong.position.y + TELEPHONE.cradle.height / 2;
    for (const u of [act.settle[1] + 0.005, act.reach[0] - 0.005, act.hang[1] + 0.02, act.goes[0] - 0.01]) {
        const {pose} = posed(u);
        const resting = pose.props.get("telephone_handset");
        expect(resting.bone, `${u}`).toBe("root");
        expect(pose.props.get("telephone").squash, `${u}`).toBe(0);
        // on the cradle: the handset's middle just over the prongs' tops, the set and the handset lowered alike by any bend
        const at = pose.props.get("telephone").at;
        expect(resting.at.z - at.z - cradle, `${u}`).toBeGreaterThan(0);
        expect(resting.at.z - at.z - cradle, `${u}`).toBeLessThan(TELEPHONE.handset.grip * 2);
    }
});

test("the telephone comes whole, never growing or fading in: out of a poof a little above the floor, it drops onto it and settles with a squash and wobble, and goes in a poof", () => {
    // whole from the first frame, above the floor, in the burst of a poof
    const first = phoneArrival(0);
    expect(first).toMatchObject({here: true, squash: 0});
    expect(first.above).toBeGreaterThan(0.3);
    expect(first.puff).toBeGreaterThan(0);
    const {pose} = posed(0);
    expect(pose.props.get("telephone")).toMatchObject({squash: 0});
    expect(pose.props.get("telephone").size).toBeUndefined();
    expect(pose.props.get("telephone_poof")).toBeTruthy();
    // its body at full size as it arrives: the shape it is drawn with leaves it unscaled
    const {set} = telephone();
    set.userData.shape({squash: first.squash, dial: 0});
    expect(set.children[0].scale.toArray()).toEqual([1, 1, 1]);
    // it falls, gathering speed, onto the floor
    const heights = Array.from({length: 41}, (_, index) => phoneArrival(act.drop[0] + ((act.drop[1] - act.drop[0]) * index) / 40).above);
    for (let index = 1; index < heights.length; index++) expect(heights[index]).toBeLessThanOrEqual(heights[index - 1]);
    expect(heights[20] - heights[40]).toBeGreaterThan(heights[0] - heights[20]);
    expect(phoneArrival(act.drop[1]).above).toBe(0);
    // it lands squashed, wobbles both ways, smaller each time, and is still by the time it is reached for
    const squashes = Array.from({length: 101}, (_, index) => phoneArrival(act.settle[0] + ((act.settle[1] - act.settle[0]) * index) / 100).squash);
    expect(Math.max(...squashes)).toBeGreaterThan(0.08);
    expect(Math.min(...squashes)).toBeLessThan(-0.01);
    expect(Math.abs(squashes[80])).toBeLessThan(Math.max(...squashes) / 3);
    expect(phoneArrival(act.reach[0]).squash).toBe(0);
    expect(phoneArrival(act.reach[0]).above).toBe(0);
    // it goes in the middle of a poof at the end
    expect(phoneArrival((act.goes[0] + act.goes[1]) / 2 - 0.005).here).toBe(true);
    expect(phoneArrival((act.goes[0] + act.goes[1]) / 2 + 0.005).here).toBe(false);
    expect(phoneArrival((act.goes[0] + act.goes[1]) / 2).puff).toBeGreaterThan(0.3);
});
