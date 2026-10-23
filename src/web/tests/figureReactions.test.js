// @vitest-environment node
import {expect, test} from "vitest";

const {
    AMBIENT,
    EVERY_VOICE_FACES,
    FLIP_ODDS,
    FLIP_OVER,
    LOOK_SECONDS,
    REACTIONS,
    VARIANTS,
    VOICE_FACES,
    WORKED_SECONDS,
    ambientFor,
    answerTo,
    eyesAt,
    eyesShown,
    flips,
    letsGoFor,
    lookOf,
    pastimeFor,
    reactionTo,
    workMoments,
} = await import("../src/figure/reactions.js");
const {EGGS, HELD, beatsAfter, cardsAfter, facesAfter, sayingsAfter, testResultsAfter} = await import("../src/domain/figureState.js");
const {CLIPS, EYES} = await import("../src/figure/figure.js");
const {FACES} = await import("../src/domain/faces.js");

test("a test run that passed turns the figure to its card and celebrates, a jump for joy, a confetti cannon or a party horn, and one that failed gives it a startled hop", () => {
    const passed = REACTIONS.find((each) => each.moment === "tests_passed");
    expect(passed.toward).toBe("card");
    expect(passed.among.map((each) => each.clip)).toEqual(["joy", "confetti_cannon", "party_horn"]);
    expect(REACTIONS.find((each) => each.moment === "tests_failed")).toMatchObject({clip: "startled", toward: "card"});
});

test("a reaction fires only when its roll wins, and not again before its cooldown is over", () => {
    const memory = new Map();
    expect(reactionTo("tests_passed", memory, 100, () => 0.99)).toBe(null);
    expect(reactionTo("tests_passed", memory, 100, () => 0).clip).toBe("joy");
    expect(reactionTo("tests_passed", memory, 105, () => 0)).toBe(null);
    expect(reactionTo("tests_passed", memory, 125, () => 0).clip).toBe("joy");
    expect(reactionTo("a moment nobody reacts to", memory, 200, () => 0)).toBe(null);
});

test("typing and reactions change the eyes; messages and work can move the body", () => {
    const user = ["answered", "typing", ...FACES.map((face) => `reacted:${face}`)];
    for (const moment of user) {
        const reactions = REACTIONS.filter((each) => each.moment === moment);
        expect(reactions.length, moment).toBeGreaterThan(0);
        for (const each of reactions) expect([each.look, each.clip], moment).toEqual([expect.any(String), undefined]);
    }
    expect(reactionTo("reacted:\u2764\ufe0f", new Map(), 0, () => 0.99).look).toBe("hearts");
    for (const each of REACTIONS.filter((reaction) => !user.includes(reaction.moment)))
        expect(each.clip ?? each.among.map((one) => one.clip).join(), each.moment).toEqual(expect.any(String));
});

test("every clip and look the figure is ever asked for exists, so no reaction, egg, held state or pastime is dead on arrival", () => {
    const named = new Set(CLIPS.map((clip) => clip.name));
    const asked = [
        ...REACTIONS.flatMap((each) => [each.clip, ...(each.among ?? []).map((one) => one.clip)]).filter(Boolean),
        ...Object.values(VARIANTS).flatMap((among) => among.map((one) => one.clip)),
        ...EGGS.map((egg) => egg.clip),
        ...AMBIENT.map((each) => each.clip),
        ...Object.values(HELD),
        "walk",
        "jump",
        "fall",
        "backflip",
        "land",
        "enter",
        "exit",
        "point",
        "hang_l",
        "hang_r",
    ];
    for (const clip of asked) expect(named.has(clip), clip).toBe(true);
    for (const each of REACTIONS.filter((reaction) => reaction.look)) expect(EYES[each.look], each.look).toBeDefined();
    for (const clip of CLIPS) expect(clip.postures.length, clip.name).toBeGreaterThan(0);
});

test("a figure at rest looks about and stretches only after the state has lasted, and then not on every occasion", () => {
    const next = new Map();
    const [look] = AMBIENT;
    expect(ambientFor("idle", look.after - 1, next, 0, () => 0)).toBe("");
    expect(ambientFor("idle", look.after, next, 0, () => 0)).toBe("look_around");
    expect(ambientFor("idle", look.after, next, 1, () => 0)).toBe("");
    expect(ambientFor("working", 999, next, 1000, () => 0)).toBe("");
    const rolled = new Map();
    expect(ambientFor("idle", look.after, rolled, 0, () => 0.99)).toBe("");
});

