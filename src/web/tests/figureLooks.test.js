// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {beforeEach, expect, test} from "vitest";

const {CLIPS, GLASS, LEDGE, Posing, SEATED_TOWARD, seatedTurn, turnToViewer} = await import("../src/figure/figure.js");
const {PILE, choicesFor, draw} = await import("../src/figure/pile.js");
const {READING, answerTo, reactionTo, readingAt} = await import("../src/figure/reactions.js");
const {readingsAfter} = await import("../src/domain/figureState.js");
const {ACTS} = await import("../src/figure/acts.js");
const {LEDGE_SLANT, bubbleNear, ledgeSpot, leanSpot} = await import("../src/figure/perches.js");
const {FRAMED} = await import("../src/figure/frame.js");

const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const radians = THREE.MathUtils.degToRad;
const FIGURE = {size: 112, below: 0.05};
const names = (entries) => entries.map((entry) => entry.name);

// a page with nothing on it to hide, until a test lays floors out by hand
beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
    globalThis.CSS = {escape: (text) => text};
});

// a bubble's floor and the floors snapshot of a chat window that holds the floors given
const bubble = (id, rect) => ({id, kind: "bubble", element: {id}, ...rect});
const floorsOf = (...floors) => ({world: {left: 0, top: 0, right: 1280, bottom: 800}, view: {left: 0, top: 0, right: 1280, bottom: 800}, floors});

test("a report brings the reading look at its bubble, never the report scroll: the head sweeps along it left to right, line by line", () => {
    expect(names(PILE.filter((entry) => entry.when.moment === "reported"))).not.toContain("scroll");
    const answer = answerTo({beat: "reported", time: 1, card: "messages:7"}, "butler", {reacted: new Map(), played: [], tally: null}, 1, () => 0, () => true);
    expect(answer).toEqual({gaze: {card: "messages:7"}});
    const box = {left: 100, right: 400, top: 50, bottom: 140};
    const looks = Array.from({length: 60}, (_, step) => readingAt(box, (step * READING.sweep * 3) / 60));
    for (const look of looks) {
        expect(look.mood).toBe("reading");
        expect(look.x).toBeGreaterThanOrEqual(box.left);
        expect(look.x).toBeLessThanOrEqual(box.right);
        expect(look.y).toBeGreaterThanOrEqual(box.top);
        expect(look.y).toBeLessThanOrEqual(box.bottom);
    }
    // along each line left to right, then the next line down
    const first = looks.slice(0, 19);
    for (let index = 1; index < first.length; index++) expect(first[index].x).toBeGreaterThan(first[index - 1].x);
    expect(new Set(first.map((look) => look.y)).size).toBe(1);
    expect(looks[20].y).toBeGreaterThan(looks[0].y);
});

test("a message of the user's the agent has read brings the same reading look now and then, at most once in thirty seconds", () => {
    const messages = [
        {table: "messages", id: 1, author: "user", read_at: 100},
        {table: "messages", id: 2, author: "user", read_at: null},
        {table: "messages", id: 3, author: "agent", read_at: 120},
    ];
    expect(readingsAfter(messages, 50)).toEqual([{beat: "read_message", time: 100, card: "messages:1"}]);
    expect(readingsAfter(messages, 100)).toEqual([]);
    const memory = new Map();
    const looks = (now) => reactionTo("read_message", memory, now, () => 0)?.gaze ?? null;
    expect(looks(1000)).toBe("read");
    expect(looks(1010)).toBe(null);
    expect(looks(1029)).toBe(null);
    expect(looks(1030)).toBe("read");
    expect(names(choicesFor({moment: "read_message"}))).toContain("nothing");
});

