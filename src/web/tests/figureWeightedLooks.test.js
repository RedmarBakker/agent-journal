// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing, drawnPose, lookToward} from "../src/figure/figure.js";
import {COMPOSER_FULL_SECONDS, COMPOSER_SECONDS, HEAD, LINGER_SECONDS, LOOKS, SCREEN_LOOKS, SWITCH_SECONDS, composerLook, headBlend, holdsHead, leadingLook, lookInFigure, looksFor} from "../src/figure/looks.js";
import {LOOK_EASE_MS, gazeAfter} from "../src/figure/reactions.js";

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);

// a look of `kind` at a point on the page
const look = (kind, x = 900, y = 200, key = kind) => ({key, kind, point: {x, y}});
// a message's bubble up to the figure's right, as a share of its picture
const MESSAGE_AT = {x: 1.2, y: 0.05};

test("every screen look targets the page behind the figure while props and the pointer keep their own depth", () => {
    const offered = Object.keys(LOOKS).map((kind) => look(kind, 0.5, 0.3));
    const routed = looksFor(clipNamed("idle"), offered);
    for (const target of routed) {
        expect(Boolean(target.point.behind), target.kind).toBe(SCREEN_LOOKS.has(target.kind));
        expect(offered.find((each) => each.key === target.key).point).not.toHaveProperty("behind");
    }
    const limited = {key: "confession", kind: "confession", point: {x: 0.7, y: 0.3, most: 45, faces: true, mood: "admiring"}};
    expect(looksFor(clipNamed("idle"), [limited])[0].point).toEqual({...limited.point, behind: true});
    for (const voice of Object.keys(stances)) {
        const at = routed.find((each) => each.kind === "said").point;
        const {pose, turned} = drawnPose(RIG, stanceOf(voice), clipNamed("idle"), 0, 0, {at: {...at, amount: 1}});
        const direction = new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(turned).get("head"));
        expect(direction.y, `${voice} looks toward the screen`).toBeGreaterThan(0.9);
        expect(Math.abs(turned), `${voice} follows the head with its body`).toBeGreaterThan(90);
    }
});

test("converting a live screen look into the figure's picture preserves its limit on the body's turn", () => {
    const origin = {x: 320, y: 480};
    const size = 112;
    const center = {x: origin.x + size / 2, y: origin.y + size * 0.3};
    for (const x of [-2, 0.5, 3]) {
        const offered = {key: "confession", kind: "confession", point: {x: origin.x + x * size, y: origin.y + 0.3 * size, most: 45, faces: true, mood: "admiring"}};
        const target = looksFor(clipNamed("idle"), [offered])[0].point;
        const gaze = gazeAfter({point: null, toward: null, amount: 0, at: 1000}, target, center, 1500);
        const at = lookInFigure(gaze, origin, size);
        expect(at).toMatchObject({most: 45, faces: true, behind: true, mood: "admiring", amount: 1});
        expect(at.x).toBeCloseTo(x, 10);
        expect(at.y).toBeCloseTo(0.3, 10);
        for (const voice of Object.keys(stances)) {
            const drawn = (point) => drawnPose(RIG, stanceOf(voice), clipNamed("idle"), 0, 0, {at: point}).turned;
            expect(Math.abs(drawn(at)), `${voice}: the live target keeps its three-quarter limit`).toBeLessThanOrEqual(45);
            expect(Math.abs(drawn({...at, most: undefined})), `${voice}: losing the limit would turn it farther`).toBeGreaterThan(60);
        }
        const shifted = lookInFigure(gaze, {x: origin.x + size, y: origin.y - size}, size);
        expect(shifted.x).toBeCloseTo(x - 1, 10);
        expect(shifted.y).toBeCloseTo(1.3, 10);
        expect(shifted.most).toBe(45);
        expect(lookInFigure({...gaze, amount: 0}, origin, size)).toBeNull();
    }
});

