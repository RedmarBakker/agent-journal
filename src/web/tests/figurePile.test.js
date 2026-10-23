// @vitest-environment node
import {expect, test} from "vitest";
import {CUT, PILE, SHENANIGAN, SHOWPIECES, UNIT, choicesFor, cutsAfter, draw, lineOf} from "../src/figure/pile.js";
import {CLIPS} from "../src/figure/figure.js";
import {ACTS} from "../src/figure/acts.js";
import {unitGranted} from "../src/figure/parcels.js";
import {carrierOf, flips} from "../src/figure/reactions.js";

const names = (entries) => entries.map((entry) => entry.name);
// a roll that lands at `share` of the way through the tickets
const rolls = (...shares) => () => shares.shift();

test("the pile is filtered to what may play where things stand: the moment, the voice, how long the state has lasted, a free hand", () => {
    expect(names(choicesFor({moment: "tests_failed"}))).toEqual(["startled", "dismay", "nothing"]);
    expect(names(choicesFor({moment: "heard", voice: "butler"}))).toEqual(["bow", "nothing"]);
    expect(names(choicesFor({moment: "heard", voice: "homie"}))).toEqual(["nod", "nothing"]);
    // an idle act once the state has lasted long enough, and only while the figure has nothing to do; a shenanigan in any state
    const idle = names(choicesFor({moment: "pastime", free: true, lasted: 20, voice: "coach"}));
    expect(idle).toEqual(["hop_up", "nothing"]);
    expect(names(choicesFor({moment: "pastime", free: true, lasted: 1000, voice: "coach"}))).toContain("whistle");
    expect(names(choicesFor({moment: "pastime", free: false, lasted: 1000, voice: "coach"}))).toEqual(["hop_up", "nothing"]);
    // a hang only with a free hand, a backflip only on a high jump, the work's acts only while that work goes on
    expect(names(choicesFor({moment: "perch", hands: false}))).toEqual(["stand"]);
    expect(names(choicesFor({moment: "perch", hands: true}))).toEqual(["hang", "stand"]);
    expect(names(choicesFor({moment: "jump", high: false}))).toEqual(["jump"]);
    expect(names(choicesFor({moment: "spell", state: "reading"}))).toEqual(["reading", "nothing"]);
    // what the figure cannot draw where it is, it never draws
    expect(names(choicesFor({moment: "tests_failed", has: (name) => name !== "dismay"}))).toEqual(["startled", "nothing"]);
});

test("one is drawn by weight, a weight of 3 counting as three tickets, and a moment cools down once it has played", () => {
    // ufo 3, crane 1: the first three tickets of four are the UFO's
    for (const [share, name] of [[0, "ufo"], [0.74, "ufo"], [0.75, "crane"], [0.99, "crane"]]) expect(draw({moment: "carrier"}, rolls(share)).name).toBe(name);
    // a moment's nothing is a draw that plays nothing
    expect(draw({moment: "tests_failed"}, rolls(0.99))).toBe(null);
    const memory = new Map();
    expect(draw({moment: "tests_failed", memory, now: 100}, rolls(0)).name).toBe("startled");
    expect(draw({moment: "tests_failed", memory, now: 110}, rolls(0))).toBe(null);
    expect(draw({moment: "tests_failed", memory, now: 120}, rolls(0)).name).toBe("startled");
});

test("after three acts in a row with no shenanigan among them, the next draw that may be one is one; an act just played is not drawn again at once", () => {
    const tally = {plain: 0, last: ""};
    const free = {moment: "pastime", free: true, lasted: 1000, voice: "butler", tally};
    // three plain acts, and the next draw, at a roll that would play nothing, is a shenanigan all the same
    for (let act = 0; act < SHENANIGAN.after; act++) draw({moment: "reported", tally}, rolls(0));
    expect(tally.plain).toBe(SHENANIGAN.after);
    const forced = draw(free, rolls(0.99));
    expect(forced.shenanigan).toBe(true);
    expect(tally.plain).toBe(0);
    // a moment with no shenanigan in it draws as ever
    for (let act = 0; act < SHENANIGAN.after; act++) draw({moment: "reported", tally: {plain: 0, last: ""}}, rolls(0));
    expect(draw({moment: "carrier", tally: {plain: 5, last: ""}}, rolls(0)).name).toBe("ufo");
    // the act just played is passed over while another may play
    expect(draw({moment: "reported", tally: {plain: 0, last: "scroll"}}, rolls(0)).name).toBe("nod");
    expect(draw({moment: "bar_failed", tally: {plain: 0, last: "fume"}}, rolls(0)).name).toBe("fume");
});

