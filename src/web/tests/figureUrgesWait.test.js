// @vitest-environment node
import {expect, test} from "vitest";

const {CLIPS} = await import("../src/figure/figure.js");
const {givesWay} = await import("../src/figure/pile.js");
const {EAGER, answerTo, eagerFor, headBeat, heardNow, playedFrom, queuedFirst} = await import("../src/figure/reactions.js");
const {actOver, closeAt, clipFor} = await import("../src/domain/figureState.js");

const has = () => true;
const clipNamed = (name) => CLIPS.find((clip) => clip.name === name);
// the moments answered before any beat waiting, right after the act on screen (VoiceFigure FIRST)
const FIRST = new Set(["long_walk", "tickled", "bar_failed"]);

// The figure's beats played a frame at a time at `fps`, as VoiceFigure's step plays them: what comes is answered and queued, a first beat
// right after the act on screen; a celebration on its chat mark sets off a pressing trip there, which breaks off the act on screen only if
// it gives way (pile.js givesWay), as any other trip; an act that has played to its end is over before what comes next is chosen. `urges`
// are the moments, each at its second. It returns each act as it started and the frame it had reached when it ended.
function played(first, urges, seconds) {
    const fps = 12;
    const memory = {reacted: new Map(), played: []};
    let beats = [first];
    let playing = null;
    let trip = null;
    const acts = [];
    for (let frame = 0; frame <= seconds * fps; frame++) {
        const now = frame / fps;
        for (const moment of urges.filter((urge) => urge.time === now)) {
            const answer = answerTo(moment, "butler", memory, now, () => 0, has);
            if (!answer?.beat) continue;
            beats = FIRST.has(moment.beat) ? queuedFirst(beats, answer.beat, playing?.name ?? "") : [...beats, answer.beat];
            if (answer.beat.onto) trip = {pressing: true};
        }
        const shown = playing && {clip: clipNamed(playing.name), once: true};
        const at = playing ? Math.floor((now - playing.started) * fps) : 0;
        if (shown && trip && givesWay(shown, now - playing.started, trip)) {
            acts.at(-1).reached = at;
            beats = beats.slice(1);
            playing = null;
        }
        if (shown && playing && actOver(shown, at)) {
            acts.at(-1).reached = at;
            beats = playedFrom(beats, playing.name);
            playing = null;
        }
        const head = headBeat(beats, null);
        if (!playing && head) {
            playing = {name: head.clip, started: now};
            acts.push({clip: head.clip, at: now, reached: null});
        }
    }
    return acts;
}

test("a telephone call plays to its last frame while a message and a run's end come during it, and they play after it in the order they came", () => {
    const call = {clip: "phone_call", card: "", mark: "messages:1"};
    const frames = clipNamed("phone_call").frames;
    // a question asked a second in, a run passing two seconds in (its nod off to its mark), and a tickle three seconds in
    const urges = [{beat: "question_asked", time: 1}, {beat: "tests_passed", time: 2, card: "messages:2"}, {beat: "tickled", time: 3}];
    const acts = played(call, urges, 40);
    expect(acts.map((act) => act.clip)).toEqual(["phone_call", "tickle_swat", "ask_sign", "nod"]);
    expect(acts[0].reached, "the call played to its last frame").toBe(frames);
    for (const act of acts) expect(act.reached, `${act.clip} played out`).toBe(clipNamed(act.clip).frames);
});

test("the anticipation of a run's end, once started, plays whole through a user's message and the run failing part way through it, and the look at the message and the fuming come after it", () => {
    const eagerClip = clipNamed("eager");
    const fps = eagerClip.fps;
    const run = {share: 0.99, began: 0, ended: ""};
    let eager = eagerFor(run, null, () => 0, EAGER.long + 1).eager;
    expect(eager).toMatchObject({on: true, urgent: true});
    let anticipated = null;
    let beats = [];
    let started = null;
    let closing = null;
    const frames = [];
    const reacted = [];
    const memory = {reacted: new Map(), played: []};
    let held = [];
    // what the figure answers, as VoiceFigure's react does: nothing while it is eager, what came meanwhile once it listens again
    const react = (...moments) => {
        const listened = heardNow(eager, held, moments);
        held = listened.held;
        for (const moment of listened.answer) {
            const answer = answerTo(moment, "butler", memory, EAGER.long + 1 + frame / fps, () => 0, has);
            reacted.push({beat: moment.beat, answer, at: EAGER.long + 1 + frame / fps});
            if (answer?.beat) beats = queuedFirst(beats, answer.beat, "");
        }
    };
    let frame = 0;
    for (; frame < 30 * fps; frame++) {
        const now = EAGER.long + 1 + frame / fps;
        // the user's message comes half a second into the anticipation, the run fails a second in, long before its hold has played
        if (frame === Math.round(fps / 2)) react({beat: "read_message", time: now, card: "messages:5"});
        // the run fails a second into the anticipation, long before its hold has played
        const bar = now >= EAGER.long + 2 ? {...run, share: 1, ended: "bad"} : run;
        const eagerness = eagerFor(bar, eager, () => 0, now, anticipated === eager?.run);
        eager = eagerness.eager;
        react();
        if (eagerness.moment) react(eagerness.moment);
        const wanted = clipFor({place: {posture: "stand"}, eager: Boolean(eager?.on), state: "running", doing: "idle", beat: headBeat(beats, null)}, has);
        if (started === null && wanted.clip === "eager") started = now;
        if (started === null) continue;
        const index = Math.floor((now - started) * fps);
        if (index >= eagerClip.intro + eagerClip.leaves) anticipated = eager?.run ?? anticipated;
        // wanted no more, the anticipation never gives way: it closes through its outro and only then the fume plays
        if (wanted.clip !== "eager" && closing === null) closing = closeAt(eagerClip, index);
        expect(givesWay({clip: eagerClip}, index / fps, {urgent: true})).toBe(false);
        if (closing !== null && index >= closing + eagerClip.outro) {
            frames.push({clip: wanted.clip, index});
            break;
        }
        frames.push({clip: "eager", index});
    }
    // still eager after the message and the failure, until its hold had played; then the look at the message, then the fume
    expect(reacted.map((each) => each.beat)).toEqual(["read_message", "bar_failed"]);
    expect(reacted[0].answer).toEqual({gaze: {card: "messages:5"}});
    expect(reacted[1].answer.beat.clip).toBe("fume");
    for (const each of reacted) expect(each.at - started).toBeGreaterThanOrEqual((eagerClip.intro + eagerClip.leaves) / fps - 0.1);
    const shown = frames.filter((each) => each.clip === "eager").map((each) => each.index);
    expect(Math.min(...shown), "from its first frame").toBe(0);
    expect(Math.max(...shown), "through its hold and its outro").toBeGreaterThanOrEqual(eagerClip.intro + eagerClip.leaves + eagerClip.outro - 1);
    expect(frames.at(-1).clip, "and then the fume").toBe("fume");
    // a run that ends before the anticipation ever came on screen holds the figure no longer than EAGER wait
    const unseen = eagerFor({...run, share: 1, ended: "bad"}, {run: 0, on: true}, () => 0, 500);
    expect(unseen.moment).toBe(null);
    expect(eagerFor({...run, share: 1, ended: "bad"}, unseen.eager, () => 0, 500 + EAGER.wait).moment).toEqual({beat: "bar_failed"});
});

