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

const ACTED = ["phone_call", "ask_sign", "scroll", "file_card", "hand_rub"];
const NEW = ["inspect", "ledge_sit", "look_left", "look_right", "look_up", "tumble", "fume", "eager", "pack_box", "press", "vacuum", "binoculars", "flashlight", "peek_under", "type_ponder", "wipe_brow", "wave_up"];

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

const {pastimeFor, reactionTo, variantOf, workMoments} = await import("../src/figure/reactions.js");
const {PILE} = await import("../src/figure/pile.js");

// the pile's entries of a moment, those that play something, the chance that one does, and the moment's cooldown
const of = (moment) => PILE.filter((entry) => entry.when.moment === moment);
const played = (moment) => of(moment).filter((entry) => entry.kind !== "nothing");
const oddsOf = (moment) => played(moment).reduce((sum, entry) => sum + entry.weight, 0) / of(moment).reduce((sum, entry) => sum + entry.weight, 0);
const cooldownOf = (moment) => played(moment)[0].cooldown;
const {beatsAfter, sayingsAfter, withSystemCards} = await import("../src/domain/figureState.js");

const JOURNAL = {
    task_finished: ["nod", "joy"],
    question_asked: ["ask_sign"],
    reported: ["scroll"],
    fact_filed: ["file_card"],
    check_passed: ["joy"],
};

const at = (seconds) => new Date(seconds * 1000).toISOString();
const message = (id, author, text, data = {}, session = null) => ({table: "messages", id, author, text, data, session, created_at: at(10 + id)});

test("each thing the agent does in the journal is its own moment, read from the chat's messages as the server writes them, and nothing else is", () => {
    const agent = {session: "s", data: {}};
    const messages = [
        message(1, "system", "Finished task 12: the stamp", {icon: "todos", tone: "good"}),
        // a new task is no longer acted out (task 2647)
        message(2, "system", "Started task 13: the parser", {icon: "todos", tone: ""}),
        message(3, "system", "Filed task 14 from your message", {icon: "inbox"}),
        message(4, "system", "Which one?", {kind: "question", process: "question"}, "s"),
        message(5, "system", "Worker 57, Mr. Muybridge, motion photographer: started on claude opus", {icon: "agents", tone: ""}),
        message(6, "system", "Fact 15 recorded", {icon: "check", tone: "good"}),
        message(7, "system", "Reminder 16 recorded", {icon: "check", tone: "good"}),
        message(8, "system", "Check Check for sins passed", {icon: "check", tone: "good"}),
        message(9, "system", "Resumed task 13: the parser", {icon: "todos", tone: ""}),
        message(10, "system", "Worker 57, Mr. Muybridge, motion photographer: released", {icon: "agents", tone: ""}),
        message(11, "system", "Finished task 99 in another session", {icon: "todos", tone: "good"}, "other"),
        message(12, "agent", "Done: the figure stamps now.", {}, "s"),
        message(13, "agent", "Worker 57 reports: done", {kind: "report"}),
        message(14, "agent", "thinking it over", {kind: "thought"}, "s"),
        message(15, "agent", "a reply in another session", {}, "other"),
        message(16, "user", "thanks", {}),
        // a worker sent off or a message the agent sends: a worker's next job, its start again, a note sent it in its session, a message to
        // another session
        message(17, "system", "Worker 57, Mr. Muybridge, motion photographer: sent its next job", {kind: "card", icon: "agents", tone: ""}),
        message(18, "system", "Worker 48, Mr. Sheraton, joiner of panels: sent a message in its session", {kind: "card", icon: "agents", tone: ""}),
        message(21, "system", "Worker 48, Mr. Sheraton, joiner of panels: started again in its last session", {kind: "card", icon: "agents", tone: ""}),
        message(19, "system", "From the main agent, about the output", {kind: "peer", sent_to: "45-mr-faraday", address: "45-mr-faraday"}),
        // a message from another session is not one the agent sends
        message(20, "system", "Drafted: the reader is committed", {kind: "peer", asks: "x", peer: "code-commandments-e1"}),
    ];
    const lead = withSystemCards(agent, messages);
    const beats = [...beatsAfter(lead, 0), ...sayingsAfter(lead, messages, 0)].map((fire) => [fire.beat, fire.card]);
    expect(beats).toEqual([
        ["task_finished", "messages:1"],
        ["question_asked", "messages:4"],
        ["messaged", "messages:5"],
        ["fact_filed", "messages:6"],
        ["fact_filed", "messages:7"],
        ["check_passed", "messages:8"],
        ["messaged", "messages:17"],
        ["messaged", "messages:18"],
        ["messaged", "messages:19"],
        ["messaged", "messages:21"],
        ["reported", "messages:13"],
    ]);
    // a message seen at the last look is not a moment again
    expect(sayingsAfter(lead, messages, 10 + 13)).toEqual([]);
});

