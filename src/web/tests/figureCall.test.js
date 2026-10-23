// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, TELEPHONE, telephoneOf} from "../src/figure/figure.js";
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
    const order = [act.appears, act.reach, act.lift, act.finger, act.dial, act.back, act.talk, act.hang, act.goes];
    for (let index = 1; index < order.length; index++) expect(order[index][0], `${index}`).toBeGreaterThanOrEqual(order[index - 1][0]);
    expect(act.back[0]).toBe(act.dial[1]);
    for (const voice of Object.keys(stances)) {
        const side = stanceOf(voice).busy.has("r") ? "l" : "r";
        const steps = Array.from({length: 97}, (_, index) => ({u: index / 96, ...posed(index / 96, voice)}));
        const prop = (step, name) => step.pose.props.get(name);
        // it appears from nothing and is gone at the end
        expect(prop(steps[0], "telephone").size, voice).toBe(0);
        expect(steps.find((step) => step.u > act.appears[1] && step.u < act.goes[0]).pose.props.get("telephone").size, voice).toBe(1);
        expect(prop(steps.at(-1), "telephone").size, voice).toBe(0);
        // the handset on the cradle, then in the free hand from the reach to the hang, then on the cradle again
        for (const step of steps) {
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

test("the telephone is solid: every part has depth, is shaded light and dark as the figure is and outlined, and it stands a size too large", () => {
    const [set, handset, cord] = ["telephone", "telephone_handset", "telephone_cord"].map((name) => Object.assign(new THREE.Group(), {name}));
    telephoneOf(set, handset, cord);
    set.userData.shape({size: 1, dial: 0});
    handset.userData.shape({size: 1});
    cord.userData.shape({size: 1, from: new THREE.Vector3(0, 0, 0.3), to: new THREE.Vector3(0.6, -0.4, 1.2)});
    const parts = [set, handset, cord].flatMap((group) => {
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
    // the base deep as well as wide and high, the dial on its slope, and the whole a third of the figure's 5.4 units across, where a real one
    // would be little more than a tenth
    const base = new THREE.Box3().setFromObject(set).getSize(new THREE.Vector3());
    expect(base.z).toBeGreaterThan(0.8);
    expect(base.y).toBeGreaterThan(0.5);
    expect(base.x / 5.4).toBeGreaterThan(0.3);
    expect(TELEPHONE.handset.length / 5.4).toBeGreaterThan(0.25);
});
