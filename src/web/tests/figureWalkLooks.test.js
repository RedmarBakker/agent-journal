// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";

const {CLIPS, HEAD_TURN, LEGS, Posing, bodyTurnFor, lookToward} = await import("../src/figure/figure.js");
const {LOOKS, WALKING, haltsWalk, headBlend, leadingLook, visitsAfterHalt, walkingGlance} = await import("../src/figure/looks.js");
const {seeded} = await import("./support/seeded.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);
const yaw = (move) => {
    const ahead = new THREE.Vector3(0, -1, 0).transformDirection(move);
    return THREE.MathUtils.radToDeg(Math.atan2(ahead.x, -ahead.y));
};

// targets on every side of a figure's head, as shares of its picture: ahead, behind, above, below and between
const SIDES = [[1.4, 0.3], [-0.4, 0.3], [0.5, -0.6], [0.5, 1.2], [1.3, -0.4], [-0.3, -0.4], [1.3, 1], [-0.3, 1]];

test("walking past targets on every side, the body faces the way it walks and the head turns at most a quarter turn from it", () => {
    for (const voice of Object.keys(stances)) {
        for (const facing of [90, 270]) {
            for (const [x, y] of SIDES) {
                const pose = new Posing(RIG, "walk", 0.3);
                clipNamed("walk").pose(pose, stanceOf(voice), 0.25);
                const further = lookToward(pose, {x, y}, facing);
                const label = `${voice} ${facing} at ${x},${y}`;
                // the body is never turned for the look while it walks, as it is standing
                expect(bodyTurnFor("walk", further), label).toBe(0);
                expect(bodyTurnFor("stand", further), label).toBe(further);
                const moves = pose.moves(facing);
                const apart = Math.abs(((yaw(moves.get("head")) - yaw(moves.get("chest")) + 540) % 360) - 180);
                expect(apart, label).toBeLessThanOrEqual(90);
            }
        }
    }
    expect(HEAD_TURN).toBeLessThanOrEqual(90);
});

test("walking, the head glances only at what lies within a quarter turn of the walk, briefly, and comes back to the walk between", () => {
    // a walk from the left of the page to the right over eight seconds, past targets above, below, ahead and behind on every side
    const targets = [{x: 300, y: 200}, {x: 300, y: 700}, {x: 650, y: 400}, {x: 900, y: 300}, {x: 120, y: 450}];
    let glancing = null;
    let lookedFrom = null;
    const glances = [];
    for (let frame = 0; frame <= 8 * 60; frame++) {
        const now = frame / 60;
        const head = {x: 100 + 100 * now, y: 450};
        // the strongest look this frame: the nearest of the targets
        const nearest = targets.reduce((best, each) => (Math.hypot(each.x - head.x, each.y - head.y) < Math.hypot(best.x - head.x, best.y - head.y) ? each : best));
        const walk = walkingGlance(glancing, {key: `${nearest.x}`, kind: "picture", point: nearest}, 1, head, now);
        glancing = walk.glancing;
        if (walk.look) {
            expect((walk.look.point.x - head.x) * 1, `${now}: within a quarter turn of the walk`).toBeGreaterThanOrEqual(0);
            lookedFrom ??= now;
        } else if (lookedFrom !== null) {
            glances.push(now - lookedFrom);
            lookedFrom = null;
        }
    }
    expect(glances.length).toBeGreaterThan(1);
    for (const seconds of glances) expect(seconds, "brief").toBeLessThanOrEqual(WALKING.glance + 1 / 60);
    // a target behind it is never glanced at, however long it leads
    expect(walkingGlance(null, {key: "behind", kind: "said", point: {x: 100, y: 450}}, 1, {x: 500, y: 450}, 0).look).toBe(null);
    expect(walkingGlance(null, {key: "behind", kind: "said", point: {x: 100, y: 450}}, -1, {x: 500, y: 450}, 0).look).not.toBe(null);
});

test("the user's new message halts the walk: the figure turns and looks at it a while, then goes over to it or on its way, both over many rolls", () => {
    expect(haltsWalk({kind: "said"})).toBe(true);
    for (const kind of Object.keys(LOOKS).filter((each) => each !== "said")) expect(haltsWalk({kind}), kind).toBe(false);
    expect(haltsWalk(null)).toBe(false);
    expect(LOOKS.said, "the strongest look of all").toBe(Math.max(...Object.values(LOOKS)));
    // the look held a moment, a second or two
    expect(WALKING.halt).toBeGreaterThanOrEqual(1);
    expect(WALKING.halt).toBeLessThanOrEqual(3);
    // the head takes the message at once, never waiting out the switch time on what it looked at
    const before = leadingLook(null, [{key: "glance", kind: "glance", point: {x: 0, y: 0}}], 10);
    expect(leadingLook(before, [{key: "glance", kind: "glance", point: {x: 0, y: 0}}, {key: "messages:7", kind: "said", point: {x: 5, y: 5}}], 10.05).look.key).toBe("messages:7");
    // then by weight and a roll: over to the message, or on to where it was going
    const random = seeded(2887);
    const visits = Array.from({length: 2000}, () => visitsAfterHalt(random));
    const share = visits.filter(Boolean).length / visits.length;
    expect(share).toBeCloseTo(LOOKS.said / (LOOKS.said + WALKING.purpose), 1);
    expect(share).toBeGreaterThan(0.2);
    expect(share).toBeLessThan(0.8);
});

test("once it has arrived the looks blend as before: a look on any side is taken whole, the body following the head", () => {
    const said = {key: "messages:7", kind: "said", point: {x: 100, y: 450}};
    // walking it would not look back at it; standing, nothing of the walk applies and the look blends by its weight against the act's
    expect(walkingGlance(null, said, 1, {x: 500, y: 450}, 0).look).toBe(null);
    expect(headBlend(said, clipNamed("idle"))).toBeCloseTo(LOOKS.said / (LOOKS.said + clipNamed("idle").head), 6);
    const pose = new Posing(RIG, "stand", 0);
    clipNamed("idle").pose(pose, stanceOf("butler"), 0);
    const further = lookToward(pose, {x: -0.6, y: 0.3}, 90);
    expect(further).not.toBe(0);
    expect(bodyTurnFor("stand", further)).toBe(further);
});

test("admiring something on the page, standing it turns round to face it, its back to the viewer; seated it turns only a little, its head the rest of the way", async () => {
    const {admiringLook} = await import("../src/figure/admire.js");
    const {SEAT_POSE} = await import("../src/figure/places.js");
    // the look at what it admires is behind it on the page, and faces it
    expect(admiringLook({left: 100, right: 220, top: 40, bottom: 120})).toEqual({x: 160, y: 80, mood: "admiring", behind: true, faces: true});
    const apart = (a, b) => Math.abs(((a - b + 540) % 360) - 180);
    // what it admires, as shares of its picture: up and to its left, up and to its right, straight up behind its head, far to its left
    for (const [x, y] of [[0.2, 0.1], [0.8, 0.15], [0.5, 0.05], [0.05, 0.3]]) {
        const at = {x, y, behind: true, faces: true};
        for (const voice of Object.keys(stances)) {
            const label = `${voice} admiring at ${x},${y}`;
            // standing: the whole body turned round to it, past a quarter turn, its back to the viewer, the head straight on at it
            const standing = new Posing(RIG, "stand", 0);
            clipNamed("idle").pose(standing, stanceOf(voice), 0.3);
            const turned = bodyTurnFor("stand", lookToward(standing, at, 0));
            const stood = standing.moves(turned);
            expect(Math.abs(yaw(stood.get("chest"))), `${label} standing: its back to the viewer`).toBeGreaterThan(90);
            expect(apart(yaw(stood.get("head")), yaw(stood.get("chest"))), `${label} standing: its head on with its body`).toBeLessThan(15);
            // seated, on an edge or composed on a floor: the body turned no further than it shifts on its seat, the head turned its way past it
            for (const posture of ["sit", "composed"]) {
                const pose = new Posing(RIG, posture, 0);
                LEGS[posture].under(pose);
                clipNamed("idle").pose(pose, stanceOf(voice), 0.3);
                LEGS[posture].over(pose);
                const little = bodyTurnFor(posture, lookToward(pose, at, 0));
                const moves = pose.moves(little);
                const seatedLabel = `${label} seated ${posture}`;
                expect(Math.abs(little), `${seatedLabel}: turned only a little`).toBeLessThanOrEqual(Math.max(...SEAT_POSE.turns));
                expect(Math.abs(yaw(moves.get("chest"))), `${seatedLabel}: never round`).toBeLessThan(45);
                expect(apart(yaw(moves.get("head")), yaw(moves.get("chest"))), `${seatedLabel}: its head turned back toward it`).toBeGreaterThan(HEAD_TURN - 10);
                expect(Math.sign(yaw(moves.get("head"))), `${seatedLabel}: toward it`).toBe(Math.sign(little));
            }
        }
    }
});
