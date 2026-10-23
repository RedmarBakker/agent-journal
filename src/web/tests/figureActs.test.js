// @vitest-environment node
import {readFileSync} from "node:fs";
import * as THREE from "three";
import {expect, test} from "vitest";
import {CLIPS, Posing} from "../src/figure/figure.js";

// the figures' own skeleton and what each voice carries, as figure.js figureOf reads them from the voices' glbs
const {rig, stances} = JSON.parse(readFileSync(new URL("./figureRig.json", import.meta.url)));
const vectors = (table) => new Map(Object.entries(table).map(([name, at]) => [name, new THREE.Vector3(...at)]));
const RIG = {order: rig.order, parents: new Map(Object.entries(rig.parents)), heads: vectors(rig.heads), along: vectors(rig.along), eyes: rig.eyes.map((at) => new THREE.Vector3(...at))};
const stanceOf = (voice) => Object.fromEntries(Object.entries(stances[voice]).map(([key, value]) => [key, Array.isArray(value) ? new Set(value) : value]));
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);

const ACTED = ["post_dove", "post_mailbox", "stamp", "pin_note", "ask_sign", "whistle_runner", "scroll", "file_card", "cheer"];
const NEW = ["pack_box", "press", "vacuum", "confetti_cannon", "party_horn", "binoculars", "flashlight", "peek_under", "type_ponder", "wipe_brow", "wave_up"];

test("every voice plays every journal moment and every new variant in each posture it is drawn in, every frame, and ends as it stood", () => {
    for (const name of [...ACTED, ...NEW]) {
        const clip = clipNamed(name);
        expect(clip, name).toBeTruthy();
        expect(clip.voices, name).toBeUndefined();
        for (const voice of Object.keys(stances)) {
            for (const posture of clip.postures) {
                for (let frame = 0; frame < clip.frames; frame++) {
                    const pose = new Posing(RIG, posture, 0);
                    pose.sky = {shade: 0, back: 0.5};
                    expect(() => clip.pose(pose, stanceOf(voice), frame / clip.frames), `${name} ${voice} ${posture} ${frame}`).not.toThrow();
                }
            }
        }
    }
});

const {REACTIONS, VARIANTS, AMBIENT, reactionTo, variantOf, workMoments} = await import("../src/figure/reactions.js");
const {beatsAfter, sayingsAfter, withSystemCards} = await import("../src/domain/figureState.js");

const JOURNAL = {
    replied: ["post_dove", "post_mailbox"],
    task_finished: ["stamp"],
    task_filed: ["pin_note"],
    question_asked: ["ask_sign"],
    worker_sent: ["whistle_runner"],
    reported: ["scroll"],
    fact_filed: ["file_card"],
    check_passed: ["cheer"],
};

const at = (seconds) => new Date(seconds * 1000).toISOString();
const message = (id, author, text, data = {}, session = null) => ({table: "messages", id, author, text, data, session, created_at: at(10 + id)});

test("each thing the agent does in the journal is its own moment, read from the chat's messages as the server writes them, and nothing else is", () => {
    const agent = {session: "s", data: {}};
    const messages = [
        message(1, "system", "Finished task 12: the stamp", {icon: "todos", tone: "good"}),
        message(2, "system", "Started task 13: the board", {icon: "todos", tone: ""}),
        message(3, "system", "Filed task 14 from your message", {icon: "inbox"}),
        message(4, "system", "Which one?", {kind: "question", process: "question"}, "s"),
        message(5, "system", "Worker 57, Mr. Muybridge, motion photographer: dispatched on claude opus", {icon: "agents", tone: ""}),
        message(6, "system", "Fact 15 recorded", {icon: "check", tone: "good"}),
        message(7, "system", "Reminder 16 recorded", {icon: "check", tone: "good"}),
        message(8, "system", "Check Check for sins passed", {icon: "check", tone: "good"}),
        message(9, "system", "Resumed task 13: the board", {icon: "todos", tone: ""}),
        message(10, "system", "Worker 57, Mr. Muybridge, motion photographer: released", {icon: "agents", tone: ""}),
        message(11, "system", "Finished task 99 in another session", {icon: "todos", tone: "good"}, "other"),
        message(12, "agent", "Done: the figure stamps now.", {}, "s"),
        message(13, "agent", "Worker 57 reports: done", {kind: "report"}),
        message(14, "agent", "thinking it over", {kind: "thought"}, "s"),
        message(15, "agent", "a reply in another session", {}, "other"),
        message(16, "user", "thanks", {}),
    ];
    const lead = withSystemCards(agent, messages);
    const beats = [...beatsAfter(lead, 0), ...sayingsAfter(lead, messages, 0)].map((fire) => [fire.beat, fire.card]);
    expect(beats).toEqual([
        ["task_finished", "messages:1"],
        ["task_filed", "messages:2"],
        ["task_filed", "messages:3"],
        ["question_asked", "messages:4"],
        ["worker_sent", "messages:5"],
        ["fact_filed", "messages:6"],
        ["fact_filed", "messages:7"],
        ["check_passed", "messages:8"],
        ["replied", "messages:12"],
        ["reported", "messages:13"],
    ]);
    // a message seen at the last look is not a moment again
    expect(sayingsAfter(lead, messages, 10 + 13)).toEqual([]);
});

