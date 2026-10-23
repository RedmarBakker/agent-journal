// @vitest-environment node
import {expect, test} from "vitest";
import {CUT, PILE, SHENANIGAN, choicesFor, cutsAfter, draw, lineOf} from "../src/figure/pile.js";
import {CLIPS} from "../src/figure/figure.js";

const names = (entries) => entries.map((entry) => entry.name);
// a roll that lands at `share` of the way through the tickets
const rolls = (...shares) => () => shares.shift();

test("the pile is filtered to what may play where things stand: the moment, the voice, how long the state has lasted, a free hand", () => {
    expect(names(choicesFor({moment: "tests_failed"}))).toEqual(["startled", "dismay", "nothing"]);
    expect(names(choicesFor({moment: "heard", voice: "butler"}))).toEqual(["bow", "nothing"]);
    expect(names(choicesFor({moment: "heard", voice: "homie"}))).toEqual(["nod", "nothing"]);
    // an idle act once the state has lasted long enough, and only while the figure has nothing to do; a shenanigan in any state
    const idle = names(choicesFor({moment: "pastime", free: true, lasted: 20, voice: "coach"}));
    expect(idle).toEqual(["look_around", "hop_up", "salto", "nothing"]);
    expect(names(choicesFor({moment: "pastime", free: true, lasted: 1000, voice: "coach"}))).toContain("whistle");
    expect(names(choicesFor({moment: "pastime", free: false, lasted: 1000, voice: "coach"}))).toEqual(["hop_up", "salto", "nothing"]);
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
    // a fall, a salto, a crane's grab, a celebration play out
    for (const name of ["fall", "salto", "tumble", "joy", "party_horn", "stamp", "post_dove"]) expect(cutsAfter(name, 60), name).toBe(false);
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
        "clip startled ×2 when moment=tests_failed, plays out",
        "clip dismay ×1 when moment=tests_failed, plays out",
        "nothing nothing ×1 when moment=tests_failed",
        "clip joy ×2 when moment=committed, plays out",
        "clip party_horn ×1 when moment=committed, plays out",
        "nothing nothing ×2 when moment=committed",
        "clip post_dove ×7 when moment=messaged, plays out",
        "nothing nothing ×13 when moment=messaged",
        "clip stamp ×4 when moment=task_finished, plays out",
        "clip joy ×2 when moment=task_finished, plays out",
        "clip party_horn ×1 when moment=task_finished, plays out",
        "nothing nothing ×7 when moment=task_finished",
        "clip ask_sign ×9 when moment=question_asked, plays out",
        "clip think ×3 when moment=question_asked, cut after 1s",
        "nothing nothing ×8 when moment=question_asked",
        "clip whistle_runner ×3 when moment=worker_sent, plays out",
        "clip wave ×1 when moment=worker_sent, cut after 1s",
        "nothing nothing ×4 when moment=worker_sent",
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
        "nothing nothing ×28 when moment=standing",
        "clip tumble ×3 when moment=launched, plays out",
        "nothing nothing ×47 when moment=launched",
        "clip wipe_brow ×4 when moment=building, cut after 1s",
        "clip look_around ×2 when moment=building, cut after 1s",
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
        "clip look_around ×6 when moment=pastime free=true lasted=20, cut after 1s",
        "clip stretch ×3 when moment=pastime free=true lasted=90, cut after 1s",
        "clip rest ×3 when moment=pastime free=true lasted=180, cut after 3s",
        "clip yawn ×2 when moment=pastime free=true lasted=60, cut after 1s",
        "clip polish ×4 when moment=pastime free=true lasted=45 voices=butler, cut after 3s",
        "clip whistle ×4 when moment=pastime free=true lasted=45 voices=coach, cut after 3s",
        "clip sip ×4 when moment=pastime free=true lasted=45 voices=colleague, cut after 3s",
        "clip headphones ×4 when moment=pastime free=true lasted=45 voices=homie, cut after 3s",
        "clip shield_polish ×4 when moment=pastime free=true lasted=45 voices=squire, cut after 3s",
        "shenanigan clip hop_up ×2 when moment=pastime, plays out",
        "shenanigan clip salto ×2 when moment=pastime, plays out",
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
        "clip eager ×2 when moment=eager slow=true, plays out",
        "nothing nothing ×3 when moment=eager",
        "shenanigan clip backflip ×7 when moment=jump high=true, plays out",
        "clip jump ×13 when moment=jump, plays out",
        "pick ufo ×3 when moment=carrier",
        "pick crane ×1 when moment=carrier",
        "pick left ×1 when moment=crane_from",
        "pick right ×1 when moment=crane_from",
        "pick hang ×2 when moment=perch hands=true",
        "pick stand ×3 when moment=perch",
        "pick caught ×1 when moment=fall settled=true",
        "pick home ×1 when moment=fall",
        "pick 0 ×1 when moment=digit",
        "pick 1 ×1 when moment=digit",
        "pick rest ×35 when moment=roam",
        "pick seat ×15 when moment=roam",
        "pick edge ×25 when moment=roam",
        "shenanigan pick bubble ×15 when moment=roam",
        "pick tab ×10 when moment=roam",
    ]);
    // every clip of the pile is one the figure has
    const clips = new Set(CLIPS.map((clip) => clip.name));
    for (const entry of PILE.filter((each) => each.kind === "clip")) expect(clips.has(entry.name), entry.name).toBe(true);
});