test("switching between a prop and text at the same page pixels eases away before changing depth", () => {
    const center = {x: 500, y: 300};
    const step = 1000 / 60;
    for (const behind of [false, true]) {
        const point = {x: 500, y: 270, behind};
        let gaze = {point, toward: null, amount: 1, at: 1000};
        let switched = false;
        for (let frame = 1; frame <= 75; frame++) {
            const before = gaze;
            gaze = gazeAfter(gaze, {...point, behind: !behind}, center, 1000 + frame * step);
            expect(Math.abs(gaze.amount - before.amount)).toBeLessThanOrEqual(step / LOOK_EASE_MS + 1e-9);
            if (gaze.point.behind !== before.point.behind) {
                expect(before.amount).toBe(0);
                expect(gaze.amount).toBeLessThanOrEqual(step / LOOK_EASE_MS + 1e-9);
                switched = true;
            }
        }
        expect(switched).toBe(true);
        expect(gaze.point.behind).toBe(!behind);
        expect(gaze.amount).toBe(1);
    }
});

// how many degrees the head turns from the act's own pose at `u` of `name` when it looks at `at` `amount` of the way
function headTurn(name, amount, voice = "butler") {
    const clip = clipNamed(name);
    const posed = () => {
        const pose = new Posing(RIG, clip.postures[0], 0);
        clip.pose(pose, stanceOf(voice), 0.3);
        return pose;
    };
    const own = posed().matrix("head");
    const pose = posed();
    lookToward(pose, {...MESSAGE_AT, amount}, 0);
    const turn = (matrix) => new THREE.Quaternion().setFromRotationMatrix(matrix);
    return THREE.MathUtils.radToDeg(turn(own).angleTo(turn(pose.matrix("head"))));
}

test("every act declares how strongly it keeps its head: the ladder, the parachute and the rummage hold it, walking and standing hardly", () => {
    for (const clip of CLIPS) expect(Object.values(HEAD), clip.name).toContain(clip.head);
    for (const name of ["ladder_climb", "chute", "rummage", "pogo"]) expect(holdsHead(clipNamed(name)), name).toBe(true);
    for (const name of ["walk", "idle"]) expect(clipNamed(name).head, name).toBe(HEAD.free);
});

test("walking, the head turns toward a new message; climbing the ladder, the act keeps its head", () => {
    const message = look("message");
    const walking = headBlend(message, clipNamed("walk"));
    const climbing = headBlend(message, clipNamed("ladder_climb"));
    expect(walking).toBeGreaterThan(0.75);
    expect(climbing).toBeLessThan(0.15);
    // the head itself: turned most of the way to the message walking, and hardly at all on the ladder
    const full = headTurn("walk", 1);
    expect(full).toBeGreaterThan(20);
    expect(headTurn("walk", walking)).toBeGreaterThan(0.7 * full);
    expect(headTurn("ladder_climb", climbing)).toBeLessThan(0.2 * headTurn("ladder_climb", 1));
});

test("the strongest of two looks wins, and a new strongest takes over only once it has led for the switch time", () => {
    expect(LOOKS.run).toBeGreaterThan(LOOKS.message);
    expect(leadingLook(null, [look("message"), look("run")], 0).look.key).toBe("run");
    // on a message, a finished run's mark comes: the head keeps to the message until the run has led two seconds
    let leading = leadingLook(null, [look("message")], 10);
    for (const now of [10.1, 11, 11.9, 10.1 + SWITCH_SECONDS - 0.01]) {
        leading = leadingLook(leading, [look("message"), look("run")], now);
        expect(leading.look.key, `${now}`).toBe("message");
    }
    expect(leadingLook(leading, [look("message"), look("run")], 10.1 + SWITCH_SECONDS).look.key).toBe("run");
    // one that leads for less, and is gone again, never takes over, and leading again it waits the whole time anew
    leading = leadingLook(null, [look("message")], 20);
    leading = leadingLook(leading, [look("message"), look("run")], 20.5);
    leading = leadingLook(leading, [look("message"), look("run")], 21.8);
    leading = leadingLook(leading, [look("message")], 22);
    expect(leading.look.key).toBe("message");
    leading = leadingLook(leading, [look("message"), look("run")], 22.6);
    expect(leadingLook(leading, [look("message"), look("run")], 23.5).look.key).toBe("message");
    expect(leadingLook(leading, [look("message"), look("run")], 22.6 + SWITCH_SECONDS).look.key).toBe("run");
    // the look it is on moves with what it looks at, and once that has been gone longer than the linger the strongest left is taken at once
    expect(leadingLook(leading, [look("message", 300, 100)], 23).look.point).toEqual({x: 300, y: 100});
    expect(leadingLook({look: look("run"), challenger: "", since: 0, seen: 0}, [look("glance")], 1).look.key).toBe("run");
    expect(leadingLook({look: look("run"), challenger: "", since: 0, seen: 0}, [look("glance")], LINGER_SECONDS).look.key).toBe("glance");
});

