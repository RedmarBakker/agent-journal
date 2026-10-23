// The figure's animations, one pile. Every entry is something the figure may do, with its weight, a weight of 3 counting as three tickets,
// and `when`, the condition it may play under: the moment it belongs to, and anything else it needs, as a voice, a stretch of time the
// state has lasted, a free hand. At each choice the pile is filtered to the entries whose condition holds, that the figure can draw and
// that are not cooling down, and one is drawn by weight (draw). A `nothing` entry is the chance that the moment passes with nothing played.
// A new animation is added to the pile, never put in another's place.
//
// An entry is a clip the body plays, a look the eyes take on, or a pick, a choice of something that is not a clip: the carrier that takes
// the work away, a perch's kind, a digit, a place to go, a spell the figure keeps up. Its `cooldown` is the seconds before its moment may
// play again once it has, kept under the moment, or under the entry itself when it stands `apart`. A reaction may turn `toward` its card
// or go `onto` it, playing there.
//
// The playful acts are `shenanigan`s: a salto on a jump up, the run up the bubbles off the screen, a jump up onto a bubble or a hang from one. They may
// play in any state, each state weighting its own acts higher, and after SHENANIGAN.after acts in a row with none among them the next
// draw that may be one is one.
export const SHENANIGAN = {after: 3};

// The showpiece acts and how long each waits before it may play again once it has, in seconds, so they stay special: the run up to the
// parachute at most every 20 minutes, the disco dance and the rope swing about every 15, the salto on a jump up, the pogo stick and the bug
// shot about every 6; the tickle swats come as often as the user tickles. A cooldown only takes an act out of the draw while it lasts;
// its weight is its own.
export const SHOWPIECES = {hop_up: 20 * 60, disco: 15 * 60, rope_swing: 15 * 60, backflip: 6 * 60, pogo: 6 * 60, bug_shot: 6 * 60, tickle_swat: 0};

// While a test run, a build or a check runs, building a server unit is drawn far above doing nothing, but one unit at most every `every`
// seconds
export const UNIT = {weight: 19, every: 3 * 60};

// The clip each voice plays when the agent puts one of the voice's own faces on a message, by voice and then by face
export const VOICE_FACES = {
    butler: {"🎩": "hat_tip", "🧐": "monocle", "🥂": "toast"},
    homie: {"🤙": "shaka", "😎": "shades", "🔥": "fire"},
    colleague: {"👍": "thumbs_up", "👀": "peer"},
    coach: {"🎉": "party_popper", "💪": "flex", "🏆": "trophy"},
    squire: {"⚔️": "sword", "🛡️": "shield_up", "🏰": "castle"},
};

// The clip every voice plays when the agent puts one of these faces on a message, beside its own
export const EVERY_VOICE_FACES = {"🙏": "thanks"};

// the look the eyes take on at a face the user puts on a message, which is aimed at the figure, so it always answers
const USER_FACES = {
    "❤️": "hearts", "👍": "amused", "🎉": "startled", "😄": "amused", "👀": "reading",
    "🙏": "hearts", "👎": "worried", "💔": "worried", "😠": "angry", "🎩": "amused",
    "🧐": "reading", "🥂": "amused", "🤙": "amused", "😎": "amused", "🔥": "startled", "💪": "amused", "🏆": "hearts",
    "⚔️": "angry", "🛡️": "worried", "🏰": "amused",
};

// The acts the next moment may cut off, and the seconds each must have played first: a look about, a stretch or a nod may give way after a
// second, the longer idle acts after three; every other act plays out, as a fall, a backflip, a celebration or an act with a prop in hand,
// so the figure never flickers between acts
export const CUT = {
    look_left: 1, look_right: 1, look_up: 1, look_around: 1, glance: 1, wipe_brow: 1, stretch: 1, yawn: 1, nod: 1, shake: 1, bow: 1,
    salute: 1, wave: 1, think: 1, rest: 3, polish: 3, whistle: 3, sip: 3, headphones: 3, shield_polish: 3,
};

const clip = (name, weight, when = {}) => ({name, kind: "clip", weight, when, cut: CUT[name] ?? false});
const look = (name, weight, when = {}) => ({name, kind: "look", weight, when});
const pick = (name, weight, when = {}, more = {}) => ({name, kind: "pick", weight, when, ...more});
const nothing = (weight) => ({name: "nothing", kind: "nothing", weight, when: {}});

// the entries of one moment, each given the moment and whatever the moment says of them all, as its cooldown; one apart from the others
// with a cooldown of its own still waits the moment's, `moment` seconds after any of them played
const at = (moment, shared, entries) => entries.map((entry) => ({...shared, ...entry, when: {moment, ...entry.when}, ...(shared.cooldown && {waits: shared.cooldown})}));