test("an act may be cut off by the next moment only as the pile says and once it has played its least, a second or three for the longer acts", () => {
    expect(cutsAfter("look_left", 0.5)).toBe(false);
    expect(cutsAfter("look_left", 1)).toBe(true);
    expect(cutsAfter("rest", 2)).toBe(false);
    expect(cutsAfter("rest", 3)).toBe(true);
    // a fall, a backflip, a crane's grab, a celebration play out
    for (const name of ["fall", "backflip", "tumble", "joy", "party_horn", "phone_call"]) expect(cutsAfter(name, 60), name).toBe(false);
    // the longer acts that may be cut, longer than three seconds, must have played three first
    const seconds = (name) => {
        const clip = CLIPS.find((each) => each.name === name);
        return clip.frames / clip.fps;
    };
    for (const [name, least] of Object.entries(CUT)) expect([name, least], name).toEqual([name, seconds(name) > 3 ? 3 : 1]);
});

test("every animation in the pile, with its weight and the condition it plays under, and whether it may be cut or plays out", () => {
    expect(PILE.map(lineOf)).toEqual([
        "clip joy ×2 when moment=tests_passed, plays out",
        "clip party_horn ×1 when moment=tests_passed, plays out",
        "nothing nothing ×1 when moment=tests_passed",
        "shenanigan clip bug_shot ×3 when moment=tests_fixed, plays out",
        "clip joy ×2 when moment=tests_fixed, plays out",
        "clip party_horn ×1 when moment=tests_fixed, plays out",
        "clip startled ×2 when moment=tests_failed, plays out",
        "clip dismay ×1 when moment=tests_failed, plays out",
        "nothing nothing ×1 when moment=tests_failed",
        "clip joy ×2 when moment=committed, plays out",
        "clip party_horn ×1 when moment=committed, plays out",
        "nothing nothing ×2 when moment=committed",
        "clip phone_call ×1 when moment=messaged, plays out",
        "clip nod ×4 when moment=task_finished, cut after 1s",
        "clip joy ×2 when moment=task_finished, plays out",
        "clip party_horn ×1 when moment=task_finished, plays out",
        "nothing nothing ×7 when moment=task_finished",
        "clip ask_sign ×9 when moment=question_asked, plays out",
        "clip think ×3 when moment=question_asked, cut after 1s",
        "nothing nothing ×8 when moment=question_asked",
        "clip scroll ×3 when moment=reported, plays out",
        "clip nod ×1 when moment=reported, cut after 1s",
        "nothing nothing ×4 when moment=reported",
        "clip file_card ×3 when moment=fact_filed, plays out",
        "clip nod ×1 when moment=fact_filed, cut after 1s",
        "nothing nothing ×6 when moment=fact_filed",
        "clip joy ×2 when moment=check_passed, plays out",
        "clip party_horn ×1 when moment=check_passed, plays out",
        "nothing nothing ×9 when moment=check_passed",
        "clip joy ×2 when moment=bar_done, plays out",
        "clip party_horn ×1 when moment=bar_done, plays out",
        "clip fume ×1 when moment=bar_failed, plays out",
        "clip look_left ×2 when moment=standing, cut after 1s",
        "clip look_right ×2 when moment=standing, cut after 1s",
        "clip look_up ×1 when moment=standing, cut after 1s",
        "nothing nothing ×40 when moment=standing",
        "clip tumble ×3 when moment=launched, plays out",
        "nothing nothing ×47 when moment=launched",
        "clip wipe_brow ×4 when moment=building, cut after 1s",
        "clip look_left ×1 when moment=building, cut after 1s",
        "clip look_right ×1 when moment=building, cut after 1s",
        "nothing nothing ×69 when moment=building",
        "clip shake ×3 when moment=failed, cut after 1s",
        "nothing nothing ×2 when moment=failed",
        "clip shake ×1 when moment=refused, cut after 1s",
        "nothing nothing ×1 when moment=refused",
        "clip stretch ×2 when moment=work_done, cut after 1s",
        "nothing nothing ×3 when moment=work_done",
        "look amused ×3 when moment=answered",
        "nothing nothing ×2 when moment=answered",
        "clip bow ×1 when moment=heard voices=butler, cut after 1s",
        "clip salute ×1 when moment=heard voices=squire, cut after 1s",
        "clip nod ×1 when moment=heard voices=coach,colleague,homie, cut after 1s",
        "nothing nothing ×1 when moment=heard",
        "clip stumble ×3 when moment=long_walk, plays out",
        "nothing nothing ×22 when moment=long_walk",
        "clip glance ×7 when moment=card_arrived, cut after 1s",
        "nothing nothing ×13 when moment=card_arrived",
        "look reading ×1 when moment=typing",
        "nothing nothing ×4 when moment=typing",
        "look hearts ×1 when moment=reacted:❤️",
        "look amused ×1 when moment=reacted:👍",
        "look startled ×1 when moment=reacted:🎉",
        "look amused ×1 when moment=reacted:😄",
        "look reading ×1 when moment=reacted:👀",
        "look hearts ×1 when moment=reacted:🙏",
        "look worried ×1 when moment=reacted:👎",
        "look worried ×1 when moment=reacted:💔",
        "look angry ×1 when moment=reacted:😠",
        "look amused ×1 when moment=reacted:🎩",
        "look reading ×1 when moment=reacted:🧐",
        "look amused ×1 when moment=reacted:🥂",
        "look amused ×1 when moment=reacted:🤙",
        "look amused ×1 when moment=reacted:😎",
        "look startled ×1 when moment=reacted:🔥",
        "look amused ×1 when moment=reacted:💪",
        "look hearts ×1 when moment=reacted:🏆",
        "look angry ×1 when moment=reacted:⚔️",
        "look worried ×1 when moment=reacted:🛡️",
        "look amused ×1 when moment=reacted:🏰",
        "clip hat_tip ×1 when moment=agent_reacted:🎩 voices=butler, plays out",
        "clip monocle ×1 when moment=agent_reacted:🧐 voices=butler, plays out",
        "clip toast ×1 when moment=agent_reacted:🥂 voices=butler, plays out",
        "clip shaka ×1 when moment=agent_reacted:🤙 voices=homie, plays out",
        "clip shades ×1 when moment=agent_reacted:😎 voices=homie, plays out",
        "clip fire ×1 when moment=agent_reacted:🔥 voices=homie, plays out",
        "clip thumbs_up ×1 when moment=agent_reacted:👍 voices=colleague, plays out",
        "clip peer ×1 when moment=agent_reacted:👀 voices=colleague, plays out",
        "clip party_popper ×1 when moment=agent_reacted:🎉 voices=coach, plays out",
        "clip flex ×1 when moment=agent_reacted:💪 voices=coach, plays out",
        "clip trophy ×1 when moment=agent_reacted:🏆 voices=coach, plays out",
        "clip sword ×1 when moment=agent_reacted:⚔️ voices=squire, plays out",
        "clip shield_up ×1 when moment=agent_reacted:🛡️ voices=squire, plays out",
        "clip castle ×1 when moment=agent_reacted:🏰 voices=squire, plays out",
        "clip thanks ×1 when moment=agent_reacted:🙏, plays out",
        "clip stretch ×3 when moment=pastime free=true lasted=90, cut after 1s",
        "clip rest ×3 when moment=pastime free=true lasted=180, cut after 3s",
        "clip yawn ×2 when moment=pastime free=true lasted=60, cut after 1s",
        "clip polish ×4 when moment=pastime free=true lasted=45 voices=butler, cut after 3s",
        "clip whistle ×4 when moment=pastime free=true lasted=45 voices=coach, cut after 3s",
        "clip sip ×4 when moment=pastime free=true lasted=45 voices=colleague, cut after 3s",
        "clip headphones ×4 when moment=pastime free=true lasted=45 voices=homie, cut after 3s",
        "clip shield_polish ×4 when moment=pastime free=true lasted=45 voices=squire, cut after 3s",
        "shenanigan clip hop_up ×2 when moment=pastime, plays out",
        "shenanigan clip disco ×8 when moment=pastime ball=bubble, plays out",
        "nothing nothing ×560 when moment=pastime",
        "clip search ×3 when moment=held:search, plays out",
        "clip binoculars ×2 when moment=held:search, plays out",
        "clip flashlight ×2 when moment=held:search, plays out",
        "clip peek_under ×1 when moment=held:search, plays out",
        "clip type ×3 when moment=held:type, plays out",
        "clip type_ponder ×1 when moment=held:type, plays out",
        "clip watch ×2 when moment=held:watch, plays out",
        "clip wave_up ×1 when moment=held:watch, plays out",
        "clip pack_box ×3 when moment=held:compacting, plays out",
        "clip press ×2 when moment=held:compacting, plays out",
        "clip vacuum ×2 when moment=held:compacting, plays out",
        "clip compacting ×1 when moment=held:compacting, plays out",
        "pick writing ×12 when moment=spell state=writing",
        "pick reading ×12 when moment=spell state=reading",
        "pick searching ×12 when moment=spell state=searching",
        "nothing nothing ×4 when moment=spell",
        "shenanigan clip tickle_swat ×1 when moment=tickled, plays out",
        "clip eager ×2 when moment=eager slow=true, plays out",
        "nothing nothing ×3 when moment=eager",
        "shenanigan clip backflip ×7 when moment=jump high=true, plays out",
        "clip jump ×13 when moment=jump, plays out",
        "shenanigan pick pogo ×2 when moment=climb",
        "pick hops ×3 when moment=climb footholds=true",
        "pick unit ×19 when moment=unit",
        "nothing nothing ×1 when moment=unit",
        "pick ufo ×3 when moment=carrier",
        "pick crane ×1 when moment=carrier",
        "pick left ×1 when moment=crane_from",
        "pick right ×1 when moment=crane_from",
        "pick hang ×1 when moment=perch hands=true",
        "pick stand ×5 when moment=perch",
        "pick caught ×1 when moment=fall settled=true",
        "pick home ×1 when moment=fall",
        "pick 0 ×1 when moment=digit",
        "pick 1 ×1 when moment=digit",
        "pick rest ×35 when moment=roam",
        "pick seat ×15 when moment=roam",
        "pick edge ×25 when moment=roam",
        "shenanigan pick bubble ×15 when moment=roam",
        "pick tab ×10 when moment=roam",
        "pick ledge ×9 when moment=roam free=true",
        "pick composed ×8 when moment=roam free=true",
        "shenanigan pick rope_swing ×8 when moment=roam free=true swings=true",
        "pick middle ×2 when moment=ledge_at",
        "pick third ×1 when moment=ledge_at",
        "pick two_thirds ×1 when moment=ledge_at",
    ]);
    // every clip of the pile is one the figure has
    const clips = new Set(CLIPS.map((clip) => clip.name));
    for (const entry of PILE.filter((each) => each.kind === "clip")) expect(clips.has(entry.name), entry.name).toBe(true);
});