test("the magnifying glass is held up to a bubble only with one within reach, the lens between the eyes and the bubble's text in every frame", () => {
    const searches = (bubbleNear) => names(choicesFor({moment: "held:search", home: true, bubble: bubbleNear}));
    expect(searches(true)).toContain("glass_bubble");
    expect(searches(false)).not.toContain("glass_bubble");
    // a bubble beside the figure at the height of its eyes is near; one far off, one above its head, or the one it stands on is not
    const floor = bubble("floor", {left: 200, right: 600, top: 500, bottom: 560});
    const spot = {x: 300, y: 500, posture: "stand", on: floor.element};
    const beside = bubble("beside", {left: 360, right: 700, top: 380, bottom: 460});
    expect(bubbleNear(floorsOf(floor, beside), spot, FIGURE)).toBe(beside);
    expect(bubbleNear(floorsOf(floor, bubble("far", {left: 600, right: 900, top: 380, bottom: 460})), spot, FIGURE)).toBe(null);
    expect(bubbleNear(floorsOf(floor, bubble("above", {left: 360, right: 700, top: 100, bottom: 200})), spot, FIGURE)).toBe(null);
    expect(bubbleNear(floorsOf(floor), spot, FIGURE)).toBe(null);
    // posed looking at the text out to its right, and to its left, the lens on the line from its eyes to the text, between them
    const clip = CLIPS.find((each) => each.name === "glass_bubble");
    for (const voice of Object.keys(stances)) {
        for (const at of [{x: 0.95, y: 0.25}, {x: 0.1, y: 0.3}]) {
            for (let frame = 0; frame < clip.frames; frame += 6) {
                const pose = new Posing(RIG, "stand", 0);
                pose.at = at;
                clip.pose(pose, stanceOf(voice), frame / clip.frames);
                const moves = pose.moves(0);
                const glass = pose.props.get("magnifying_glass");
                const eyes = RIG.eyes.reduce((sum, eye) => sum.add(eye), new THREE.Vector3()).divideScalar(RIG.eyes.length).applyMatrix4(moves.get("head"));
                const turned = new THREE.Matrix4().extractRotation(moves.get(glass.frame)).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(radians(glass.turn.x), radians(glass.turn.y), radians(glass.turn.z), "ZYX")));
                const lens = glass.at.clone().applyMatrix4(moves.get(glass.bone)).addScaledVector(new THREE.Vector3(0, 0, 1).transformDirection(turned), (GLASS.handle / 2 + GLASS.radius) * glass.size);
                const text = new THREE.Vector3((at.x - 0.5) * FRAMED.height, 0.3, FRAMED.middle + (0.5 - at.y) * FRAMED.height);
                const line = text.clone().sub(eyes);
                const along = lens.clone().sub(eyes).dot(line) / line.lengthSq();
                const off = lens.clone().sub(eyes.clone().addScaledVector(line, along)).length();
                const label = `${voice} at ${at.x} frame ${frame}`;
                expect(along, label).toBeGreaterThan(0.1);
                expect(along, label).toBeLessThan(0.85);
                expect(off, label).toBeLessThan(0.3);
            }
        }
    }
});

test("beside the side of a bubble rising over its floor, with room, the figure leans against it, its hand on the wall's line, among the idle stays at a modest weight", () => {
    const floor = {id: "floor", kind: "bubble", element: {}, left: 200, right: 700, top: 500, bottom: 560};
    const near = {x: 300, y: 500, on: floor.element};
    // a bubble above, its left side over the floor at the hand's height
    const upper = bubble("upper", {left: 450, right: 900, top: 380, bottom: 470});
    const spot = leanSpot(FIGURE, near, floorsOf(floor, upper));
    expect(spot).toMatchObject({posture: "stand", y: 500, on: floor.element, lean: {wall: 450, way: 1}});
    expect(spot.x).toBeCloseTo(450 - ACTS.lean.wall * FIGURE.size, 6);
    // no wall: nothing above, or a bubble whose side is too high to reach
    expect(leanSpot(FIGURE, near, floorsOf(floor))).toBe(null);
    expect(leanSpot(FIGURE, near, floorsOf(floor, bubble("high", {left: 450, right: 900, top: 100, bottom: 300})))).toBe(null);
    // no room: the wall's side right at the floor's end, where the figure would stand off it
    expect(leanSpot(FIGURE, near, floorsOf(floor, bubble("tight", {left: 215, right: 900, top: 380, bottom: 470})))).toBe(null);
    // the pose, for every voice and both ways all through its loop: the whole body tilted from the feet toward the wall, its head well out
    // over its feet that way and its weight on the hand on that side, flat at the wall's line; the ankles crossed, the outer foot over the
    // inner, in front of it and past it toward the wall, both feet on the floor
    const clip = CLIPS.find((each) => each.name === "lean");
    for (const voice of Object.keys(stances)) {
        for (const way of [1, -1]) {
            for (let frame = 0; frame < clip.frames; frame += 8) {
                const pose = new Posing(RIG, "stand", 0);
                pose.leanWay = way;
                clip.pose(pose, stanceOf(voice), frame / clip.frames);
                const moves = pose.moves(0);
                const at = (name) => RIG.heads.get(name).clone().applyMatrix4(moves.get(name));
                const [inner, outer] = way > 0 ? ["l", "r"] : ["r", "l"];
                const label = `${voice} ${way} frame ${frame}`;
                expect(Math.abs(at(`hand_${inner}`).x - way * ACTS.lean.wall * FRAMED.height), label).toBeLessThan(0.25);
                const feet = (at("foot_l").x + at("foot_r").x) / 2;
                expect(way * (at("head").x - feet), label).toBeGreaterThan(0.45);
                expect(at(`foot_${outer}`).y, label).toBeLessThan(at(`foot_${inner}`).y);
                expect(way * (at(`foot_${outer}`).x - at(`foot_${inner}`).x), label).toBeGreaterThan(-0.1);
                for (const side of ["l", "r"]) expect(at(`foot_${side}`).z, `${label} ${side}`).toBeLessThan(0.6);
            }
        }
    }
    const roams = PILE.filter((entry) => entry.when.moment === "roam" && entry.when.free !== false);
    const lean = roams.find((entry) => entry.name === "lean");
    expect(lean.when.free).toBe(true);
    expect(lean.weight / roams.reduce((sum, entry) => sum + entry.weight, 0)).toBeLessThan(0.1);
});