// the ways the figure celebrates: a jump for joy with its hands up, a party horn blown
const celebrations = () => [clip("joy", 2), clip("party_horn", 1)];

// the idle acts, while the figure has nothing to do: each once the state has lasted `lasted` seconds, apart from the others, and so
// weighted against nothing that one is played about every half minute, looked for every second
const pastime = (name, weight, lasted, cooldown, more = {}) => ({...clip(name, weight, {free: true, lasted, ...more.when}), cooldown, apart: true});

// a showpiece among the acts, a shenanigan in any state, apart from the others, waiting its own cooldown (SHOWPIECES)
const showpiece = (entry) => ({...entry, cooldown: SHOWPIECES[entry.name], apart: true, shenanigan: true});

export const PILE = [
    // a test run's end: celebrated on its card, now and then by shooting a bug that crawls into the chat instead of the visor's glow, or a
    // start at a failure
    ...at("tests_passed", {cooldown: 20, toward: "card", onto: true}, [...celebrations(), {...showpiece(clip("bug_shot", 1)), toward: "", onto: false}, nothing(1)]),
    ...at("tests_failed", {cooldown: 20, toward: "card"}, [clip("startled", 2), clip("dismay", 1), nothing(1)]),
    ...at("committed", {cooldown: 30, toward: "card", onto: true}, [...celebrations(), nothing(2)]),
    // what the agent has just done in the journal, acted out now and then, never every time
    ...at("messaged", {cooldown: 120}, [clip("post_dove", 7), nothing(13)]),
    ...at("task_finished", {cooldown: 90, toward: "card", onto: true}, [clip("stamp", 4), ...celebrations(), nothing(7)]),
    ...at("question_asked", {cooldown: 60}, [clip("ask_sign", 9), clip("think", 3), nothing(8)]),
    ...at("worker_sent", {cooldown: 90}, [clip("whistle_runner", 3), clip("wave", 1), nothing(4)]),
    ...at("reported", {cooldown: 90}, [clip("scroll", 3), clip("nod", 1), nothing(4)]),
    ...at("fact_filed", {cooldown: 120}, [clip("file_card", 3), clip("nod", 1), nothing(6)]),
    ...at("check_passed", {cooldown: 120, toward: "card", onto: true}, [...celebrations(), nothing(9)]),
    // a bar the figure was eager for has ended, as its card says: it celebrates, or, the more for having been eager, is crushed and fumes
    ...at("bar_done", {}, celebrations()),
    ...at("bar_failed", {}, [clip("fume", 1)]),
    // standing still or thinking, it looks about now and then, so standing still is never the same loop
    ...at("standing", {cooldown: 7}, [clip("look_left", 2), clip("look_right", 2), clip("look_up", 1), nothing(28)]),
    // landing from a launch it very rarely trips and falls to its knees
    ...at("launched", {cooldown: 300}, [clip("tumble", 3), nothing(47)]),
    // a break from the hammering now and then
    ...at("building", {cooldown: 30}, [clip("wipe_brow", 4), clip("look_around", 2), nothing(69)]),
    ...at("failed", {cooldown: 20, toward: "card"}, [clip("shake", 3), nothing(2)]),
    ...at("refused", {cooldown: 20}, [clip("shake", 1), nothing(1)]),
    ...at("work_done", {cooldown: 120}, [clip("stretch", 2), nothing(3)]),
    ...at("answered", {cooldown: 15}, [look("amused", 3), nothing(2)]),
    ...at("heard", {cooldown: 30}, [
        clip("bow", 1, {voices: ["butler"]}),
        clip("salute", 1, {voices: ["squire"]}),
        clip("nod", 1, {voices: ["coach", "colleague", "homie"]}),
        nothing(1),
    ]),
    ...at("long_walk", {cooldown: 90}, [clip("stumble", 3), nothing(22)]),
    ...at("card_arrived", {cooldown: 20, toward: "card"}, [clip("glance", 7), nothing(13)]),
    ...at("typing", {cooldown: 60}, [look("reading", 1), nothing(4)]),
    // a face the user puts on a message changes the eyes, every time; one the agent puts on in its voice is played out, every time
    ...Object.entries(USER_FACES).flatMap(([face, mood]) => at(`reacted:${face}`, {}, [look(mood, 1)])),
    ...Object.entries(VOICE_FACES).flatMap(([voice, faces]) => Object.entries(faces).map(([face, name]) => at(`agent_reacted:${face}`, {}, [clip(name, 1, {voices: [voice]})])[0])),
    ...Object.entries(EVERY_VOICE_FACES).flatMap(([face, name]) => at(`agent_reacted:${face}`, {}, [clip(name, 1)])),
    // the idle acts, while it has nothing to do, a wait on a run, a worker or the user as much as idle
    ...at("pastime", {}, [
        pastime("look_around", 6, 20, 25),
        pastime("stretch", 3, 90, 90),
        // after a long quiet it lies down on its back for a while, whistling, on any floor it stands on
        pastime("rest", 3, 180, 120),
        pastime("yawn", 2, 60, 60),
        pastime("polish", 4, 45, 60, {when: {voices: ["butler"]}}),
        pastime("whistle", 4, 45, 60, {when: {voices: ["coach"]}}),
        pastime("sip", 4, 45, 60, {when: {voices: ["colleague"]}}),
        pastime("headphones", 4, 45, 60, {when: {voices: ["homie"]}}),
        pastime("shield_polish", 4, 45, 60, {when: {voices: ["squire"]}}),
        // the shenanigan: it hops up the bubbles off the top of the chat and comes back down on a parachute (figure/skyward.js); it turns
        // a salto only now and then on a high jump up onto a bubble (the jump moment), never where it stands
        {...showpiece(clip("hop_up", 2)), flies: true},
        // it disco dances under a disco ball: now and then where there is room over its hat for the ball, and most of all standing on a
        // bubble with another above it to hang the ball from (perches.js discoBall), one cooldown for both
        showpiece(clip("disco", 2, {ball: "room"})),
        showpiece(clip("disco", 60, {ball: "bubble"})),
        nothing(560),
    ]),
    // how a held clip is played for one stretch of it: searching with the magnifying glass, binoculars, a flashlight in a dark corner or
    // under a lifted corner of the floor; typing on or stopping to think at the laptop; watching the UFO with a hand shading the eyes or
    // waving up at it; and while the context compacts, packed into a box that shrinks, squashed under a press, vacuuming up words, or
    // squaring a stack of papers
    ...at("held:search", {}, [clip("search", 3), clip("binoculars", 2), clip("flashlight", 2), clip("peek_under", 1)]),
    ...at("held:type", {}, [clip("type", 3), clip("type_ponder", 1)]),
    ...at("held:watch", {}, [clip("watch", 2), clip("wave_up", 1)]),
    ...at("held:compacting", {}, [clip("pack_box", 3), clip("press", 2), clip("vacuum", 2), clip("compacting", 1)]),
    // the work's own acts, each only while that work goes on and then weighted heavily, a spell keeping it up a while so it is seen though
    // the tool lasts a moment: the laptop while the agent edits, the book while it reads, the searching while it searches
    ...at("spell", {}, [pick("writing", 12, {state: "writing"}), pick("reading", 12, {state: "reading"}), pick("searching", 12, {state: "searching"}), nothing(4)]),
    // the mouse pointer tickling it (tickle.js): it swats at the pointer every time, as often as it is tickled
    ...at("tickled", {}, [showpiece(clip("tickle_swat", 1))]),
    // a slow docked bar near its end: the figure gets eager for it now and then
    ...at("eager", {}, [clip("eager", 2, {slow: true}), nothing(3)]),
    // a jump up more than the figure's own height now and then turns over backwards on the way
    ...at("jump", {}, [showpiece(clip("backflip", 7, {high: true})), clip("jump", 13)]),
    // a climb past three of the figure's heights (climbs.js POGO): now and then on the pogo stick it pulls from behind its back, else
    // hopping up the bubbles on the way, and on the stick always when there are none to hop on
    ...at("climb", {}, [showpiece(pick("pogo", 2)), pick("hops", 3, {footholds: true})]),
    // while a run goes, whether the figure builds a server unit now (UNIT)
    ...at("unit", {cooldown: UNIT.every}, [pick("unit", UNIT.weight), nothing(1)]),
    // what takes the work away once it is committed, the UFO or the crane, one of them every time with no cooldown, and the side the crane
    // rolls in from
    ...at("carrier", {}, [pick("ufo", 3), pick("crane", 1)]),
    ...at("crane_from", {}, [pick("left", 1), pick("right", 1)]),
    // a perch on a bubble: a hang from its corner by a free hand, or a stand on its corner
    ...at("perch", {}, [pick("hang", 2, {hands: true}), pick("stand", 3)]),
    // a falling figure caught by a bubble it falls past, but never soon after another fall, or dropping straight home
    ...at("fall", {}, [pick("caught", 1, {settled: true}), pick("home", 1)]),
    // a digit a blow's dust lets out
    ...at("digit", {}, [pick("0", 1), pick("1", 1)]),
    // where the figure goes when nothing calls it, and how long it stays, in seconds between the two: rests on a corner of the edge, sits on
    // the corner itself with its legs over the end, strolls the edge, perches on a bubble or stands on a tab
    ...at("roam", {}, [
        pick("rest", 35, {}, {stay: [15, 40]}),
        pick("seat", 15, {}, {stay: [15, 40]}),
        pick("edge", 25, {}, {stay: [8, 20]}),
        pick("bubble", 15, {}, {stay: [15, 40], shenanigan: true}),
        pick("tab", 10, {}, {stay: [10, 25]}),
        // with nothing to do, it sits on the edge of the floor it stands on, facing the viewer, its legs over the edge
        pick("ledge", 14, {free: true}, {stay: [20, 45]}),
        // with nothing to do and a bubble near the middle of the chat above it, it ties a rope swing under that bubble and swings
        showpiece(pick("rope_swing", 8, {free: true, swings: true}, {stay: [25, 50]})),
    ]),
    // where along the floor it sits on the edge: around the middle, or a third of the way from either end, never at an end
    ...at("ledge_at", {}, [pick("middle", 2, {}, {along: 1 / 2}), pick("third", 1, {}, {along: 1 / 3}), pick("two_thirds", 1, {}, {along: 2 / 3})]),
];

