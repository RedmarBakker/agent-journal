// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {afterEach, expect, test, vi} from "vitest";
import {page} from "./support/figurePage.js";
import {clearOfNewest, freeSpot, hiddenAt, newestAsideSpot, newestButton, tripBetween, posedFacing, seatedFacing, turnStep} from "../src/figure/places.js";
import {FigurePlayer} from "../src/figure/player.js";
import {NEWEST_ASIDE, newestScootAt, newestSeatAfter} from "../src/figure/newest.js";
import {CLIPS, GROUND, blendedMoves, drawnPose, reachSide} from "../src/figure/figure.js";

const figure = {size: 112, below: GROUND};
const original = {window: globalThis.window, document: globalThis.document, Node: globalThis.Node};
afterEach(() => Object.assign(globalThis, original));

function chatWithButton(box = {left: 460, right: 550, top: 545, bottom: 580}) {
    const home = page();
    const button = document.createElement("button");
    button.className = "thread-down";
    button.textContent = "3 new";
    button.getBoundingClientRect = () => ({...box, width: box.right - box.left, height: box.bottom - box.top});
    home.parentElement.append(button);
    return {home, button};
}

test("Newest is measured in the active thread even when its label changes to a count, and disappears with the button", () => {
    const {button} = chatWithButton();
    expect(newestButton()).toMatchObject({left: 460, right: 550, top: 545, bottom: 580});
    button.getBoundingClientRect = () => ({left: 220, right: 310, top: 400, bottom: 430});
    expect(newestButton()).toMatchObject({left: 220, top: 400});
    button.checkVisibility = () => false;
    expect(newestButton()).toBeNull();
    button.remove();
    expect(newestButton()).toBeNull();
});

test("a Newest-labelled control inside a message never creates an exclusion", () => {
    const {button} = chatWithButton();
    button.className = "";
    button.textContent = "Newest";
    const bubble = document.createElement("div");
    bubble.dataset.figureBubble = "";
    button.replaceWith(bubble);
    bubble.append(button);
    expect(newestButton()).toBeNull();
});

test("standing takes the nearest available side on the same floor and travels with an ordinary walking leg", () => {
    chatWithButton();
    const near = {x: 500, y: 600, posture: "stand", face: 0};
    const aside = newestAsideSpot(figure, near, {left: 300, right: 700});
    expect(aside).toMatchObject({y: near.y, posture: "stand", face: 0});
    expect(aside.x).toBeLessThan(near.x);
    expect(clearOfNewest(aside, figure)).toBe(true);
    const trip = tripBetween(near, aside, figure.size, {random: () => 1});
    expect(trip.pace).toBe(1);
    expect(trip.legs.filter((leg) => leg.ms > 0).every((leg) => !leg.hopping)).toBe(true);
    expect(trip.legs.find((leg) => !leg.hopping).ms).toBeCloseTo(Math.abs(aside.x - near.x) / 90 * 1000);
    expect(newestAsideSpot(figure, near, {left: 490, right: 700}).x).toBeGreaterThan(near.x);
    expect(newestAsideSpot(figure, near, {left: 460, right: 550})).toBeNull();
});

test("seated legs below the ledge also keep clear, and the seat becomes eligible again when Newest goes away", () => {
    const {button} = chatWithButton({left: 470, right: 530, top: 604, bottom: 628});
    const seat = {x: 500, y: 600, posture: "sit", face: 70};
    expect(clearOfNewest(seat, figure)).toBe(false);
    expect(hiddenAt(seat, figure)).toBeGreaterThan(0);
    const aside = newestAsideSpot(figure, seat, {left: 300, right: 700});
    expect(aside).toMatchObject({y: 600, posture: "sit", face: 70});
    expect(clearOfNewest(aside, figure)).toBe(true);
    expect(freeSpot([seat], figure, seat)).toBeNull();
    button.remove();
    expect(clearOfNewest(seat, figure)).toBe(true);
    expect(freeSpot([seat], figure, seat)).toEqual(seat);
});