test("each journal moment is acted out now and then, never every time: it plays on a winning roll only, and not again before its cooldown", () => {
    for (const [moment, acts] of Object.entries(JOURNAL)) {
        expect(oddsOf(moment), moment).toBeLessThan(1);
        expect(cooldownOf(moment), moment).toBeGreaterThanOrEqual(60);
        const memory = new Map();
        expect(reactionTo(moment, memory, 1000, () => oddsOf(moment)), moment).toBe(null);
        expect(acts, moment).toContain(reactionTo(moment, memory, 1000, () => 0).clip);
        expect(reactionTo(moment, memory, 1000 + cooldownOf(moment) - 1, () => 0), moment).toBe(null);
        expect(reactionTo(moment, memory, 1000 + cooldownOf(moment), () => 0)?.clip, moment).toEqual(expect.any(String));
    }
});

// every entry of a moment a draw may land on, each at the roll that lands on it, `nothing` among them
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
    // the journal moments, the celebrations, the breaks from the hammering and the glances from standing still; a message sent is the
    // telephone call alone (figureCall.test.js)
    // a pass, a passed check and a commit are celebrated by the jump for joy alone
    const joyAlone = ["check_passed", "tests_passed", "committed"];
    for (const moment of [...Object.keys(JOURNAL), "tests_passed", "committed", "building", "standing"]) {
        expect(played(moment).length, moment).toBeGreaterThan(joyAlone.includes(moment) ? 0 : 1);
        expect(picks(of(moment), (random) => reactionTo(moment, new Map(), 0, random)?.clip ?? "nothing"), moment).toEqual(of(moment).map((each) => each.name));
    }
    expect(workMoments("building", false, 0, 5).moments).toEqual([{beat: "building", time: 5}]);
    // searching, typing and watching the UFO, each picked again for each stretch
    expect(of("held:search").map((each) => each.name)).toEqual(["search", "binoculars", "flashlight", "peek_under"]);
    for (const clip of ["search", "type", "watch", "compacting"]) {
        const among = of(`held:${clip}`);
        expect(among.length, clip).toBeGreaterThan(1);
        expect(among.map((each) => each.name), clip).toContain(clip);
        expect(picks(among, (random) => variantOf(clip, random, has)), clip).toEqual(among.map((each) => each.name));
        expect(variantOf(clip, () => 0.99, (name) => name === clip), clip).toBe(clip);
    }
    expect(variantOf("idle", () => 0, has)).toBe("idle");
    // the figure at rest has more idle acts than one
    expect(new Set(played("pastime").filter((each) => each.when.free && !each.when.voices).map((each) => each.name)).size).toBeGreaterThan(2);
});

const {SKYWARD, goneMs, skywardAt, skywardHops, skywardMs} = await import("../src/figure/skyward.js");
const {fallStep} = await import("../src/domain/falls.js");
const {chuteFrom} = await import("../src/domain/figureMotion.js");
const {clipFor} = await import("../src/domain/figureState.js");
const {ACTS, heldPhases, squeezeOf} = await import("../src/figure/acts.js");