// whether a condition holds where things stand: its moment, a voice among its voices, a state lasted at least so long, and anything else
// it names, as a free hand or a high jump, as `scene` has it
const holds = (when, scene) =>
    Object.entries(when).every(([key, wanted]) => (key === "voices" ? wanted.includes(scene.voice) : key === "lasted" ? scene.lasted >= wanted : scene[key] === wanted));

// what an entry's cooldown is kept under: its moment, or itself when it stands apart
const cooledUnder = (entry) => (entry.apart ? `${entry.when.moment}/${entry.name}` : entry.when.moment);

// The entries that may play where things stand, `scene`: its moment and what else the conditions read, whether the figure `has` a clip,
// and, with `memory` (cooldown key to when it last played, in seconds) and `now`, only those not cooling down. With a `tally` of the acts
// played since the last shenanigan at SHENANIGAN.after or more, only the shenanigans, where there is one; and never the tally's last act
// again while anything else may play.
export function choicesFor(scene) {
    const has = scene.has ?? (() => true);
    const since = (key) => scene.now - (scene.memory.get(key) ?? -Infinity);
    const cooled = (entry) => !scene.memory || ((!entry.cooldown || since(cooledUnder(entry)) >= entry.cooldown) && (!entry.waits || since(entry.when.moment) >= entry.waits));
    const choices = PILE.filter((entry) => holds(entry.when, scene) && (entry.kind !== "clip" || has(entry.name)) && cooled(entry));
    const due = (scene.tally?.plain ?? 0) >= SHENANIGAN.after && choices.some((entry) => entry.shenanigan);
    const kept = due ? choices.filter((entry) => entry.shenanigan) : choices;
    // the act just played is not drawn again at once, while anything else may play
    const fresh = kept.filter((entry) => entry.kind === "nothing" || entry.name !== scene.tally?.last);
    return fresh.some((entry) => entry.kind !== "nothing") ? fresh : kept;
}