test("the laptop is typed on a corner seat or a bubble's edge, never a floor seat; the slanted seat on the compose box's edge is back, its feet swaying and its toes tipping", () => {
    for (let roll = 0; roll < 1; roll += 0.05) expect(["seat", "bubble_ledge"]).toContain(draw({moment: "laptop"}, () => roll).name);
    // on the compose box's edge it sits slanted toward the nearer end, its legs over the edge, never lounging on its top
    const compose = {getBoundingClientRect: () => ({left: 300, right: 900, top: 600, bottom: 700, width: 600, height: 100}), closest: () => null, querySelector: () => null};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? compose : null);
    const left = ledgeSpot(1 / 3, FIGURE, {on: compose});
    const right = ledgeSpot(2 / 3, FIGURE, {on: compose});
    expect(left).toMatchObject({posture: "sit", face: 360 - LEDGE_SLANT, leans: true});
    expect(right).toMatchObject({posture: "sit", face: LEDGE_SLANT, leans: true});
    expect(LEDGE_SLANT).toBeGreaterThan(20);
    expect(LEDGE_SLANT).toBeLessThan(60);
    const clip = CLIPS.find((each) => each.name === "ledge_sit");
    const sways = [];
    const taps = [];
    for (let frame = 0; frame < clip.frames; frame += 2) {
        const pose = new Posing(RIG, "sit", 0);
        clip.pose(pose, stanceOf("butler"), frame / clip.frames);
        sways.push(pose.sway);
        taps.push(pose.tap);
    }
    expect(Math.max(...sways) - Math.min(...sways)).toBeGreaterThan(0.5);
    expect(Math.max(...taps)).toBeCloseTo(LEDGE.toes, 0);
    expect(Math.min(...taps)).toBe(0);
});

test("seated sideways the figure turns its head toward the camera by itself, so its face shows, and follows a look the other way instead", () => {
    expect(seatedTurn("sit", null)).toBe(SEATED_TOWARD);
    expect(seatedTurn("sit", {x: 0.9, y: 0.3})).toBe(0);
    expect(seatedTurn("stand", null)).toBe(0);
    // turned 70 degrees on a corner seat, the head comes round toward the viewer
    const heading = (strength) => {
        const pose = new Posing(RIG, "sit", 0);
        CLIPS.find((each) => each.name === "type").pose(pose, stanceOf("butler"), 0);
        turnToViewer(pose, 70, strength);
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(pose.moves(0).get("head"));
        return THREE.MathUtils.radToDeg(Math.atan2(ahead.x, -ahead.y));
    };
    expect(heading(SEATED_TOWARD) - heading(0)).toBeLessThan(-5);
});

test("the agent's read of an image attached to a message gives that image the heaviest look for at least three seconds", async () => {
    const {ATTACHMENT_SECONDS, LOOKS, attachmentRead} = await import("../src/figure/looks.js");
    const read = (id, at, path) => ({id, kind: "ToolStarting", created_at: new Date(at * 1000).toISOString(), actor: "agent:s1", data: {tool_name: "Read", call: {read_paths: [path]}}});
    const entries = [read(1, 100, "/p/src/a.py"), read(2, 101, "/p/.journal/files/message/42/shot.png")];
    expect(ATTACHMENT_SECONDS).toBeGreaterThanOrEqual(3);
    expect(Math.max(...Object.values(LOOKS)), "no other look weighs more").toBe(LOOKS.attachment);
    expect(attachmentRead(entries, 101.5)).toBe(42);
    expect(attachmentRead(entries, 101 + ATTACHMENT_SECONDS)).toBe(42);
    expect(attachmentRead(entries, 101 + ATTACHMENT_SECONDS + 1), "then it returns to what it was doing").toBe(0);
    expect(attachmentRead([read(1, 100, "/p/src/a.py")], 100.5), "a read of another file is no look").toBe(0);
});
