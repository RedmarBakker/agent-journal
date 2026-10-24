// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, TELEPHONE, phoneArrival, telephoneOf} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import {PILE, choicesFor} from "../src/figure/pile.js";
import {reactionTo} from "../src/figure/reactions.js";
import {beatsAfter, withSystemCards} from "../src/domain/figureState.js";
import {callStretch} from "../src/figure/places.js";

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

test("only an agent given work starts the call: a worker's dispatch and its next job, never its start again, a message sent it or a message to another session", () => {
    const card = (id, text, data) => ({table: "messages", id, author: "system", text, data, session: null, created_at: new Date((10 + id) * 1000).toISOString()});
    const messages = [
        card(1, "Worker 57, Mr. Muybridge, motion photographer: started on claude opus", {kind: "card", icon: "agents", tone: "", row: "workers:57", task: 2742, card_type: "process", process: "worker", active: true}),
        card(2, "Worker 57, Mr. Muybridge, motion photographer: sent its next job", {kind: "card", icon: "agents", tone: "", row: "workers:57", task: 2743}),
        card(3, "Worker 57, Mr. Muybridge, motion photographer: started again in its last session", {kind: "card", icon: "agents", tone: ""}),
        card(4, "Worker 57, Mr. Muybridge, motion photographer: sent a message in its session", {kind: "card", icon: "agents", tone: ""}),
        card(5, "From the main agent, about the output", {kind: "peer", sent_to: "45-mr-faraday", address: "45-mr-faraday"}),
        // a worker's own standing is no send-off
        card(6, "Worker 57, Mr. Muybridge, motion photographer: merged", {kind: "card", icon: "agents", tone: ""}),
    ];
    const beats = beatsAfter(withSystemCards({session: "s", data: {}}, messages), 0);
    expect(beats.map((fire) => [fire.beat, fire.card])).toEqual([1, 2].map((id) => ["messaged", `messages:${id}`]));
    // every one of them calls, whatever the roll, but not twice in one burst
    for (const roll of [0, 0.5, 0.99]) expect(reactionTo("messaged", new Map(), 1000, () => roll).clip).toBe("phone_call");
    const memory = new Map();
    reactionTo("messaged", memory, 1000, () => 0);
    expect(reactionTo("messaged", memory, 1010, () => 0)).toBe(null);
    expect(reactionTo("messaged", memory, 1060, () => 0), "a minute later the telephone stays away").toBe(null);
    expect(reactionTo("messaged", memory, 1100, () => 0), "past ninety seconds it still stays away").toBe(null);
    expect(reactionTo("messaged", memory, 1120, () => 0).clip, "after two minutes it rings again").toBe("phone_call");
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
    const dial = named("dial_plate");
    const middle = dial.getWorldPosition(new THREE.Vector3());
    const facing = new THREE.Vector3(0, 1, 0).applyQuaternion(dial.getWorldQuaternion(new THREE.Quaternion()));
    expect(middle.z).toBeGreaterThan(base.brow[0]);
    expect(middle.y).toBeLessThan(base.brow[1]);
    expect(facing.z).toBeGreaterThan(0.4);
    expect(facing.y).toBeGreaterThan(0.3);
    // two prongs on top; the handset rests above them, longer than the top is wide, so its ear and mouth pieces hang past its sides
    for (const sign of [1, -1]) expect(named(`prong_${sign}`).position.y).toBeGreaterThan(base.height - 0.05);
    expect(TELEPHONE.handset.length / 2).toBeGreaterThan(across(base.height - 0.05, base.height + 0.3) + TELEPHONE.handset.end[0] / 2);
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
    expect(pose.props.get("telephone").size).toBe(1);
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

test("the hand holds the handset from behind: its palm at the back of the grip, the grip between the hand and the head at the ear, and under the palm as it comes off the cradle", () => {
    for (const voice of Object.keys(stances)) {
        const side = stanceOf(voice).busy.has("r") ? "l" : "r";
        let checked = 0;
        for (let index = 0; index <= 200; index++) {
            const u = index / 200;
            const {pose, moves, at} = posed(u, voice);
            const held = pose.props.get("telephone_handset");
            if (held?.bone !== `hand_${side}`) continue;
            checked++;
            const grip = held.at.clone().applyMatrix4(moves.get(held.bone));
            const palm = pose.grip(side, [0, 0, 0]).applyMatrix4(moves.get(`hand_${side}`));
            const head = at("head").add(new THREE.Vector3(0, 0, 0.8));
            const label = `${voice} ${u}`;
            // the grip a palm's depth from the palm
            expect(grip.distanceTo(palm), label).toBeGreaterThan(0.1);
            if (u > act.lift[1] && u < act.hang[0]) {
                // at the ear: the grip between the hand and the head, the palm on its far side
                expect(grip.distanceTo(head), label).toBeLessThan(palm.distanceTo(head) - 0.1);
                expect(Math.sign(palm.x - grip.x), label).toBe(Math.sign(palm.x - head.x));
            }
            // just off the cradle: the grip under the palm
            if (u < act.lift[0] + 0.01) expect(grip.z, label).toBeLessThan(palm.z - 0.1);
        }
        expect(checked, voice).toBeGreaterThan(50);
    }
});

test("on the telephone it says whom it calls: the worker and the task it holds, or the session messaged, in a bubble while it talks and until the handset is down", async () => {
    const {callLines} = await import("../src/domain/figureState.js");
    const {answerTo} = await import("../src/figure/reactions.js");
    const {bubbleSpot, callSays, handsetSide, tailEnd} = await import("../src/figure/places.js");
    // the call's beat keeps the mark that set it off
    const answer = answerTo({beat: "messaged", time: 1, card: "messages:5"}, "butler", {reacted: new Map(), played: []}, 1000, () => 0, () => true);
    expect(answer.beat).toMatchObject({clip: "phone_call", mark: "messages:5"});
    // a worker given work: two sentences only, its number, then the task its mark gave it, called out, never its title
    expect(callLines([{row: "workers:57", task: 2742}])).toEqual(["Worker 57", "Task 2742!"]);
    // a mark that names no task says nothing, nor does any other mark: no worker is named without a task
    expect(callLines([{row: "workers:58", task: 0}])).toEqual([]);
    expect(callLines([{row: "workers:58", task: 0}, {row: "workers:57", task: 2742}])).toEqual(["Worker 57", "Task 2742!"]);
    expect(callLines([{row: "tasks:3", task: 0}])).toEqual([]);
    // said from the talk's start until the handset is down, never before or after
    expect(callSays(act.talk[0] - 0.01)).toBe(false);
    for (const u of [act.talk[0], (act.talk[0] + act.talk[1]) / 2, act.hang[0], act.hang[1] - 0.001]) expect(callSays(u), `${u}`).toBe(true);
    expect(callSays(act.hang[1])).toBe(false);
    // the bubble stands up beside the head, on the side where it hides fewer of the chat's words, else toward the more room
    const head = {x: 500, y: 400};
    const text = {left: 520, right: 800, top: 300, bottom: 400};
    const hides = (box) => (box.left < text.right && text.left < box.right && box.top < text.bottom && text.top < box.bottom ? 5 : 0);
    const spot = bubbleSpot(head, 120, 40, {left: 100, right: 600}, hides);
    expect(spot.side).toBe(-1);
    expect(spot.right).toBeLessThan(head.x);
    expect(spot.bottom).toBeLessThan(head.y);
    expect(bubbleSpot(head, 120, 40, {left: 100, right: 600}, () => 0).side).toBe(1);
    expect(bubbleSpot(head, 120, 40, {left: 600, right: 100}, () => 0).side).toBe(-1);
    // hiding no more words either way, on the handset's side so its tail is short, unless the page has no room for it there
    for (const way of [1, -1]) {
        const handset = {x: head.x + way * 20, y: head.y + 10};
        expect(bubbleSpot(head, 120, 40, handsetSide(head, handset, 120, 1000), () => 0).side, `${way}`).toBe(way);
    }
    expect(bubbleSpot(head, 120, 40, handsetSide(head, {x: head.x + 20, y: head.y}, 120, 1000), hides).side).toBe(-1);
    expect(bubbleSpot({x: 60, y: 400}, 120, 40, handsetSide({x: 60, y: 400}, {x: 40, y: 410}, 120, 1000), () => 0).side).toBe(1);
    // its tail ends at the handset on its side, else at the head's edge on its own side, never across the face
    expect(tailEnd(head, {x: 520, y: 410}, 1, 112)).toEqual({x: 520, y: 410});
    const short = tailEnd(head, {x: 480, y: 410}, 1, 112);
    expect(short.x).toBeGreaterThan(head.x);
    expect(short.y).toBe(head.y);
});

test("drawn after the reference picture: a large cream dial plate fills most of the sloped front, with the dark wheel, its white holes, the marks round it and the label, and the handset has round ends", () => {
    const {set, handset} = telephone();
    const named = (group, name) => group.getObjectByName(`${group.name}_${name}`);
    const size = (mesh) => new THREE.Box3().setFromObject(mesh).getSize(new THREE.Vector3());
    const body = size(named(set, "base"));
    // the plate, cream, round and most of the body's width, the wheel on it a dark disc inside its rim
    const plate = named(set, "dial_plate");
    const wheel = named(set, "dial_wheel");
    expect(plate.geometry.parameters.radiusTop * 2).toBeGreaterThan(body.x * 0.6);
    expect(wheel.geometry.parameters.radiusTop).toBeLessThan(plate.geometry.parameters.radiusTop);
    const colour = (mesh) => mesh.material.uniforms.colour.value;
    expect(colour(plate).x + colour(plate).y + colour(plate).z).toBeGreaterThan(2.2);
    expect(colour(wheel).x + colour(wheel).y + colour(wheel).z).toBeLessThan(0.5);
    // the ten finger holes light on the dark wheel, a mark for each number round them on the plate, and the label in the middle
    for (let index = 0; index < TELEPHONE.dial.holes; index++) {
        expect(colour(named(set, `hole_${index}`)).x, `${index}`).toBeGreaterThan(0.8);
        expect(named(set, `number_${index}`), `${index}`).toBeTruthy();
    }
    expect(named(set, "dial_label")).toBeTruthy();
    // the handset's ends, round bulbs wider than its handle, the same across as front to back
    const handle = TELEPHONE.handset.grip * 2;
    for (const end of ["ear", "mouth"]) {
        const bulb = named(handset, `${end}_piece`);
        expect(bulb.geometry.type, end).toBe("SphereGeometry");
        const extent = size(bulb);
        expect(extent.x, end).toBeGreaterThan(handle * 1.8);
        expect(Math.abs(extent.x - extent.z), end).toBeLessThan(0.01);
    }
});

test("the talk held longer plays round without a jump: the figure stands at the talk's end as it stood at its start, so the talk starts again where it ended", () => {
    const call = CLIPS.find((clip) => clip.name === "phone_call");
    const {from, to} = callStretch(30);
    for (const voice of Object.keys(stances)) {
        const [start, end] = [from, to].map((frame) => {
            const pose = new Posing(RIG, "stand", 0);
            call.pose(pose, stanceOf(voice), frame / call.frames);
            return pose.moves(0);
        });
        for (const bone of ["head", "hand_l", "hand_r", "spine"].filter((name) => start.has(name))) {
            const [a, b] = [start, end].map((moves) => moves.get(bone).elements);
            expect(Math.max(...a.map((value, index) => Math.abs(value - b[index]))), `${voice} ${bone}`).toBeLessThan(1e-6);
        }
    }
});

test("the telephone rings at most once in two minutes, gathering every worker given work into one call that names each in turn", async () => {
    const {callLines} = await import("../src/domain/figureState.js");
    const {answerTo, heldCall, joinedCall} = await import("../src/figure/reactions.js");
    const {phrasesOf} = await import("../src/figure/comicBubble.js");
    const {CALL_COOLDOWN} = await import("../src/figure/pile.js");
    expect(CALL_COOLDOWN).toBe(120);
    const tasks = {57: 2742, 58: 2743, 59: 2744};
    const memory = {reacted: new Map(), played: []};
    const given = (id, time) => ({beat: "messaged", time, card: `workers:${id}:dispatched`});
    // the first worker given work sets off the call
    const first = answerTo(given(57, 1000), "butler", memory, 1000, () => 0, () => true);
    expect(first.beat).toMatchObject({clip: "phone_call", mark: "workers:57:dispatched"});
    let beats = [first.beat];
    // the next two, within the minute, while the call waits or plays, join it rather than ring again
    beats = joinedCall(beats, "workers:58:dispatched");
    beats = joinedCall(beats, "workers:59:dispatched");
    expect(beats).toHaveLength(1);
    expect(beats[0].marks).toEqual(["workers:57:dispatched", "workers:58:dispatched", "workers:59:dispatched"]);
    expect(joinedCall(beats, "workers:58:dispatched")).toBe(beats);
    const words = (marks) => phrasesOf(callLines(marks.map((mark) => ({row: mark.split(":").slice(0, 2).join(":"), task: tasks[mark.split(":")[1]]})))).map((phrase) => phrase.rows.map((row) => row.text).join(" "));
    expect(words(beats[0].marks)).toEqual(["Worker 57", "Task 2742!", "Worker 58", "Task 2743!", "Worker 59", "Task 2744!"]);
    // with no call waiting, a worker given work inside the two minutes rings nothing: it waits, held, for the next call
    expect(joinedCall([], "workers:58:dispatched")).toBeNull();
    expect(answerTo(given(58, 1060), "butler", memory, 1060, () => 0, () => true)).toBeNull();
    const held = ["workers:58:dispatched", "workers:59:dispatched"];
    expect(heldCall(held, [], memory.reacted, 1060)).toBeNull();
    expect(heldCall(held, [], memory.reacted, 1000 + CALL_COOLDOWN - 1)).toBeNull();
    // once the two minutes are over, the held workers are called together, and the next call waits two minutes again
    const later = heldCall(held, [], memory.reacted, 1000 + CALL_COOLDOWN);
    expect(later).toMatchObject({clip: "phone_call", mark: "workers:58:dispatched", marks: held});
    expect(heldCall(["workers:57:dispatched"], [], memory.reacted, 1000 + CALL_COOLDOWN + 60)).toBeNull();
    expect(answerTo(given(57, 1000 + CALL_COOLDOWN + 60), "butler", memory, 1000 + CALL_COOLDOWN + 60, () => 0, () => true)).toBeNull();
    expect(heldCall([], [], memory.reacted, 2000)).toBeNull();
});

test("a worker's dispatch sets off the call by what its mark is, the worker's process card, whatever it says; a failed one does not; and the dispatches gather into one call", async () => {
    const {answerTo, heldCall, joinedCall} = await import("../src/figure/reactions.js");
    const {CALL_COOLDOWN} = await import("../src/figure/pile.js");
    const dispatch = (id, worker, text, tone = "", process = "worker") => ({
        table: "messages",
        id,
        author: "system",
        text: `Worker ${worker}, Mr. Muybridge, motion photographer: ${text}`,
        data: {kind: "card", icon: "agents", tone, row: `workers:${worker}`, task: 2700 + worker, card_type: "process", process, active: true},
        session: "s",
        created_at: new Date((1000 + id) * 1000).toISOString(),
    });
    // the last, another process's card with a worker's row, is no dispatch
    const messages = [dispatch(1, 57, "started on claude opus"), dispatch(2, 58, "started"), dispatch(3, 59, "failed", "bad"), dispatch(4, 60, "started on codex"), dispatch(5, 61, "started on claude sonnet"), dispatch(6, 62, "started on claude opus", "", "output")];
    const beats = beatsAfter(withSystemCards({session: "s", data: {}}, messages), 0);
    expect(beats.map((fire) => [fire.beat, fire.card])).toEqual([1, 2, 4, 5].map((id) => ["messaged", `messages:${id}`]));
    // the first dispatch rings, the next while its call waits joins it, and one inside the two minutes with no call waiting is held
    const memory = {reacted: new Map(), played: []};
    const first = answerTo(beats[0], "butler", memory, beats[0].time, () => 0, () => true);
    expect(first.beat).toMatchObject({clip: "phone_call", mark: "messages:1"});
    const queue = joinedCall([first.beat], beats[1].card);
    expect(queue[0].marks).toEqual(["messages:1", "messages:2"]);
    expect(answerTo(beats[2], "butler", memory, beats[2].time + 60, () => 0, () => true)).toBeNull();
    const held = [beats[2].card, beats[3].card];
    expect(heldCall(held, [], memory.reacted, beats[0].time + CALL_COOLDOWN - 1)).toBeNull();
    expect(heldCall(held, [], memory.reacted, beats[0].time + CALL_COOLDOWN)).toMatchObject({clip: "phone_call", mark: "messages:4", marks: held});
});

test("jobs handed out in a row make one call: each worker named, then each task given it in turn, then the next worker and its task; after the cooldown a call starts anew", async () => {
    const {callLines} = await import("../src/domain/figureState.js");
    const {answerTo, heldCall, joinedCall} = await import("../src/figure/reactions.js");
    const {phrasesOf} = await import("../src/figure/comicBubble.js");
    const {CALL_COOLDOWN} = await import("../src/figure/pile.js");
    // a worker's dispatch and its next jobs, each mark naming the task it gave (features/workers worker_process_card, worker_moment_cards)
    const dispatch = (id, worker, task) => ({table: "messages", id, author: "system", session: "s", text: `Worker ${worker}, Mr. Muybridge, motion photographer: started on claude opus`, data: {kind: "card", icon: "agents", tone: "", row: `workers:${worker}`, card_type: "process", process: "worker", active: true, task}, created_at: new Date((1000 + id) * 1000).toISOString()});
    const nextJob = (id, worker, task) => ({table: "messages", id, author: "system", session: "s", text: `Worker ${worker}, Mr. Muybridge, motion photographer: sent its next job`, data: {kind: "card", icon: "agents", tone: "", row: `workers:${worker}`, task}, created_at: new Date((1000 + id) * 1000).toISOString()});
    // worker 260 given tasks 200, 201 and 204, and worker 261 dispatched on task 300 in between, all within a few seconds
    const messages = [dispatch(1, 260, 200), nextJob(2, 260, 201), dispatch(3, 261, 300), nextJob(4, 260, 204)];
    const lead = withSystemCards({session: "s", data: {}}, messages);
    const beats = beatsAfter(lead, 0);
    expect(beats.map((beat) => beat.beat)).toEqual(["messaged", "messaged", "messaged", "messaged"]);
    // the first rings, every other joins the call while it waits or plays
    const memory = {reacted: new Map(), played: []};
    const first = answerTo(beats[0], "butler", memory, beats[0].time, () => 0, () => true);
    let queue = [first.beat];
    for (const beat of beats.slice(1)) queue = joinedCall(queue, beat.card);
    expect(queue).toHaveLength(1);
    // the call's words, as the figure reads them from the marks it gathered (VoiceFigure callMarks)
    const words = (call) => phrasesOf(callLines((call.marks ?? [call.mark]).map((key) => lead.data.cards.find((card) => card.key === key)))).map((phrase) => phrase.rows.map((row) => row.text).join(" "));
    expect(words(queue[0])).toEqual(["Worker 260", "Task 200!", "Task 201!", "Task 204!", "Worker 261", "Task 300!"]);
    // the next job inside the cooldown, with no call waiting, rings nothing and is held; once the cooldown is over it makes a call of its own
    const later = withSystemCards({session: "s", data: {}}, [...messages, nextJob(60, 261, 301)]);
    const held = beatsAfter(later, 1004).map((beat) => beat.card);
    expect(answerTo({beat: "messaged", time: 1060, card: held[0]}, "butler", memory, 1060, () => 0, () => true)).toBeNull();
    expect(heldCall(held, [], memory.reacted, beats[0].time + CALL_COOLDOWN - 1)).toBeNull();
    const anew = heldCall(held, [], memory.reacted, beats[0].time + CALL_COOLDOWN);
    expect(phrasesOf(callLines(anew.marks.map((key) => later.data.cards.find((card) => card.key === key)))).map((phrase) => phrase.rows.map((row) => row.text).join(" "))).toEqual(["Worker 261", "Task 301!"]);
});

test("a worker is called only once a task is given to it: a mark that names none rings nothing, a dispatch on a task rings a call saying the worker and the task, and no call is ever spoken without a task", async () => {
    const {answerTo, heldCall, joinedCall} = await import("../src/figure/reactions.js");
    const {phrasesOf} = await import("../src/figure/comicBubble.js");
    const {callLines} = await import("../src/domain/figureState.js");
    const mark = (id, label, data) => ({table: "messages", id, author: "system", session: "s", text: `Worker 260, Mr. Muybridge, motion photographer: ${label}`, data: {kind: "card", icon: "agents", tone: "", row: "workers:260", ...data}, created_at: new Date((1000 + id) * 1000).toISOString()});
    const process = {card_type: "process", process: "worker", active: true};
    // a dispatch or a next job whose mark names no task, a worker named alone: no call
    const untasked = [mark(1, "started on claude opus", {...process, task: 0}), mark(2, "sent its next job", {}), mark(3, "sent its next job", {task: 0})];
    expect(beatsAfter(withSystemCards({session: "s", data: {}}, untasked), 0)).toEqual([]);
    // a dispatch on task 200: the call says the worker, then the task
    const tasked = [...untasked, mark(4, "started on claude opus", {...process, task: 200})];
    const lead = withSystemCards({session: "s", data: {}}, tasked);
    const beats = beatsAfter(lead, 0);
    expect(beats.map((beat) => [beat.beat, beat.card])).toEqual([["messaged", "messages:4"]]);
    const call = answerTo(beats[0], "butler", {reacted: new Map(), played: []}, beats[0].time, () => 0, () => true).beat;
    const words = (marks) => phrasesOf(callLines(marks.map((key) => lead.data.cards.find((card) => card.key === key)))).map((phrase) => phrase.rows.map((row) => row.text).join(" "));
    expect(words(call.marks ?? [call.mark])).toEqual(["Worker 260", "Task 200!"]);
    // whatever marks a call gathers or holds, a worker without a task is never named: every worker it says is followed by a task
    for (const marks of [["messages:1", "messages:4"], ["messages:2", "messages:3"], ["messages:4", "messages:2"]]) {
        const said = words(joinedCall([{...call, marks: [marks[0]]}], marks[1])[0].marks);
        said.forEach((line, index) => {
            if (line.startsWith("Worker")) expect(said[index + 1], `${marks}: ${said}`).toMatch(/^Task /);
        });
        const held = heldCall(marks, [], new Map(), 10000);
        expect(words(held.marks).filter((line) => line.startsWith("Worker")).length).toBeLessThanOrEqual(words(held.marks).filter((line) => line.startsWith("Task")).length);
    }
});
