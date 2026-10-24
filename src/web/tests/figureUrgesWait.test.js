// @vitest-environment node
import {expect, test} from "vitest";

const {CLIPS} = await import("../src/figure/figure.js");
const {givesWay} = await import("../src/figure/pile.js");
const {EAGER, answerTo, eagerFor, headBeat, heardNow, playedFrom, queuedFirst} = await import("../src/figure/reactions.js");
const {actOver, clipFor} = await import("../src/domain/figureState.js");

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

test("a run that ends at any moment of its anticipation ends the anticipation there: cut at once for the reaction to the end, never still playing after it", () => {
    const eagerClip = clipNamed("eager");
    const fps = eagerClip.fps;
    const start = EAGER.long + 1;
    // a long run three seconds from its end at its pace when the figure looks, past the anticipation's intro's time from it
    const run = {share: start / (start + 3), began: 0, ended: ""};
    // the run ends on each frame of the anticipation, from its first, through its intro, its hold played round, and long after
    for (let end = 0; end <= (eagerClip.intro + 4 * eagerClip.leaves) * 1.5; end++) {
        let eager = eagerFor(run, null, () => 0, start).eager;
        expect(eager).toMatchObject({on: true, urgent: true});
        const memory = {reacted: new Map(), played: []};
        let held = [];
        let beats = [];
        const reacted = [];
        const shown = [];
        for (let frame = 0; frame <= end + 2 * fps; frame++) {
            const now = start + frame / fps;
            const label = `ended on frame ${end}, frame ${frame}`;
            const fresh = frame === Math.round(fps / 2) ? [{beat: "read_message", time: now, card: "messages:5"}] : [];
            const eagerness = eagerFor(frame >= end ? {...run, share: 1, ended: "bad"} : run, eager, () => 0, now);
            eager = eagerness.eager;
            // what it answers, as VoiceFigure's react does: nothing while eager, what came meanwhile once it listens again, then the end
            const listened = heardNow(eager, held, [...fresh, ...(eagerness.moment ? [eagerness.moment] : [])]);
            held = listened.held;
            for (const moment of listened.answer) {
                const answer = answerTo(moment, "butler", memory, now, () => 0, has);
                reacted.push({beat: moment.beat, frame});
                if (answer?.beat) beats = queuedFirst(beats, answer.beat, "");
            }
            const wanted = clipFor({place: {posture: "stand"}, eager: Boolean(eager?.on), state: "running", doing: "idle", beat: headBeat(beats, null)}, has);
            // on screen, as VoiceFigure's step has it: the anticipation while it is wanted; cut at the end, the reaction in its place at once
            const onScreen = shown.at(-1) === "eager" && wanted.clip !== "eager" && !eagerness.cut ? "eager" : wanted.clip;
            shown.push(onScreen);
            if (frame < end) expect(onScreen, label).toBe("eager");
            if (frame === end) expect(eagerness, label).toMatchObject({eager: {on: false}, moment: {beat: "bar_failed"}, cut: true});
            if (frame >= end) expect(onScreen, label).not.toBe("eager");
        }
        // the end reacted to on its own frame, the fume at once, and a message that came while it was eager answered with it, never lost
        expect(reacted.filter((each) => each.beat === "bar_failed")).toEqual([{beat: "bar_failed", frame: end}]);
        expect(shown[end], `ended on frame ${end}`).toBe("fume");
        if (end > Math.round(fps / 2)) expect(reacted.map((each) => each.beat), `ended on frame ${end}`).toEqual(["read_message", "bar_failed"]);
    }
});