test("seated travel pauses between three pushes and never moves sideways while the hips are down", () => {
    let previous = newestScootAt(0);
    let moving = false;
    let pushes = 0;
    for (let index = 1; index <= 2400; index++) {
        const at = newestScootAt(index / 2400);
        const moves = at.across - previous.across > 1e-8;
        if (moves && !moving) pushes++;
        if (moves) expect(Math.min(at.lift, previous.lift)).toBeGreaterThan(NEWEST_ASIDE.lift * 0.999);
        expect(at.across).toBeGreaterThanOrEqual(previous.across);
        expect(at.across - previous.across).toBeLessThan(0.003);
        moving = moves;
        previous = at;
    }
    expect(pushes).toBe(3);
    expect(newestScootAt(0)).toMatchObject({across: 0, lift: 0, ready: 0});
    expect(newestScootAt(1)).toMatchObject({across: 1, lift: 0, ready: 0});
});

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));

// Bone positions are sampled at display-frame cadence, including every lift, support reset and settled endpoint.
test("every voice scoots in each seated posture without standing, unreachable limbs, or discontinuous bone positions", () => {
    const clip = CLIPS.find((each) => each.name === "newest_scoot");
    const idle = CLIPS.find((each) => each.name === "idle");
    for (const voice of Object.keys(stances)) {
        for (const posture of ["sit", "lounge", "composed"]) {
            const stance = stanceOf(voice);
            const at = (u) => drawnPose(RIG, stance, clip, u * (clip.frames - 1), 0, {posture, stride: 0.65, walkWay: 1}).pose;
            const first = at(0);
            const last = at(1);
            const rest = drawnPose(RIG, stance, idle, 0, 0, {posture}).pose;
            for (const bone of RIG.order) {
                expect(first.head(bone, first.matrix(bone)).distanceTo(rest.head(bone, rest.matrix(bone))), `${voice} ${posture} starts ${bone}`).toBeLessThan(1e-6);
                expect(last.head(bone, last.matrix(bone)).distanceTo(first.head(bone, first.matrix(bone))), `${voice} ${posture} ends ${bone}`).toBeLessThan(1e-6);
            }
            let previous = first;
            for (let frame = 1; frame <= 144; frame++) {
                const pose = at(frame / 144);
                expect(pose.posture).toBe(posture);
                for (const bone of RIG.order) {
                    const point = pose.head(bone, pose.matrix(bone));
                    expect(point.toArray().every(Number.isFinite)).toBe(true);
                    expect(point.distanceTo(previous.head(bone, previous.matrix(bone))), `${voice} ${posture} frame ${frame} ${bone}`).toBeLessThan(0.2);
                }
                previous = pose;
            }
        }
    }
});


// The planted wrist stays on the bench in page space while the hips cross beneath it, for both directions and turned seats.
test("the scoot keeps its supporting palm planted during each push", () => {
    const clip = CLIPS.find((each) => each.name === "newest_scoot");
    for (const voice of Object.keys(stances)) {
        const stance = stanceOf(voice);
        for (const posture of clip.postures) {
            for (const facing of [-70, 0, 70]) {
                for (const way of [-1, 1]) {
                    for (let shuffle = 0; shuffle < 3; shuffle++) {
                        const points = [0.4, 0.55, 0.73].map((phase) => {
                            const u = 0.12 + 0.76 * (shuffle + phase) / 3;
                            const pose = drawnPose(RIG, stance, clip, u * (clip.frames - 1), facing, {posture, stride: 0.65, walkWay: way}).pose;
                            const hand = `hand_${reachSide(stance, -way)}`;
                            const at = pose.head(hand, pose.moves(facing).get(hand));
                            return at.add(new THREE.Vector3(way * 0.65 * 5.4 * newestScootAt(u).across, 0, 0));
                        });
                        for (const point of points.slice(1)) expect(point.distanceTo(points[0]), `${voice} ${posture} ${facing} ${way} push ${shuffle}`).toBeLessThan(0.015);
                    }
                }
            }
        }
    }
});

// A run's lit visor or changing eye expression must not turn the moving body away from its planted support.
test("visor and eye reactions do not turn the body during a scoot", () => {
    const clip = CLIPS.find((each) => each.name === "newest_scoot");
    const options = {posture: "sit", stride: 0.65, walkWay: 1, at: null};
    const plain = drawnPose(RIG, stanceOf("butler"), clip, 22, 70, options);
    const lit = drawnPose(RIG, stanceOf("butler"), clip, 22, 70, {...options, eyes: {mood: "amused", seconds: 1, lasts: 2}, screen: {eyes: 1, glow: 1, open: 1}});
    expect(lit.turned).toBe(plain.turned);
    for (const bone of RIG.order) expect(lit.pose.head(bone, lit.pose.matrix(bone)).distanceTo(plain.pose.head(bone, plain.pose.matrix(bone)))).toBeLessThan(1e-6);
});