test("each journal moment is acted out now and then, never every time: it plays on a winning roll only, and not again before its cooldown", () => {
    for (const [moment, acts] of Object.entries(JOURNAL)) {
        const reaction = REACTIONS.find((each) => each.moment === moment);
        expect(reaction.odds, moment).toBeLessThan(1);
        expect(reaction.cooldown, moment).toBeGreaterThanOrEqual(60);
        const memory = new Map();
        expect(reactionTo(moment, memory, 1000, () => reaction.odds), moment).toBe(null);
        expect(acts, moment).toContain(reactionTo(moment, memory, 1000, () => 0).clip);
        expect(reactionTo(moment, memory, 1000 + reaction.cooldown - 1, () => 0), moment).toBe(null);
        expect(reactionTo(moment, memory, 1000 + reaction.cooldown, () => 0)?.clip, moment).toEqual(expect.any(String));
    }
});

// every clip a pick may land on, each at the roll that lands on it
const picks = (among, pick) => {
    const total = among.reduce((sum, each) => sum + each.weight, 0);
    let before = 0;
    return among.map((each) => {
        const roll = (before + each.weight / 2) / total;
        before += each.weight;
        return pick(() => roll);
    });
};

test("every moment the figure acts out has more than one way to play it, picks among them by weight, and never picks one it lacks", () => {
    const has = (name) => Boolean(clipNamed(name));
    // the journal moments, the celebrations and the breaks from the hammering
    for (const moment of [...Object.keys(JOURNAL), "tests_passed", "committed", "task_finished", "building"]) {
        const reaction = REACTIONS.find((each) => each.moment === moment);
        expect(reaction.among.length, moment).toBeGreaterThan(1);
        const memory = () => new Map();
        // the first roll is the odds', the second the pick's
        const rolls = (random) => {
            const seen = [0, random()];
            return () => seen.shift();
        };
        expect(picks(reaction.among, (random) => reactionTo(moment, memory(), 0, rolls(random)).clip), moment).toEqual(reaction.among.map((each) => each.clip));
    }
    expect(workMoments("building", false, 0, 5).moments).toEqual([{beat: "building", time: 5}]);
    // searching, typing and watching the UFO, each picked again for each stretch
    expect(VARIANTS.search.map((each) => each.clip)).toEqual(["search", "binoculars", "flashlight", "peek_under"]);
    for (const [clip, among] of Object.entries(VARIANTS)) {
        expect(among.length, clip).toBeGreaterThan(1);
        expect(among.map((each) => each.clip), clip).toContain(clip);
        expect(picks(among, (random) => variantOf(clip, random, has)), clip).toEqual(among.map((each) => each.clip));
        expect(variantOf(clip, () => 0.99, (name) => name === clip), clip).toBe(clip);
    }
    expect(variantOf("idle", () => 0, has)).toBe("idle");
    // the figure at rest has more pastimes than one
    expect(new Set(AMBIENT.filter((each) => !each.voice).map((each) => each.clip)).size).toBeGreaterThan(2);
});

const {SKYWARD, goneMs, skywardAt, skywardHops, skywardMs} = await import("../src/figure/skyward.js");
const {fallStep} = await import("../src/domain/falls.js");
const {chuteFrom} = await import("../src/domain/figureMotion.js");
const {clipFor} = await import("../src/domain/figureState.js");
const {ACTS, heldPhases, squeezeOf} = await import("../src/figure/acts.js");