test("now and then while idle the figure hops up the bubbles above it very fast, off the top of the screen, and stays gone one to five seconds", () => {
    const pastime = of("pastime").find((each) => each.flies);
    expect([pastime.name, pastime.shenanigan, oddsOf("pastime") < 1]).toEqual(["hop_up", true, true]);
    // a shenanigan, played in any state, a wait on a run, a worker or the user, or work, as much as idle (messages 40669, 40680, 41809)
    const has = (name) => name === "hop_up";
    for (const state of ["idle", "waiting", "asking", "thinking"]) {
        const scene = {voice: "butler", place: {posture: "stand"}, beats: 0, arriving: false, leaving: false, moving: false};
        expect(pastimeFor(scene, {state, lasted: 0}, new Map(), 0, () => 0, has), state).toEqual({clip: "hop_up", card: "", flies: true});
    }
    // the run ends over the chat's top, past which the figure is not drawn
    const hops = skywardHops({x: 300, y: 700}, [{x: 340, y: 560}, {x: 260, y: 400}, {x: 330, y: 260}], 40);
    expect(hops.map((hop) => hop.to.y)).toEqual([560, 400, 260, 40]);
    // each hop goes up, and a hop of the figure's height takes well under half a second
    for (const hop of hops) expect(hop.to.y).toBeLessThan(hop.from.y);
    expect(skywardHops({x: 0, y: 112}, [], 0)[0].ms).toBeLessThan(500);
    for (let ms = 20; ms < skywardMs(hops); ms += 20) expect(skywardAt(hops, ms, 112).gone).toBe(false);
    expect(skywardAt(hops, skywardMs(hops), 112)).toMatchObject({y: 40, gone: true});
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
    expect(of("held:compacting").map((each) => each.name)).toEqual(["pack_box", "press", "vacuum", "compacting"]);
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
    expect(eagerFor(at(0.8), null, () => oddsOf("eager"), 120).eager).toEqual({run: 100, on: false});
    const eager = eagerFor(at(0.8), null, () => 0, 120).eager;
    expect(eager).toEqual({run: 100, on: true});
    expect(eagerFor(at(0.95), {run: 100, on: false}, () => 0, 123).eager.on).toBe(false);
    // a quick run, under ten seconds old when it nears its end, never makes it eager
    expect(eagerFor(at(0.6), null, () => 0, 100 + EAGER.after - 4).eager).toEqual({run: 100, on: false});
    // started, it is kept to the end whatever the figure does, and then it is cheered or fumed at
    expect(eagerFor(at(0.97), eager, () => 0.99, 124)).toEqual({eager, moment: null});
    expect(eagerFor(at(1, "good"), eager, () => 0, 125)).toEqual({eager: {run: 100, on: false}, moment: {beat: "bar_done"}});
    expect(eagerFor(at(1, "bad"), eager, () => 0, 125).moment).toEqual({beat: "bar_failed"});
    // the dock drawn again, with a new bar for the same run, is still that run: its end is fumed at once, never again
    const fumed = eagerFor(at(1, "bad"), eager, () => 0, 125).eager;
    const redrawn = (share, ended = "") => ({bar: {}, share, ended, began: 100});
    expect(eagerFor(redrawn(0.97), fumed, () => 0, 126)).toEqual({eager: fumed, moment: null});
    expect(eagerFor(redrawn(1, "bad"), fumed, () => 0, 127).moment).toBe(null);
    expect(reactionTo("bar_failed", new Map(), 0, () => 0.99).clip).toBe("fume");
    expect(of("bar_done").map((each) => each.name)).toEqual(["joy"]);
    // only the bar going ends it with nothing to mark
    expect(eagerFor(null, eager, () => 0, 126)).toEqual({eager: {run: 100, on: false}, moment: null});
    expect(clipFor({place: {posture: "stand"}, eager: true, state: "running", doing: "think"}, () => true).clip).toBe("eager");
});