test("each showpiece waits its own cooldown, listed in one place: the parachute 20 minutes, the disco and the rope swing 15, the salto, the pogo stick and the bug shot 5 to 8, the tickle swats none", () => {
    expect(SHOWPIECES.hop_up).toBe(20 * 60);
    expect([SHOWPIECES.disco, SHOWPIECES.rope_swing]).toEqual([15 * 60, 15 * 60]);
    for (const name of ["backflip", "pogo", "bug_shot"]) expect(SHOWPIECES[name] >= 5 * 60 && SHOWPIECES[name] <= 8 * 60, name).toBe(true);
    expect(SHOWPIECES.tickle_swat).toBe(0);
    // every showpiece in the pile takes its cooldown from the list, kept apart from the other acts of its moment
    const showpieces = PILE.filter((entry) => entry.name in SHOWPIECES);
    expect(showpieces.length).toBeGreaterThan(0);
    for (const entry of showpieces) expect([entry.name, entry.cooldown, entry.apart]).toEqual([entry.name, SHOWPIECES[entry.name], true]);
});

test("a showpiece is out of the draw while its cooldown lasts and back in at its own weight once it is over", () => {
    const memory = new Map();
    const idle = (now) => ({moment: "pastime", free: true, lasted: 1000, voice: "butler", memory, now});
    const hopUp = (now) => choicesFor(idle(now)).find((entry) => entry.name === "hop_up");
    const weight = hopUp(0).weight;
    // the run to the parachute drawn, it is not drawn again for twenty minutes, whatever the roll
    const tickets = choicesFor(idle(0));
    const at = tickets.slice(0, tickets.findIndex((entry) => entry.name === "hop_up")).reduce((sum, entry) => sum + entry.weight, 0);
    expect(draw(idle(0), () => (at + 0.5) / tickets.reduce((sum, entry) => sum + entry.weight, 0)).name).toBe("hop_up");
    for (const now of [1, 60, 600, SHOWPIECES.hop_up - 1]) expect(hopUp(now), String(now)).toBeUndefined();
    expect(hopUp(SHOWPIECES.hop_up).weight).toBe(weight);
    // the salto on a jump up turns now and then, then waits its cooldown before it turns again
    const jumps = new Map();
    expect(flips(400, 112, () => 0, jumps, 0)).toBe(true);
    expect(flips(400, 112, () => 0, jumps, SHOWPIECES.backflip - 1)).toBe(false);
    expect(flips(400, 112, () => 0, jumps, SHOWPIECES.backflip)).toBe(true);
});