// One entry drawn by weight from those that may play in `scene` (choicesFor), with `random`; null when none may, or when nothing is drawn.
// The one drawn starts its cooldown in the scene's memory, and is counted on the scene's tally, which a shenanigan sets back to none.
export function draw(scene, random) {
    const choices = choicesFor(scene);
    let roll = random() * choices.reduce((sum, entry) => sum + entry.weight, 0);
    const drawn = choices.find((entry) => (roll -= entry.weight) < 0) ?? choices.at(-1) ?? null;
    if (!drawn || drawn.kind === "nothing") return null;
    scene.memory?.set(cooledUnder(drawn), scene.now);
    if (drawn.waits) scene.memory?.set(drawn.when.moment, scene.now);
    if (scene.tally) Object.assign(scene.tally, {plain: drawn.shenanigan ? 0 : scene.tally.plain + 1, last: drawn.name});
    return drawn;
}

// an entry as a line: what it is, its weight and the condition it plays under
export const lineOf = (entry) =>
    `${entry.shenanigan ? "shenanigan " : ""}${entry.kind} ${entry.name} ×${entry.weight} when ${Object.entries(entry.when).map(([key, value]) => `${key}=${value}`).join(" ")}${entry.kind === "clip" ? (entry.cut ? `, cut after ${entry.cut}s` : ", plays out") : ""}`;

// whether the clip `name` may be cut off by the next moment once it has played `seconds`: only an act of CUT that has played its least
export const cutsAfter = (name, seconds) => Boolean(CUT[name]) && seconds >= CUT[name];