test("a look at what keeps its interest is held: through lapses in it the head stays on it, never back at rest between, and turns only when another wins or the interest ends", () => {
    const idle = clipNamed("idle");
    const center = {x: 500, y: 300};
    // a bar it watches, up to its right, its interest lapsing a moment now and then, its own idle glance coming up in a lapse, and the
    // agent's new message, stronger, coming at 6 seconds; at 9 seconds all of it is over
    const bar = (now) => look("bar", 760, 180 + 4 * now);
    const lapses = [[1, 1.6], [3, 4.5], [5.2, 5.5]];
    const lapsed = (now) => lapses.some(([from, to]) => now >= from && now < to);
    const offered = (now) => {
        if (now >= 9) return [];
        const looks = lapsed(now) ? [look("glance", 380, 280)] : [bar(now)];
        return now >= 6 ? [...looks, look("message", 260, 120)] : looks;
    };
    let [leading, gaze] = [null, {point: null, toward: null, amount: 0, at: 0}];
    const frames = [];
    for (let frame = 0; frame <= 12 * 30; frame++) {
        const now = frame / 30;
        leading = leadingLook(leading, offered(now), now);
        gaze = gazeAfter(gaze, leading.look?.point ?? null, center, now * 1000, null, headBlend(leading.look, idle));
        frames.push({now, key: leading.look?.key ?? null, amount: gaze.amount, point: gaze.point});
    }
    const blend = headBlend(look("bar"), idle);
    // eased onto the bar within half a second, then held on it through every lapse until the message has led the switch time: the same
    // look carried on, its head turned all the way it turns and never easing back toward rest
    const held = frames.filter((each) => each.now >= 0.6 && each.now < 6 + SWITCH_SECONDS);
    for (const each of held) {
        expect(each.key, `${each.now}s`).toBe("bar");
        expect(each.amount, `${each.now}s`).toBe(blend);
        // on the bar where it is, or through a lapse where it last was
        const seen = lapses.find(([from, to]) => each.now >= from && each.now < to)?.[0] ?? each.now;
        expect(Math.hypot(each.point.x - bar(seen).point.x, each.point.y - bar(seen).point.y), `${each.now}s`).toBeLessThan(5);
    }
    // the message, stronger, takes over once it has led the switch time, and the head turns to it
    const turned = frames.find((each) => each.now >= 6 + SWITCH_SECONDS + 0.5);
    expect(turned.key).toBe("message");
    expect(Math.hypot(turned.point.x - 260, turned.point.y - 120)).toBeLessThan(5);
    // the interest over at 9 seconds, the look is held a moment longer, then let go and the head eases back to rest
    expect(frames.find((each) => each.now >= 9 + LINGER_SECONDS / 2).key).toBe("message");
    const after = frames.filter((each) => each.now >= 9 + LINGER_SECONDS);
    expect(after.every((each) => each.key === null)).toBe(true);
    expect(after.at(-1).amount).toBe(0);
});