test("a running test run builds a server unit nearly every time it may, but never two within three minutes", () => {
    const memory = new Map();
    let seed = 7;
    const random = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
    // a look every second for an hour, each unit built and piled in the next half minute
    const granted = [];
    for (let now = 0; now < 3600; now++) if (!granted.length || now - granted.at(-1) >= 30) unitGranted(memory, now, random) && granted.push(now);
    const gaps = granted.slice(1).map((at, index) => at - granted[index]);
    expect(Math.min(...gaps)).toBeGreaterThanOrEqual(UNIT.every);
    // once it may, it builds one at once most of the time
    expect(gaps.filter((gap) => gap === UNIT.every).length / gaps.length).toBeGreaterThan(0.8);
    expect(granted.length).toBeGreaterThanOrEqual(Math.floor(3600 / UNIT.every) - 2);
});

test("a commit with units always brings the UFO or the crane to take them, with no cooldown between", () => {
    expect(PILE.filter((entry) => entry.when.moment === "carrier").every((entry) => !entry.cooldown && entry.kind === "pick")).toBe(true);
    for (let share = 0; share < 1; share += 0.01) expect(["ufo", "crane"]).toContain(carrierOf(() => share));
});

test("a pass that fixed a failed test run, and only that, may bring a bug the figure shoots, in place of the visor's glow, waiting its own cooldown and the moment's", () => {
    const bugShot = (moment, scene = {}) => choicesFor({moment, ...scene}).some((entry) => entry.name === "bug_shot");
    expect(bugShot("tests_fixed")).toBe(true);
    for (const moment of ["tests_passed", "tests_failed", "committed", "check_passed", "bar_done", "pastime", "building"]) expect(bugShot(moment, {free: true, lasted: 1000}), moment).toBe(false);
    const entry = PILE.find((each) => each.name === "bug_shot");
    expect(entry).toMatchObject({when: {moment: "tests_fixed"}, cooldown: SHOWPIECES.bug_shot, toward: "", onto: false});
    // drawn, it is not drawn again for its cooldown, and nothing else of a fixed run plays inside the run's own
    const memory = new Map();
    expect(draw({moment: "tests_fixed", memory, now: 0}, () => 0).name).toBe("bug_shot");
    expect(choicesFor({moment: "tests_fixed", memory, now: 10}).filter((each) => each.kind !== "nothing")).toEqual([]);
    expect(bugShot("tests_fixed", {memory, now: 30})).toBe(false);
    expect(bugShot("tests_fixed", {memory, now: SHOWPIECES.bug_shot})).toBe(true);
});

test("a finished task never brings the stamp: no stamp in the pile or among the clips, and its moment draws a nod, a celebration or nothing", () => {
    expect(PILE.some((entry) => entry.name === "stamp")).toBe(false);
    expect(CLIPS.some((clip) => clip.name === "stamp")).toBe(false);
    expect(Object.keys(ACTS)).not.toContain("stamp");
    const drawn = new Set();
    for (let share = 0; share < 1; share += 0.01) drawn.add(draw({moment: "task_finished"}, () => share)?.name ?? "nothing");
    expect([...drawn].sort()).toEqual(["joy", "nod", "nothing", "party_horn"]);
});