// Typing turns its rendered body to sixty degrees, but that temporary clip direction must never replace the seat's zero direction.
test("leaving a scoot preserves the canonical seat and eases from a temporary typing angle without standing", () => {
    const place = {x: 620, y: 600, posture: "sit", face: 0};
    const footing = {id: "home", dx: 320, dy: 0, posture: "sit", face: 0};
    const aside = {canonicalFace: 0, footingFace: 0, face: 60, facing: 60};
    for (const clip of [CLIPS.find((each) => each.name === "idle"), CLIPS.find((each) => each.name === "type")]) {
        const facing = seatedFacing(clip, place.face);
        const resumed = newestSeatAfter(aside, place, footing, facing, 10);
        expect(resumed.place).toEqual(place);
        expect(resumed.footing).toEqual(footing);
        expect(turnStep(resumed.posed, {posture: "sit", facing})).toEqual({posture: "sit", facing});
        expect(posedFacing(resumed.seatPose, 10)).toBe(60);
        expect(posedFacing(resumed.seatPose, 11.2)).toBeCloseTo(facing);
        expect(posedFacing(resumed.seatPose, 10.01)).toBeCloseTo(60, 1);
    }
});

// Autonomous flights remain ineligible while a seated figure is already making room.
test("a scooting figure cannot start an autonomous flight", async () => {
    const {pastimeFor} = await import("../src/figure/reactions.js");
    const scene = {voice: "homie", moving: true, place: {posture: "sit"}, beats: 0, held: false, room: 60, arriving: false, leaving: false};
    for (const random of [() => 0, () => 0.5, () => 0.999999]) expect(pastimeFor(scene, {state: "idle", lasted: 60}, {}, 60, random, () => true)).toBeNull();
});


// Use the actual player and skeletal blend; only the final canvas copy is replaced so no WebGL context is needed.
test("notice eases from a reading pose even when the idle clip and facing key remain unchanged", () => {
    const clip = CLIPS.find((each) => each.name === "idle");
    const stance = stanceOf("butler");
    const read = drawnPose(RIG, stance, clip, 0, 0, {posture: "stand", at: {x: 1.5, y: 0.2, amount: 1}});
    const notice = {posture: "stand", at: {x: 0.5, y: 0.85, amount: 1}};
    const target = drawnPose(RIG, stance, clip, 0, 0, notice);
    const goal = target.pose.moves(target.turned);
    const from = read.pose.moves(read.turned);
    const context = {clearRect() {}, drawImage() {}};
    const player = Object.assign(Object.create(FigurePlayer.prototype), {moves: from, shape: "idle/stand/0", posture: "stand", blend: null, shown: "", canvas: {width: 112, height: 112, getContext: () => context}});
    player.liveOf = (shown, frame, facing, options) => {
        const pose = drawnPose(RIG, stance, shown, frame, facing, options);
        const result = blendedMoves(RIG, pose.pose, pose.turned, options.blend);
        if (options.blend) options.blend.settled = result.settled;
        return {frame: {}, moves: result.moves};
    };
    const rotation = (moves) => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(moves.get("head")));
    const original = rotation(from);
    const destination = rotation(goal);
    let clock = 1000;
    const time = vi.spyOn(performance, "now").mockImplementation(() => clock);
    try {
        player.easeFromCurrent();
        player.show(clip, 0, 0, notice);
        expect(rotation(player.moves).angleTo(original)).toBeLessThan(1e-6);
        expect(rotation(player.moves).angleTo(destination)).toBeGreaterThan(0.2);
        const began = player.blend.began;
        let previous = rotation(player.moves).angleTo(destination);
        for (let step = 1; step <= 30; step++) {
            clock = 1000 + step * 16;
            player.show(clip, 0, 0, notice);
            const distance = rotation(player.moves).angleTo(destination);
            expect(distance).toBeLessThanOrEqual(previous + 1e-6);
            if (player.blend) expect(player.blend.began).toBe(began);
            previous = distance;
        }
        expect(previous).toBeLessThan(1e-6);
        expect(player.blend).toBeNull();
        player.blend = {from, began: 900, plant: true};
        player.easeFromCurrent();
        expect(player.blend.plant).toBe(true);
    } finally {
        time.mockRestore();
    }
});
