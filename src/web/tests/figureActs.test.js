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

const ACTED = ["post_dove", "stamp", "pin_note", "ask_sign", "whistle_runner", "scroll", "file_card"];
const NEW = ["look_left", "look_right", "look_up", "tumble", "fume", "eager", "pack_box", "press", "vacuum", "party_horn", "binoculars", "flashlight", "peek_under", "type_ponder", "wipe_brow", "wave_up"];

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

const {REACTIONS, VARIANTS, AMBIENT, pastimeFor, reactionTo, variantOf, workMoments} = await import("../src/figure/reactions.js");
const {beatsAfter, sayingsAfter, withSystemCards} = await import("../src/domain/figureState.js");

const JOURNAL = {
    messaged: ["post_dove"],
    task_finished: ["stamp"],
    task_filed: ["pin_note"],
    question_asked: ["ask_sign"],
    worker_sent: ["whistle_runner"],
    reported: ["scroll"],
    fact_filed: ["file_card"],
    check_passed: ["joy", "party_horn"],
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
        // a message the agent sends: a worker's next job, a note told it in its session, a message to another session
        message(17, "system", "Worker 57, Mr. Muybridge, motion photographer: sent its next job", {kind: "card", icon: "agents", tone: ""}),
        message(18, "system", "Worker 48, Mr. Sheraton, joiner of panels: told a message in its session", {kind: "card", icon: "agents", tone: ""}),
        message(19, "system", "From the main agent, about the output", {kind: "peer", sent_to: "45-mr-faraday", address: "45-mr-faraday"}),
        // a message from another session is not one the agent sends
        message(20, "system", "Drafted: the reader is committed", {kind: "peer", asks: "x", peer: "code-commandments-e1"}),
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
        ["messaged", "messages:17"],
        ["messaged", "messages:18"],
        ["messaged", "messages:19"],
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
    // the journal moments but the message, which the user wants as the dove alone (message 40754), the celebrations, the breaks from the
    // hammering and the glances from standing still
    for (const moment of [...Object.keys(JOURNAL).filter((each) => each !== "messaged"), "tests_passed", "committed", "building", "standing"]) {
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
    expect([pastime.clip, pastime.odds < 1]).toEqual(["hop_up", true]);
    // played whenever the figure has nothing to do, a wait on a run, a worker or the user as much as idle (messages 40669, 40680)
    const has = (name) => Boolean(clipNamed(name));
    for (const state of ["idle", "waiting", "asking"]) {
        const due = new Map(AMBIENT.filter((each) => !each.flies).map((each) => [each.clip, Infinity]));
        const scene = {voice: "butler", place: {posture: "stand"}, beats: 0, arriving: false, leaving: false, moving: false};
        expect(pastimeFor(scene, {state, lasted: pastime.after}, due, 0, () => 0, has), state).toEqual({clip: "hop_up", card: "", flies: true});
    }
    expect(pastimeFor({voice: "butler", place: {posture: "stand"}, beats: 0}, {state: "thinking", lasted: 999}, new Map(), 0, () => 0, has)).toBe(null);
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
        const stepped = fallStep(body, 700, 1 / 60, chute.most);
        expect(stepped.speed).toBeLessThanOrEqual(most);
        body = stepped;
    }
    // falling free it would be far quicker
    expect(fallStep({y: 0, speed: most}, 700, 1 / 60).speed).toBeGreaterThan(most);
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

const {EAGER, eagerFor, secondsLeft} = await import("../src/figure/reactions.js");

test("eager for a docked bar's end: it starts when the run looks about five seconds from done at its pace, only for a run ten seconds old by then, and is never called off before the end", () => {
    const bar = {};
    const at = (share, ended = "") => ({bar, share, ended, began: 100});
    expect(secondsLeft(20, 0.8)).toBeCloseTo(5);
    // a run 20 seconds in at 70 percent has over 8 seconds left: not yet
    expect(eagerFor(at(0.7), null, () => 0, 120)).toEqual({eager: null, moment: null});
    // at 80 percent after 20 seconds it has 5 left: it rolls, once, by the odds
    expect(eagerFor(at(0.8), null, () => EAGER.odds, 120).eager).toEqual({bar, on: false});
    const eager = eagerFor(at(0.8), null, () => 0, 120).eager;
    expect(eager).toEqual({bar, on: true});
    expect(eagerFor(at(0.95), {bar, on: false}, () => 0, 123).eager.on).toBe(false);
    // a quick run, under ten seconds old when it nears its end, never makes it eager
    expect(eagerFor(at(0.6), null, () => 0, 100 + EAGER.after - 4).eager).toEqual({bar, on: false});
    // started, it is kept to the end whatever the figure does, and then it is cheered or fumed at
    expect(eagerFor(at(0.97), eager, () => 0.99, 124)).toEqual({eager, moment: null});
    expect(eagerFor(at(1, "good"), eager, () => 0, 125)).toEqual({eager: {bar, on: false}, moment: {beat: "bar_done"}});
    expect(eagerFor(at(1, "bad"), eager, () => 0, 125).moment).toEqual({beat: "bar_failed"});
    expect(reactionTo("bar_failed", new Map(), 0, () => 0.99).clip).toBe("fume");
    expect(REACTIONS.find((each) => each.moment === "bar_done").among.map((each) => each.clip)).toEqual(["joy", "party_horn"]);
    // only the bar going ends it with nothing to mark
    expect(eagerFor(null, eager, () => 0, 126)).toEqual({eager: {bar, on: false}, moment: null});
    expect(clipFor({place: {posture: "stand"}, eager: true, state: "running", doing: "think"}, () => true).clip).toBe("eager");
});

test("eager, the figure's eyes are sparkling stars from the first frames until it lets go of the bar, for every voice", () => {
    const clip = clipNamed("eager");
    for (const voice of Object.keys(stances)) {
        for (let frame = 4; frame < clip.intro + clip.leaves; frame++) {
            const pose = new Posing(RIG, "stand", 0);
            clip.pose(pose, stanceOf(voice), frame / clip.frames);
            expect(pose.stars, `${voice} ${frame}`).toBeGreaterThan(0.9);
        }
        const last = new Posing(RIG, "stand", 0);
        clip.pose(last, stanceOf(voice), (clip.frames - 0.01) / clip.frames);
        expect(last.stars, voice).toBeLessThan(0.1);
    }
});

const {SEAT_INBOARD, seatAt} = await import("../src/figure/places.js");

test("sitting on a corner the figure sits just inside it, toward the inside of the edge, its seat on the box and its knees past the end", () => {
    const box = {left: 100, width: 400, top: 300};
    const figure = {size: 112};
    const right = seatAt(box, "right", figure);
    const left = seatAt(box, "left", figure);
    expect([right.x, left.x]).toEqual([500 - SEAT_INBOARD * 112, 100 + SEAT_INBOARD * 112]);
    // the knees, a seated thigh's length out along the edge it faces, reach past the end, so the legs never hang over the box's face
    const thigh = (1.35 - 0.79) * (112 / 5.4) * Math.sin((70 * Math.PI) / 180);
    expect(SEAT_INBOARD * 112).toBeLessThan(thigh);
    expect(SEAT_INBOARD * 112).toBeGreaterThan(0.04 * 112);
    expect([right.face, left.face, right.posture]).toEqual([70, 290, "sit"]);
});

const {TYPING, typingIn, typingSpell} = await import("../src/figure/reactions.js");
const {hornOpen, partOf} = await import("../src/figure/acts.js");
const {GLANCE, HEAD_TURN, TUMBLE} = await import("../src/figure/figure.js");

// the way the head and the chest face, in degrees toward the viewer's right, of a pose
const facingsOf = (pose) => {
    const moves = pose.moves(0);
    const yaw = (bone) => {
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(moves.get(bone));
        return THREE.MathUtils.radToDeg(Math.atan2(ahead.x, -ahead.y));
    };
    return {head: yaw("head"), chest: yaw("chest")};
};
const posedAt = (name, voice, t) => {
    const pose = new Posing(RIG, "stand", 0);
    clipNamed(name).pose(pose, stanceOf(voice), t);
    return pose;
};

test("blown, the party horn shoots open at once, stays open over a second, rolls back up a little slower, the head turned to the side", () => {
    const {frames, fps, opens, rolls} = ACTS.party_horn;
    const seconds = (share) => (share * frames) / fps;
    expect(seconds(opens[1] - opens[0])).toBeLessThan(0.2);
    expect(seconds(rolls[0] - opens[1])).toBeGreaterThanOrEqual(1);
    expect(seconds(rolls[0] - opens[1])).toBeLessThanOrEqual(1.5);
    expect(seconds(rolls[1] - rolls[0])).toBeGreaterThan(seconds(opens[1] - opens[0]));
    expect(hornOpen((opens[1] + rolls[0]) / 2)).toBe(1);
    expect([hornOpen(0), hornOpen(1)]).toEqual([0, 0]);
    for (const voice of Object.keys(stances)) {
        const {head, chest} = facingsOf(posedAt("party_horn", voice, (opens[1] + rolls[0]) / 2));
        expect(Math.abs(head - chest), voice).toBeGreaterThan(35);
    }
});

test("now and then an edit sets the figure typing for a spell it is plainly seen at, kept while its agent works on, and not again too soon", () => {
    const spell = typingSpell("writing", null, 100, () => 0);
    expect(spell.until - spell.began).toBeGreaterThanOrEqual(TYPING.seconds[0]);
    expect(TYPING.odds).toBeLessThan(1);
    // the edit is over and the agent thinks or reads: the figure types on; once the agent waits or idles, it stops
    expect(typingIn({state: "thinking", since: 103}, spell, 105)).toEqual({state: "writing", since: 100});
    expect(typingIn({state: "reading", since: 103}, spell, 105).state).toBe("writing");
    expect(typingIn({state: "waiting", since: 103}, spell, 105).state).toBe("waiting");
    expect(typingIn({state: "thinking", since: 103}, spell, spell.until).state).toBe("thinking");
    // a lost roll, and the cooldown after a spell, hold the next one back
    const lost = typingSpell("writing", null, 100, () => 0.99);
    expect(lost).toEqual({began: 0, until: 0, next: 100 + TYPING.cooldown});
    expect(typingSpell("writing", lost, 110, () => 0)).toBe(lost);
    expect(typingSpell("writing", spell, spell.until + 1, () => 0)).toBe(spell);
    expect(typingSpell("writing", spell, 100 + TYPING.cooldown, () => 0).began).toBe(100 + TYPING.cooldown);
    expect(typingSpell("thinking", null, 100, () => 0)).toBe(null);
});

test("standing still, the figure now and then glances left, right or up, its head within HEAD_TURN of its body, the body turning past that", () => {
    const standing = REACTIONS.find((each) => each.moment === "standing");
    expect(standing.among.map((each) => each.clip)).toEqual(["look_left", "look_right", "look_up"]);
    expect([standing.odds < 1, standing.cooldown > 0]).toEqual([true, true]);
    for (const voice of Object.keys(stances)) {
        for (const [name, way] of [["look_left", -1], ["look_right", 1]]) {
            const {head, chest} = facingsOf(posedAt(name, voice, 0.5));
            expect(Math.abs(head - chest), `${voice} ${name}`).toBeLessThanOrEqual(HEAD_TURN);
            expect(Math.sign(head), `${voice} ${name}`).toBe(way);
            expect(Math.abs(head), `${voice} ${name}`).toBeGreaterThan(HEAD_TURN);
        }
        const up = posedAt("look_up", voice, 0.5);
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(up.moves(0).get("head"));
        expect(ahead.z, voice).toBeGreaterThan(0.2);
        expect(GLANCE.frames / GLANCE.fps).toBeLessThanOrEqual(2.5);
    }
});

test("very rarely, landing from a launch, the figure trips onto its knees, shakes its head and gets up, never through the floor", () => {
    const launched = REACTIONS.find((each) => each.moment === "launched");
    expect([launched.clip, launched.odds <= 0.1, launched.cooldown >= 120]).toEqual(["tumble", true, true]);
    for (const voice of Object.keys(stances)) {
        const kneeling = posedAt("tumble", voice, 0.4);
        const moves = kneeling.moves(0);
        const at = (name) => kneeling.head(name, moves.get(name));
        for (const side of ["l", "r"]) expect(at(`shin_${side}`).z, voice).toBeLessThan(0.2);
        for (let frame = 0; frame < TUMBLE.frames; frame++) {
            const pose = posedAt("tumble", voice, frame / TUMBLE.frames);
            const all = pose.moves(0);
            // the root is the rig's origin, under the body, not a part of it
            for (const name of RIG.order.filter((bone) => bone !== "root")) expect(pose.head(name, all.get(name)).z, `${voice} ${frame} ${name}`).toBeGreaterThan(-0.12);
        }
    }
});

test("falls are snappy: the tumble drops to its knees in a quarter of a second with a quick bounce, and a landing is over in a third of one", () => {
    const seconds = ([from, to]) => ((to - from) * TUMBLE.frames) / TUMBLE.fps;
    expect(seconds(TUMBLE.down)).toBeLessThanOrEqual(0.3);
    expect(seconds(TUMBLE.bounce)).toBeLessThanOrEqual(0.3);
    expect(TUMBLE.bounce[0]).toBe(TUMBLE.down[1]);
    const land = clipNamed("land");
    expect(land.frames / land.fps).toBeLessThanOrEqual(0.35);
});

test("the head holds its turn to the side, unmoved, from the party horn's first frame up to its last, for every voice, the horn being flat", () => {
    const {frames, raise, lower, turn} = ACTS.party_horn;
    // the page draws the horn while it is raised and not yet lowered (chat/FigureAct.vue horn.up)
    const shown = (u) => partOf(u, raise) * (1 - partOf(u, lower)) > 0;
    for (const voice of Object.keys(stances)) {
        const held = [];
        for (let step = 0; step <= frames * 4; step++) {
            const u = step / (frames * 4);
            if (!shown(u)) continue;
            const {head, chest} = facingsOf(posedAt("party_horn", voice, u * (frames - 1) / frames));
            held.push(head - chest);
        }
        expect(held.length, voice).toBeGreaterThan(frames);
        expect(Math.max(...held) - Math.min(...held), voice).toBeLessThan(0.5);
        expect(Math.abs(held[0]), voice).toBeGreaterThan(turn / 2);
    }
});