test("a run gone over two minutes is always anticipated near its end, whatever the roll: the figure cuts off any act and goes to the mark; a shorter run is left to the odds", async () => {
    const {givesWay} = await import("../src/figure/pile.js");
    const {eagerSpot} = await import("../src/figure/perches.js");
    const {boxed} = await import("./support/figurePage.js");
    // a run that began at 100, five seconds or less from its end at its pace when the figure looks
    const nearEnd = (seconds) => ({bar: {}, share: 1 - 4 / (seconds + 4), ended: "", began: 100});
    expect(secondsLeft(121, nearEnd(121).share)).toBeLessThan(EAGER.lead);
    for (const roll of [0, 0.5, 0.999]) expect(eagerFor(nearEnd(121), null, () => roll, 100 + 121).eager, `${roll}`).toEqual({run: 100, on: true, urgent: true});
    // a minute's run rolls the odds as ever: eager on a winning roll, not on a losing one, and never urgent
    expect(eagerFor(nearEnd(60), null, () => 0, 100 + 60).eager).toEqual({run: 100, on: true});
    expect(eagerFor(nearEnd(60), null, () => 0.999, 100 + 60).eager).toEqual({run: 100, on: false});
    // the act in hand gives way at once to the urgent trip, even one that plays out otherwise, as the disco does and a fresh act
    for (const name of ["disco", "phone_call", "rope_swing", "joy"]) {
        const shown = {once: true, clip: {name}};
        expect(givesWay(shown, 0.1, {urgent: true}), name).toBe(true);
        expect(givesWay(shown, 0.1, {pressing: true}), name).toBe(false);
        expect(givesWay(shown, 0.1), name).toBe(false);
    }
    // and it goes to the mark docked over the compose box, from wherever it is, staying there once it is on it
    const bars = boxed({left: 300, right: 700, top: 540, bottom: 600});
    const scroll = {...boxed({left: 200, top: 100, right: 900, bottom: 540}), querySelectorAll: () => []};
    const thread = {...boxed({left: 200, top: 100, right: 900, bottom: 800}), querySelector: (selector) => (selector === ".thread-scroll" ? scroll : selector === "[data-figure-docked-bars]" ? bars : null)};
    const home = {...boxed({left: 300, right: 700, top: 600, bottom: 720}), closest: () => thread};
    globalThis.window = {innerWidth: 1280, innerHeight: 800};
    globalThis.CSS = {escape: (text) => text};
    globalThis.document = {querySelector: (selector) => (selector === "[data-figure-home]" ? home : null), querySelectorAll: () => []};
    const spot = eagerSpot({x: 400, y: 600, on: home}, {size: 112, below: 0.05});
    expect(spot).toMatchObject({y: 540, on: bars});
    expect(eagerSpot(null, {size: 112, below: 0.05})).toMatchObject({y: 540, on: bars});
    expect(eagerSpot(spot, {size: 112, below: 0.05})).toBe(null);
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
const {LEGS} = await import("../src/figure/figure.js");

test("at a corner the figure lounges back from the end on the top, side-on with its legs straight out along the floor away from the end and hands flat on the floor behind", () => {
    const box = {left: 100, width: 400, top: 300};
    const figure = {size: 112};
    const right = seatAt(box, "right", figure);
    const left = seatAt(box, "left", figure);
    expect([right.x, left.x]).toEqual([500 - SEAT_INBOARD * 112, 100 + SEAT_INBOARD * 112]);
    expect([right.face, left.face, right.posture]).toEqual([270, 90, "lounge"]);
    for (const voice of Object.keys(stances)) {
        const pose = new Posing(RIG, "lounge", 0);
        LEGS.lounge.under(pose);
        clipNamed("idle").pose(pose, stanceOf(voice), 0);
        LEGS.lounge.over(pose);
        const moves = pose.moves(0);
        const at = (bone) => pose.head(bone, moves.get(bone));
        for (const side of ["l", "r"]) {
            if (!stanceOf(voice).free.has(side)) continue;
            // the feet out ahead of the hips, along the floor as it lies side-on, and up level with them, the hands behind the hips and down at the floor line
            expect(at(`foot_${side}`).y, `${voice} foot`).toBeLessThan(at(`thigh_${side}`).y - 0.6);
            expect(Math.abs(at(`foot_${side}`).z - at(`thigh_${side}`).z), `${voice} foot level`).toBeLessThan(0.45);
            expect(at(`hand_${side}`).y, `${voice} hand`).toBeGreaterThan(at(`thigh_${side}`).y);
            expect(at(`hand_${side}`).z, `${voice} hand low`).toBeLessThan(at(`thigh_${side}`).z + 0.35);
        }
    }
});

const {SPELL, spellFor, spellIn} = await import("../src/figure/reactions.js");
const {hornOpen, partOf} = await import("../src/figure/acts.js");
const {GLANCE, TUMBLE} = await import("../src/figure/figure.js");

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

test("now and then an edit, a read or a search sets the figure at its work for a spell it is plainly seen at, kept while its agent works on, and not again too soon", () => {
    const spell = spellFor("writing", null, 100, () => 0);
    expect(spell.state).toBe("writing");
    expect(spell.until - spell.began).toBeGreaterThanOrEqual(SPELL.seconds[0]);
    // the work's own acts, each only while that work goes on, weighted heavily (message 41805)
    for (const state of SPELL.kept) {
        expect(spellFor(state, null, 100, () => 0).state, state).toBe(state);
        expect(oddsOf("spell") > 0.5 && played("spell").find((each) => each.name === state).when.state === state, state).toBe(true);
    }
    // the edit is over and the agent thinks or reads: the figure types on; once the agent waits or idles, it stops
    expect(spellIn({state: "thinking", since: 103}, spell, 105)).toEqual({state: "writing", since: 100});
    expect(spellIn({state: "reading", since: 103}, spell, 105).state).toBe("writing");
    expect(spellIn({state: "waiting", since: 103}, spell, 105).state).toBe("waiting");
    expect(spellIn({state: "thinking", since: 103}, spell, spell.until).state).toBe("thinking");
    // a lost draw, and the wait after a spell, hold the next one back
    const lost = spellFor("writing", null, 100, () => 0.99);
    expect(lost).toEqual({state: "writing", began: 0, until: 0, next: 100 + SPELL.every});
    expect(spellFor("writing", lost, 110, () => 0)).toBe(lost);
    expect(spellFor("writing", spell, spell.until + 1, () => 0)).toBe(spell);
    expect(spellFor("writing", spell, 100 + SPELL.every, () => 0).began).toBe(100 + SPELL.every);
    expect(spellFor("thinking", null, 100, () => 0)).toBe(null);
});

test("standing still, the figure now and then glances a little to one side or up and holds it a moment, never sweeping left and right", () => {
    expect(played("standing").map((each) => each.name)).toEqual(["look_left", "look_right", "look_up"]);
    expect([oddsOf("standing") <= 0.15, cooldownOf("standing") >= 10]).toEqual([true, true]);
    for (const voice of Object.keys(stances)) {
        for (const [name, way] of [["look_left", -1], ["look_right", 1]]) {
            const {head, chest} = facingsOf(posedAt(name, voice, 0.5));
            expect(Math.sign(head), `${voice} ${name}`).toBe(way);
            expect(Math.abs(head), `${voice} ${name}`).toBeLessThanOrEqual(30);
            expect(Math.abs(chest), `${voice} ${name}`).toBeLessThan(Math.abs(head));
            const {head: held} = facingsOf(posedAt(name, voice, 0.3));
            expect(Math.abs(held - head), `${voice} ${name} is held still in its middle`).toBeLessThan(1);
        }
        const up = posedAt("look_up", voice, 0.5);
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(up.moves(0).get("head"));
        expect(ahead.z, voice).toBeGreaterThan(0);
    }
    expect(GLANCE.frames / GLANCE.fps).toBeLessThanOrEqual(3);
});

test("the butler tips the top hat he wears: it leaves his head while it is in his hand, and there is no second hat to lift", () => {
    const tipped = posedAt("hat_tip", "butler", 0.5);
    expect([tipped.stowed.has("butler_top_hat"), tipped.stowed.has("butler_top_hat_band"), tipped.props.has("top_hat")]).toEqual([true, true, true]);
    expect([...tipped.props.keys()].some((name) => name.includes("bowler"))).toBe(false);
    const before = posedAt("hat_tip", "butler", 0.05);
    expect([before.stowed.has("butler_top_hat"), before.props.has("top_hat")]).toEqual([false, false]);
});

test("very rarely, landing from a launch, the figure trips onto its knees, shakes its head and gets up, never through the floor", () => {
    expect([played("launched").map((each) => each.name), oddsOf("launched") <= 0.1, cooldownOf("launched") >= 120]).toEqual([["tumble"], true, true]);
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

const {VISOR, crtAt, glowTurn} = await import("../src/figure/visor.js");
const {turnToViewer} = await import("../src/figure/figure.js");

test("while the visor glows the figure turns toward the viewer, partly and never head on, held all the glow long, from every facing, for every voice", () => {
    // the head's way from the viewer, in degrees, for a figure turned `facing` degrees, posed and turned toward the viewer `strength` of the way
    const fromViewer = (voice, facing, strength) => {
        const pose = posedAt("idle", voice, 0.3);
        turnToViewer(pose, facing, strength);
        const moves = pose.moves(facing);
        const ahead = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("head"));
        const chest = new THREE.Vector3(0, -1, 0).transformDirection(moves.get("chest"));
        const yaw = (way) => THREE.MathUtils.radToDeg(Math.atan2(way.x, -way.y));
        return {away: Math.abs(yaw(ahead)), apart: Math.abs(((yaw(ahead) - yaw(chest) + 540) % 360) - 180)};
    };
    const glow = [];
    for (let seconds = VISOR.eyesOut; seconds < VISOR.seconds - VISOR.eyesBack; seconds += 0.05) glow.push(glowTurn(crtAt(seconds)));
    expect(glow.every((strength) => strength === 1)).toBe(true);
    for (const voice of Object.keys(stances)) {
        for (const facing of [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]) {
            const sideways = Math.abs(((facing + 180) % 360) - 180);
            const unturned = fromViewer(voice, facing, 0).away;
            const held = glow.map((strength) => fromViewer(voice, facing, strength));
            const label = `${voice} ${facing}`;
            // held the same all the glow long
            expect(Math.max(...held.map((each) => each.away)) - Math.min(...held.map((each) => each.away)), label).toBeLessThan(0.5);
            const {away, apart} = held[0];
            // the head within its turn of the body
            expect(apart, label).toBeLessThanOrEqual(65.5);
            if (sideways === 0) continue;
            // turned toward the viewer, at least a little, and never quite head on
            expect(unturned - away, label).toBeGreaterThan(Math.min(sideways * 0.5, 20));
            expect(away, label).toBeGreaterThan(1);
        }
    }
});

test("tickled, each swat goes at the pointer: the hand on the pointer's side reaches toward it, left or right, high or low", () => {
    const handAt = (at, side) => {
        const pose = new Posing(RIG, "stand", 0);
        pose.at = at;
        clipNamed("tickle_swat").pose(pose, stanceOf("butler"), 0.125);
        const moves = pose.moves(0);
        return pose.head(`hand_${side}`, moves.get(`hand_${side}`));
    };
    const hands = (at) => ["l", "r"].map((side) => handAt(at, side));
    const [leftHigh, rightHigh, leftLow, rightLow] = [{x: 0.1, y: 0.2}, {x: 0.9, y: 0.2}, {x: 0.1, y: 0.7}, {x: 0.9, y: 0.7}].map((at) => hands({...at, amount: 1}));
    const reaching = (pair) => (Math.abs(pair[0].x) > Math.abs(pair[1].x) ? pair[0] : pair[1]);
    // the reaching hand is on the pointer's side, and higher for a pointer above than below
    expect(Math.sign(reaching(leftHigh).x)).not.toBe(Math.sign(reaching(rightHigh).x));
    expect(reaching(leftHigh).z).toBeGreaterThan(reaching(leftLow).z);
    expect(reaching(rightHigh).z).toBeGreaterThan(reaching(rightLow).z);
});

test("the swat goes on for as long as the pointer keeps tickling, past one play of it, and ends soon after the pointer stops", async () => {
    const {UNTICKLED, movedTo, tickling, TICKLE} = await import("../src/figure/tickle.js");
    const swat = clipNamed("tickle_swat");
    const playMs = (swat.frames / swat.fps) * 1000;
    let pointer = UNTICKLED;
    const held = [];
    let last = 0;
    for (let at = 0; at <= TICKLE.prolonged + playMs * 3; at += 120) {
        pointer = movedTo(pointer, 400 + (Math.floor(at / 120) % 2 ? 30 : 0), at);
        if (at >= TICKLE.within + TICKLE.prolonged) held.push(tickling(pointer, at));
        last = at;
    }
    // at every moment past the first play, so whenever a swat ends, the tickle still holds and the swat starts again
    expect(held.length).toBeGreaterThan(10);
    expect(held.every(Boolean)).toBe(true);
    expect(tickling(pointer, last + TICKLE.lingers + 1)).toBe(false);
});

test("a move that overshoots the figure still tickles it: the pointer counts within its reach round the body, and nowhere further", async () => {
    const {TICKLE, nearBody} = await import("../src/figure/tickle.js");
    const body = {left: 100, right: 160, top: 200, bottom: 300};
    expect(nearBody(body, 130, 250)).toBe(true);
    expect(nearBody(body, 160 + TICKLE.reach - 1, 250)).toBe(true);
    expect(nearBody(body, 100 - TICKLE.reach + 1, 199)).toBe(true);
    expect(nearBody(body, 160 + TICKLE.reach + 1, 250)).toBe(false);
    expect(TICKLE.reach).toBeGreaterThanOrEqual(30);
});

test("the jump for joy lasts three to four and a half seconds, a few jumps, and plays out", async () => {
    const {CLIPS} = await import("../src/figure/figure.js");
    const {cutsAfter} = await import("../src/figure/pile.js");
    const joy = CLIPS.find((clip) => clip.name === "joy");
    const seconds = joy.frames / joy.fps;
    expect(seconds).toBeGreaterThanOrEqual(3);
    expect(seconds).toBeLessThanOrEqual(4.5);
    expect(ACTS.joy.jumps).toBeGreaterThanOrEqual(3);
    expect(cutsAfter("joy", seconds), "no following beat cuts it short").toBe(false);
});

test("a finished task now and then brings the hands rubbed together before the chest, sliding round each other, with a little nod", async () => {
    const {choicesFor} = await import("../src/figure/pile.js");
    const {ACTS} = await import("../src/figure/acts.js");
    const rub = choicesFor({moment: "task_finished"}).find((entry) => entry.name === "hand_rub");
    expect(rub.weight).toBeGreaterThanOrEqual(3);
    const clip = clipNamed("hand_rub");
    // about two seconds
    expect(clip.frames / clip.fps).toBeGreaterThan(1.8);
    expect(clip.frames / clip.fps).toBeLessThan(2.6);
    const act = ACTS.hand_rub;
    for (const voice of Object.keys(stances)) {
        const across = new Set();
        const over = new Set();
        for (let frame = 0; frame < clip.frames; frame++) {
            const t = frame / clip.frames;
            const u = (t * clip.frames) / (clip.frames - 1);
            if (u <= act.together[1] || u >= act.apart[0]) continue;
            const pose = new Posing(RIG, "stand", 0);
            clip.pose(pose, stanceOf(voice), t);
            const moves = pose.moves(0);
            const at = (name) => pose.head(name, moves.get(name));
            const [left, right, chest] = [at("hand_l"), at("hand_r"), at("chest")];
            const label = `${voice} ${frame}`;
            // the hands together, before the chest at its height
            expect(left.distanceTo(right), label).toBeLessThan(0.75);
            for (const hand of [left, right]) {
                expect(hand.y, label).toBeLessThan(chest.y - 0.3);
                expect(Math.abs(hand.z - chest.z), label).toBeLessThan(0.5);
            }
            across.add(Math.sign(Math.round((left.x - right.x) * 100)));
            over.add(Math.sign(Math.round((left.z - right.z) * 100)));
        }
        // sliding round each other: each passes the other, over and under, as they rub
        expect(over.has(1) && over.has(-1), voice).toBe(true);
        expect(across.size, voice).toBeGreaterThan(1);
    }
});
