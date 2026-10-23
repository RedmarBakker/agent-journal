// @vitest-environment node
import {describe, expect, it} from "vitest";
import {CLIPS} from "../src/figure/figure.js";
import {givesWay} from "../src/figure/pile.js";
import {EAGER, answerTo, eagerFor, isListening, playedFrom, queuedFirst, queues, stillGoing, workMoments} from "../src/figure/reactions.js";

const named = Object.fromEntries(CLIPS.map((clip) => [clip.name, clip]));
const memoryOf = () => ({reacted: new Map(), played: [], tally: {plain: 0, last: ""}});
const has = () => true;

// the thinking act as the figure answers a look while the agent thinks, at `now`
function thinkingAct(memory, now) {
    const moment = workMoments("thinking", false, 0, now).moments.find((each) => each.beat === "pondering");
    return answerTo(moment, "butler", memory, now, () => 0, has)?.beat;
}

describe("the thinking act and the queue", () => {
    it("ends with the thinking: started while the agent thinks, it is gone from the queue and broken off the moment the thinking ends", () => {
        const act = thinkingAct(memoryOf(), 1000);
        expect(act.during).toBe("thinking");
        let beats = [act, {clip: "nod", card: ""}];
        const thinking = stillGoing(beats, "thinking", act.clip);
        expect([thinking.beats, thinking.cut], "while it thinks it plays on").toEqual([beats, false]);
        const ended = stillGoing(beats, "writing", act.clip);
        expect(ended.beats.map((beat) => beat.clip), "gone once the thinking ends").toEqual(["nod"]);
        expect(ended.cut, "broken off on screen, its bulb never reached").toBe(true);
        beats = ended.beats;
        expect(stillGoing([act], "idle", "").cut, "and dropped unplayed when it only waited").toBe(false);
        expect(stillGoing([act], "idle", "").beats).toEqual([]);
    });

    it("is never queued twice: another play while one for the thinking waits or plays is not queued", () => {
        const memory = memoryOf();
        const act = thinkingAct(memory, 1000);
        const again = {...act};
        expect(queues([act], again)).toBe(false);
        expect(queues([], again)).toBe(true);
        expect(queues([act], {clip: "nod", card: ""}), "other beats queue as ever").toBe(true);
    });

    it("interrupted, it is dropped and never queued again: the interruption plays, then what waited behind, never the act", () => {
        const act = thinkingAct(memoryOf(), 1000);
        const swat = {clip: "tickle_swat", card: ""};
        const queued = queuedFirst([act, {clip: "nod", card: ""}], swat, act.clip);
        expect(queued.cut, "the act broken off").toBe(true);
        expect(queued.beats.map((beat) => beat.clip)).toEqual(["tickle_swat", "nod"]);
        const after = playedFrom(queued.beats, "tickle_swat");
        expect(after.map((beat) => beat.clip), "after the swat, the act does not come back").toEqual(["nod"]);
        expect(stillGoing(after, "idle", "nod").beats.some((beat) => beat.clip === act.clip)).toBe(false);
        // a beat that played to its end takes only itself off the queue, never the one that came first meanwhile
        expect(playedFrom([swat, {clip: "nod", card: ""}], act.clip).map((beat) => beat.clip)).toEqual(["tickle_swat", "nod"]);
    });
});

describe("acts that hold", () => {
    it("the anticipation of a run's end plays through whatever comes: no moment is heard while it lasts, and its clip is never cut", () => {
        expect(named.eager.holds, "declared on the act").toBe(true);
        const progress = {share: 0.99, began: 0, ended: ""};
        const eager = eagerFor(progress, null, () => 0, EAGER.long + 1).eager;
        expect(eager.on).toBe(true);
        expect(isListening(eager), "a tickle, a card or a look waits it out").toBe(false);
        for (const seconds of [0.5, 3, 30]) {
            expect(givesWay({clip: named.eager}, seconds), `${seconds}`).toBe(false);
            expect(givesWay({clip: named.eager}, seconds, {urgent: true}), `${seconds} even for a trip that drops everything`).toBe(false);
        }
    });

    it("the celebration after it plays to its end: a first beat that comes meanwhile waits behind it, and it is never cut", () => {
        for (const [moment, tone] of [["bar_done", "good"], ["bar_failed", "bad"]]) {
            const progress = {share: 0.99, began: 0, ended: ""};
            const eager = eagerFor(progress, null, () => 0, EAGER.long + 1).eager;
            const end = eagerFor({...progress, share: 1, ended: tone}, eager, () => 0, EAGER.long + 5);
            expect(end.moment.beat).toBe(moment);
            expect(isListening(end.eager), "listening again once the run has ended").toBe(true);
            const celebration = answerTo(end.moment, "butler", memoryOf(), 0, () => 0, has).beat;
            expect(celebration.holds, `${moment} declared to hold`).toBe(true);
            const swat = {clip: "tickle_swat", card: ""};
            const queued = queuedFirst([celebration], swat, celebration.clip);
            expect(queued.cut, `${moment} not broken off`).toBe(false);
            expect(queued.beats.map((beat) => beat.clip), `${moment} the swat waits behind it`).toEqual([celebration.clip, "tickle_swat"]);
            expect(givesWay({clip: named[celebration.clip], once: true, holds: true}, 60), `${moment} never cut`).toBe(false);
        }
        expect(givesWay({clip: named.nod, once: true}, 1), "an act that does not hold gives way as ever").toBe(true);
    });
});