test("in a middle case the head eases to a blend of the look and the act's own head, by their weights", () => {
    const wave = clipNamed("wave");
    expect(wave.head).toBe(HEAD.gestures);
    const blend = headBlend(look("message"), wave);
    expect(blend).toBeCloseTo(LOOKS.message / (LOOKS.message + HEAD.gestures), 6);
    expect(blend).toBeGreaterThan(0.4);
    expect(blend).toBeLessThan(0.7);
    // the gaze eases in to that blend and holds there, and back out to none once there is nothing to look at
    const center = {x: 500, y: 300};
    let gaze = {point: null, toward: null, amount: 0, at: 0};
    const amounts = [];
    for (let ms = 0; ms <= 1500; ms += 50) {
        gaze = gazeAfter(gaze, {x: 900, y: 200}, center, ms, null, blend);
        amounts.push(gaze.amount);
    }
    expect(amounts.every((amount, index) => index === 0 || amount >= amounts[index - 1])).toBe(true);
    expect(amounts.at(-1)).toBe(blend);
    gaze = gazeAfter(gaze, null, center, 3000, null, 0);
    expect(gaze.amount).toBe(0);
    // the head turned that share of the way from the wave's own head toward the message
    const full = headTurn("wave", 1);
    expect(headTurn("wave", blend) / full).toBeGreaterThan(blend - 0.15);
    expect(headTurn("wave", blend) / full).toBeLessThan(blend + 0.15);
});

test("on the telephone the head follows nothing but the call: no look is taken up while it plays, and it looks again once the call is over", () => {
    const phone = clipNamed("phone_call");
    const idle = clipNamed("idle");
    expect(phone.head).toBe(HEAD.alone);
    expect(holdsHead(phone)).toBe(true);
    // whatever catches its interest meanwhile: the user's new message, the pointer, the agent's message, a bar, its own glance
    const offered = [look("said", 700, 300), look("pointer", 400, 500), look("message", 900, 200), look("bar", 500, 600), look("glance", 450, 380)];
    for (const each of offered) expect(headBlend(each, phone), each.kind).toBe(0);
    expect(looksFor(phone, offered)).toEqual([]);
    // every frame of the call, a twelfth of a second apart, the head takes up none of them
    const seconds = phone.frames / phone.fps;
    let leading = null;
    for (let frame = 0; frame <= seconds * 12; frame++) {
        leading = leadingLook(leading, looksFor(phone, offered), frame / 12);
        expect(leading.look, `${frame / 12}s into the call`).toBe(null);
    }
    // the handset down, the next act looks again at once, at the strongest of them
    leading = leadingLook(leading, looksFor(idle, offered), seconds + 1 / 12);
    expect(leading.look).toMatchObject({kind: "said"});
    expect(headBlend(leading.look, idle)).toBeGreaterThan(0.5);
});

test("the composer is a look while the user types, strongest just after a keystroke and weaker after a pause, and lapses", () => {
    expect(composerLook(0, 100)).toBe(null);
    expect(composerLook(100, 100)).toBe("typing");
    expect(composerLook(100, 100 + COMPOSER_FULL_SECONDS)).toBe("typing");
    expect(composerLook(100, 100 + COMPOSER_FULL_SECONDS + 0.1)).toBe("typing_pause");
    expect(composerLook(100, 100 + COMPOSER_SECONDS)).toBe("typing_pause");
    expect(composerLook(100, 100 + COMPOSER_SECONDS + 0.1)).toBe(null);
    expect(LOOKS.typing).toBeGreaterThan(LOOKS.typing_pause);
    expect(LOOKS.typing_pause).toBeGreaterThan(LOOKS.glance);
});

test("typing is one look among the others: it wins over the figure's idle glances, and a new message from the agent keeps the head", () => {
    const composer = look("typing", 300, 600, "composer");
    expect(leadingLook(null, [look("glance", 100, 100), composer], 10).look.key).toBe("composer");
    const message = look("message", 900, 200);
    expect(leadingLook(null, [composer, message], 10).look.kind).toBe("message");
    const held = leadingLook(null, [composer], 10);
    const weaker = look("typing_pause", 300, 600, "composer");
    expect(leadingLook(held, [weaker], 11).look.key, "the same look goes on as it weakens").toBe("composer");
    expect(leadingLook(held, [], 10 + LINGER_SECONDS + 1).look).toBe(null);
});