test("only a jump of more than the figure's own height sometimes turns over", () => {
    expect(flips(112 * FLIP_OVER, 112, () => 0)).toBe(false);
    expect(flips(112 * FLIP_OVER + 1, 112, () => FLIP_ODDS - 0.01)).toBe(true);
    expect(flips(112 * FLIP_OVER + 1, 112, () => FLIP_ODDS)).toBe(false);
});

test("a watched test run that ends is seen once, as a pass or a failure, and a run already known is not seen again", () => {
    const card = (key, ending) => ({key, time: 9, watch: {figure: "Tests 100%", ending}});
    const known = new Map();
    const agent = (...cards) => ({data: {cards}});
    expect(testResultsAfter(agent(card("messages:1", "")), known)).toEqual([]);
    expect(testResultsAfter(agent(card("messages:1", "finished")), known)).toEqual([{beat: "tests_passed", time: 9, card: "messages:1"}]);
    expect(testResultsAfter(agent(card("messages:1", "finished")), known)).toEqual([]);
    expect(testResultsAfter(agent(card("messages:2", "failed with code 1")), known)).toEqual([
        {beat: "tests_failed", time: 9, card: "messages:2"},
    ]);
    expect(testResultsAfter(agent({key: "messages:3", time: 9, watch: {figure: "", ending: "finished"}}), known)).toEqual([]);
});

test("the user typing now and then makes its eyes read, and finishing a long stretch of work now and then makes it stretch", () => {
    const memory = new Map();
    expect(reactionTo("typing", memory, 0, () => 0).look).toBe("reading");
    expect(reactionTo("typing", memory, 10, () => 0)).toBe(null);
    expect(reactionTo("typing", memory, 100, () => 0.99)).toBe(null);
    expect(reactionTo("work_done", memory, 0, () => 0).clip).toBe("stretch");
});

test("every moment a reaction waits for is one the journal makes, from cards shaped as the server writes them", () => {
    // features/git_actions, features/checks (a failing check), a watched test run, features/journal_laws, features/ask_questions,
    // and the person_at runner/hook_report stamps when the user writes
    const cards = [
        {time: 2, tone: "commit", icon: "branch"},
        {time: 2, icon: "check", tone: "danger"},
        {time: 2, icon: "terminal", tone: "danger"},
        {time: 2, icon: "question"},
        // features/tasks, features/inbox, features/questions, features/workers, features/facts and features/checks, as their cards read
        {time: 2, icon: "todos", tone: "good", label: "Finished task 12: the stamp"},
        {time: 2, icon: "inbox", label: "Filed task 13 from your message"},
        {time: 2, kind: "question", label: "Which one?"},
        {time: 2, icon: "agents", label: "Worker 57, Mr. Muybridge, motion photographer: dispatched on claude opus"},
        {time: 2, icon: "check", tone: "good", label: "Fact 15 recorded"},
        {time: 2, icon: "check", tone: "good", label: "Check Check for sins passed"},
        {time: 2, key: "messages:1", icon: "terminal", watch: {figure: "Tests 100%", ending: "finished"}},
        {time: 2, key: "messages:2", icon: "terminal", watch: {figure: "Tests 90%", ending: "failed with code 1"}},
    ];
    const agent = {data: {cards, person_at: 2}};
    const said = (kind) => ({table: "messages", id: kind.length + 1, author: "agent", session: "s", created_at: new Date(2000).toISOString(), data: {kind}});
    // the user's faces, and the agent's own in every voice's set and those of every voice
    const own = [...Object.values(VOICE_FACES).flatMap((faces) => Object.keys(faces)), ...Object.keys(EVERY_VOICE_FACES)];
    const put = [...FACES.map((face) => ["user", face]), ...own.map((face) => ["agent", face])];
    const faces = put.map(([author, face], n) => ({
        table: "reactions",
        id: n + 1,
        author,
        created_at: new Date(2000).toISOString(),
        emoji: face,
        message_id: n,
    }));
    const made = new Set(
        [
            ...beatsAfter(agent, 1),
            ...cardsAfter(agent, new Set()),
            ...testResultsAfter(agent, new Map()),
            ...facesAfter(faces, 1),
            ...sayingsAfter({session: "s"}, [said(""), said("report")], 1),
            // the figure's own page sees these two: a key pressed in the compose box, and the agent settling after WORKED_SECONDS of work
            {beat: "typing"},
            {beat: "work_done"},
            {beat: "long_walk"},
            {beat: "building"},
        ].map((fire) => fire.beat)
    );
    for (const each of REACTIONS) expect(made.has(each.moment), each.moment).toBe(true);
});

