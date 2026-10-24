// @vitest-environment node
import {beforeEach, expect, test} from "vitest";

const {PILE, SHENANIGANS, choicesFor, draw} = await import("../src/figure/pile.js");
const {EAGER, roomFor, secondsLeft, spellFor, spellIn} = await import("../src/figure/reactions.js");
const {WORKING, clipOf} = await import("../src/domain/figureState.js");
const {perchOn, roamNext, targetFor} = await import("../src/figure/perches.js");

const FIGURE = {size: 112, below: 0.05};
const HANDS = ["l", "r"];
const WAITING = ["idle", "waiting", "asking"];
// the moments the figure draws its own doings from, with every condition a shenanigan may ask for met
const OWN = {pastime: {lasted: 1000, ball: "bubble", voice: "butler"}, roam: {swings: true}, jump: {high: true}, climb: {footholds: true}};
const rolls = () => Array.from({length: 100}, (_, index) => index / 100);
// every act the figure may draw by itself where it has `room` seconds to be away
const drawnWith = (room) => Object.entries(OWN).flatMap(([moment, scene]) => choicesFor({moment, free: room > 0, room, ...scene}).filter((entry) => entry.kind !== "nothing"));

beforeEach(() => {
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.document = {querySelector: () => null, querySelectorAll: () => []};
    globalThis.CSS = {escape: (text) => text};
});

test("while its agent works the figure draws no shenanigan, nor during a run whose bar has too little left or no pace yet", () => {
    for (const state of WORKING) {
        expect(roomFor(state, null, 100), state).toBe(0);
        expect(drawnWith(roomFor(state, null, 100)).filter((entry) => entry.shenanigan), state).toEqual([]);
    }
    expect(roomFor("testing", {began: 0, share: 0.9, ended: ""}, 45)).toBe(0);
    expect(roomFor("testing", {began: 0, share: 0, ended: ""}, 45)).toBe(0);
    // nor hangs from a bubble by a hand while it works
    const bubble = {id: "b", kind: "bubble", element: {}, left: 260, right: 500, top: 300, bottom: 360};
    const floors = {view: {left: 250, right: 700, top: 100, bottom: 660}, floors: [bubble]};
    expect(perchOn(floors, FIGURE, HANDS, () => 0, {free: false}).kind).toBe("stand");
    expect(perchOn(floors, FIGURE, HANDS, () => 0, {free: true}).kind).toBe("hang");
});

test("while its agent works the figure works: the laptop while it edits, the state's own act while it searches, reads or builds, free during a test run, and the laptop kept a spell after an edit", () => {
    expect(["writing", "searching", "reading", "testing", "building"].map(clipOf)).toEqual(["type", "search", "read", "idle", "work"]);
    const spell = spellFor("writing", null, 0, () => 0);
    expect(clipOf(spellIn({state: "thinking", since: 1}, spell, 5).state)).toBe("type");
});

test("now and then, bored of its spot, the working figure takes its work elsewhere: up onto a bubble, and its laptop to a bubble's edge", () => {
    const working = new Set(rolls().map((roll) => roamNext(() => roll, {free: false, room: 0}).where));
    expect(working.has("bubble")).toBe(true);
    const laptop = rolls().map((roll) => draw({moment: "laptop"}, () => roll).name);
    expect(laptop.filter((where) => where === "seat").length).toBeGreaterThan(laptop.filter((where) => where === "bubble_ledge").length * 3);
    expect(laptop).toContain("bubble_ledge");
    // on the page: the compose box at home and a bubble just above it, where the figure sits on the edge at its laptop
    const box = (rect) => ({...rect, width: rect.right - rect.left, height: rect.bottom - rect.top});
    const bubble = {getBoundingClientRect: () => box({left: 300, right: 600, top: 700, bottom: 740})};
    const scroll = {querySelectorAll: () => [bubble], getBoundingClientRect: () => box({left: 236, right: 778, top: 0, bottom: 760})};
    const thread = {querySelector: (selector) => (selector === ".thread-scroll" ? scroll : null), getBoundingClientRect: () => box({left: 236, right: 778, top: 0, bottom: 900})};
    const home = {getBoundingClientRect: () => box({left: 258, right: 754, top: 768, bottom: 888}), closest: () => thread, querySelector: () => null};
    document.querySelector = (selector) => (selector === "[data-figure-home]" ? home : null);
    const at = {state: "writing", counts: {question: 0, waiting: 0, suggestion: 0}, now: 100, near: {x: 700, y: 768, on: home}, figure: FIGURE, hands: HANDS};
    // the laptop's draw lands on the bubble's edge, at its middle
    const sequence = [0.95, 0, 0, 0];
    const moved = targetFor({...at, stay: {where: "edge", until: 500, along: {x: 400, y: 0}}, random: () => sequence.shift() ?? 0});
    expect(moved.stay).toMatchObject({where: "bubble_ledge", laptop: true, until: 130});
    expect(moved.spot).toMatchObject({posture: "sit", x: 450, y: 700, on: bubble});
    expect(clipOf("writing")).toBe("type");
    // kept while its stay lasts, then mostly back to a corner at home
    expect(targetFor({...at, now: 120, stay: moved.stay}).stay).toBe(moved.stay);
    expect(targetFor({...at, now: 131, stay: moved.stay, random: () => 0}).spot).toMatchObject({posture: "sit", on: home});
});

test("while it waits, and during a long run, the figure plays its shenanigans, and none it could not be back from in time for the run's anticipation", () => {
    for (const state of WAITING) {
        expect(roomFor(state, null, 100), state).toBe(Infinity);
        expect(new Set(drawnWith(Infinity).filter((entry) => entry.shenanigan).map((entry) => entry.name)), state).toEqual(new Set(Object.keys(SHENANIGANS)));
    }
    // a test run a quarter done after a minute has three minutes left: the run up the bubbles fits
    const long = roomFor("testing", {began: 0, share: 0.25, ended: ""}, 60);
    expect(long).toBe(180 - EAGER.lead);
    expect(choicesFor({moment: "pastime", free: true, room: long, lasted: 60}).map((entry) => entry.name)).toContain("hop_up");
    // near its end only what is over in time: a salto, never the run up the bubbles or a stay on a bubble
    const near = roomFor("testing", {began: 0, share: 0.9, ended: ""}, 90);
    expect(near).toBeCloseTo(5, 6);
    expect(drawnWith(near).filter((entry) => entry.shenanigan).map((entry) => entry.name)).toEqual(expect.arrayContaining(["backflip"]));
    expect(drawnWith(near).some((entry) => ["hop_up", "bubble", "rope_swing", "disco"].includes(entry.name))).toBe(false);
    // at any point of any run, a shenanigan drawn is over before the figure is due back for the anticipation
    const shenanigans = PILE.filter((entry) => entry.shenanigan);
    for (let elapsed = 10; elapsed <= 600; elapsed += 30) {
        for (let share = 0.05; share < 1; share += 0.05) {
            const progress = {began: 0, share, ended: ""};
            const room = roomFor("testing", progress, elapsed);
            for (const entry of shenanigans) {
                const offered = choicesFor({moment: entry.when.moment, free: room > 0, room, ...OWN[entry.when.moment]}).includes(entry);
                if (offered) expect(entry.lasts + EAGER.lead, `${entry.name} at ${elapsed}s, ${share}`).toBeLessThanOrEqual(secondsLeft(elapsed, share) + 1e-9);
            }
        }
    }
});