test("now and then while idle the figure hops up the bubbles above it very fast, off the top of the screen, and stays gone one to five seconds", () => {
    const pastime = AMBIENT.find((each) => each.flies);
    expect([pastime.clip, pastime.state, pastime.odds < 1]).toEqual(["hop_up", "idle", true]);
    const hops = skywardHops({x: 300, y: 700}, [{x: 340, y: 560}, {x: 260, y: 400}, {x: 330, y: 260}], 0, 112);
    expect(hops.map((hop) => hop.to.y)).toEqual([560, 400, 260, -168]);
    // each hop goes up, and a hop of the figure's height takes well under half a second
    for (const hop of hops) expect(hop.to.y).toBeLessThan(hop.from.y);
    expect(skywardHops({x: 0, y: 112}, [], 0, 112)[0].ms).toBeLessThan(500);
    let previous = skywardAt(hops, 0, 112);
    for (let ms = 20; ms < skywardMs(hops); ms += 20) {
        const now = skywardAt(hops, ms, 112);
        expect(now.gone).toBe(false);
        previous = now;
    }
    expect(previous.y).toBeLessThan(0);
    expect(skywardAt(hops, skywardMs(hops), 112)).toMatchObject({y: -168, gone: true});
    expect([goneMs(() => 0), goneMs(() => 0.999999)].map(Math.round)).toEqual([1000, 5000]);
    expect(clipFor({place: {posture: "stand"}, flying: {way: 1}, state: "idle", doing: "idle"}, () => true)).toMatchObject({clip: "hop_up", facing: 90});
});

test("it floats back down on a parachute, never faster than the parachute lets it, and lands as from any fall", () => {
    const most = SKYWARD.chute * 112;
    const chute = chuteFrom(400, -28, most, 0, () => 0.9);
    expect(chute).toMatchObject({posture: "stand", chute: true, most, catches: false});
    let body = {y: chute.y, speed: 0};
    for (let frame = 0; frame < 200 && body.y < 700; frame++) {
        const stepped = fallStep(body, 700, 1 / 60, {ms: 400}, 112, chute.most);
        expect(stepped.speed).toBeLessThanOrEqual(most);
        body = stepped;
    }
    // falling free it would be far quicker
    expect(fallStep({y: 0, speed: most}, 700, 1 / 60, {ms: 400}, 112).speed).toBeGreaterThan(most);
    expect(clipFor({mode: "airborne", place: {posture: "stand"}, chute: true}, () => true).clip).toBe("chute");
    expect(clipFor({mode: "airborne", place: {posture: "stand"}, chute: false}, () => true).clip).toBe("fall");
});

test("while the context compacts the figure is packed into a box that shrinks, squashed under a press, or vacuums up words, picked each time", () => {
    expect(VARIANTS.compacting.map((each) => each.clip)).toEqual(["pack_box", "press", "vacuum", "compacting"]);
    const box = ACTS.pack_box;
    const frames = box.intro + box.hold + box.outro;
    const at = (frame) => frame / frames;
    // the box shrinks with it inside at the end of the way in and stays small all the while it compacts, then grows back as it ends
    expect(squeezeOf("pack_box", 0)).toEqual({x: 1, y: 1});
    for (let frame = box.intro; frame < box.intro + box.hold; frame++) expect(squeezeOf("pack_box", at(frame)).y).toBeLessThan(box.small + 0.03);
    expect(squeezeOf("pack_box", at(frames - 1)).y).toBeCloseTo(1, 5);
    // the outro, the pop and the jump out, plays only once the compaction is over: the held stretch is what loops
    const clip = clipNamed("pack_box");
    expect([clip.intro, clip.outro, clip.leaves, clip.loops]).toEqual([box.intro, box.outro, box.hold, true]);
    expect(heldPhases(box, at(box.intro + box.hold + box.outro * box.pops + 1)).out).toBeGreaterThan(box.pops);
    // squashed flat under the press, and back to its height once it lifts
    const press = ACTS.press;
    const pressed = (frame) => squeezeOf("press", frame / (press.intro + press.hold + press.outro));
    expect(pressed(press.intro + 1).y).toBeCloseTo(1 - press.flat, 5);
    expect(pressed(press.intro + 1).x).toBeGreaterThan(1);
    expect(pressed(press.intro + press.hold + press.outro).y).toBeCloseTo(1, 5);
    expect(squeezeOf("vacuum", 0.5)).toBe(null);
});