test("a look shows only while the figure faces no further than sideways, so one that comes while it hangs with its back turned waits", () => {
    for (const facing of [0, 60, 90, 270, 300, -90, 450]) expect(eyesShown(facing), facing).toBe(true);
    for (const facing of [180, 150, 210, -180, 540]) expect(eyesShown(facing), facing).toBe(false);
});

test("a look's clock runs only while its eyes are shown: it waits while the figure faces away, plays out its time, and then ends", () => {
    let looking = lookOf("hearts", 100);
    let drawn = eyesAt(looking, 180, 101);
    expect(drawn.eyes).toBe(null);
    looking = drawn.looking;
    drawn = eyesAt(looking, 0, 101.5);
    expect(drawn.eyes).toMatchObject({mood: "hearts", seconds: 0.5, lasts: LOOK_SECONDS});
    expect(eyesAt(drawn.looking, 0, 101 + LOOK_SECONDS)).toEqual({looking: null, eyes: null});
    // only a figure hanging with its back to the viewer lets go of where it is for a look
    expect(letsGoFor({posture: "hang", face: 180})).toBe(true);
    expect([letsGoFor({posture: "hang", face: 0}), letsGoFor({posture: "sit", face: 300})]).toEqual([false, false]);
});

test("typing is a moment, and so is the end of a stretch of work long enough, timed from when the work began", () => {
    expect(workMoments("idle", true, 0, 50)).toEqual({moments: [{beat: "typing", time: 50}], began: 0});
    expect(workMoments("running", false, 0, 50)).toEqual({moments: [], began: 50});
    expect(workMoments("thinking", false, 50, 60).began).toBe(50);
    expect(workMoments("reading", false, 10, 20)).toEqual({moments: [], began: 10});
    expect(workMoments("idle", false, 50, 50 + WORKED_SECONDS)).toEqual({
        moments: [{beat: "work_done", time: 50 + WORKED_SECONDS}],
        began: 0,
    });
    expect(workMoments("idle", false, 50, 51).moments).toEqual([]);
});

test("a moment is answered by its egg first, else by its reaction, a beat for the body or a look for the eyes, and a missing clip by nothing", () => {
    const memory = () => ({reacted: new Map(), played: []});
    const has = () => true;
    expect(answerTo({beat: "failed", time: 1}, "squire", memory(), 0, () => 0, has)).toEqual({beat: {clip: "squire_chase", card: ""}});
    expect(answerTo({beat: "reacted:\u2764\ufe0f", time: 1}, "butler", memory(), 0, () => 0, has)).toEqual({look: "hearts"});
    expect(answerTo({beat: "tests_passed", time: 1, card: "tests:1"}, "butler", memory(), 0, () => 0, has)).toEqual({
        beat: {clip: "joy", card: "tests:1"},
    });
    expect(
        answerTo(
            {beat: "tests_passed", time: 1},
            "butler",
            memory(),
            0,
            () => 0,
            () => false
        )
    ).toBe(null);
});

test("the figure does something by itself only while it is calm: idle, not hanging, with nothing to play and neither coming nor going", () => {
    const calm = {place: {posture: "sit"}, beats: 0, arriving: false, leaving: false};
    const waited = {state: "idle", lasted: 1000};
    const has = () => true;
    expect(pastimeFor(calm, waited, new Map(), 0, () => 0, has)).toEqual({clip: AMBIENT[0].clip, card: "", flies: false});
    expect(pastimeFor({...calm, beats: 1}, waited, new Map(), 0, () => 0, has)).toBe(null);
    expect(pastimeFor({...calm, place: {posture: "hang"}}, waited, new Map(), 0, () => 0, has)).toBe(null);
    expect(pastimeFor(calm, {...waited, state: "running"}, new Map(), 0, () => 0, has)).toBe(null);
});

