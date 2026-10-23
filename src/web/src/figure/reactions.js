import {HELD, WORKING, eggFor} from "../domain/figureState.js";

// What the figure does about what happens around it, and how often. Every number that decides it is here, so it can be tuned in one place.
// Nothing fires every time: `odds` is the chance a moment is reacted to at all, and `cooldown` the seconds before the same reaction may
// play again, so the figure is a creature that notices things now and then, not a status icon.

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

// the ways the figure celebrates, by weight: a jump for joy with its hands up, a party horn blown
const CELEBRATIONS = [{clip: "joy", weight: 2}, {clip: "party_horn", weight: 1}];

// The clips a held clip is played as, one picked by its weight each time the figure takes it up, so one stretch of the same work looks
// unlike the last: searching with the magnifying glass, binoculars, a flashlight in a dark corner, or under a lifted corner of the floor;
// typing on, or stopping to think at the laptop; watching the UFO with a hand shading the eyes, or waving up at it; and while the context
// compacts, packed into a box that shrinks, squashed under a press, vacuuming up words, or squaring a stack of papers
export const VARIANTS = {
    search: [{clip: "search", weight: 3}, {clip: "binoculars", weight: 2}, {clip: "flashlight", weight: 2}, {clip: "peek_under", weight: 1}],
    type: [{clip: "type", weight: 3}, {clip: "type_ponder", weight: 1}],
    watch: [{clip: "watch", weight: 2}, {clip: "wave_up", weight: 1}],
    compacting: [{clip: "pack_box", weight: 3}, {clip: "press", weight: 2}, {clip: "vacuum", weight: 2}, {clip: "compacting", weight: 1}],
};

// one of `among` ({clip, weight}) the figure has, picked by weight with `random`, or null when it has none of them
function pick(among, random, has) {
    const had = among.filter((each) => has(each.clip));
    let roll = random() * had.reduce((sum, each) => sum + each.weight, 0);
    return had.find((each) => (roll -= each.weight) < 0)?.clip ?? had.at(-1)?.clip ?? null;
}

// the clip a held clip is played as this time (VARIANTS), itself when it has no others
export const variantOf = (clip, random, has) => (VARIANTS[clip] ? pick(VARIANTS[clip], random, has) : null) ?? clip;

// The reactions to a moment, by its name; the first whose roll succeeds plays. `moment` is a beat, a card seen to change, or a held state.
// A clip moves the body once; a look changes only the eyes. Card-directed clips face their source.
// A reaction with `among` plays one of those clips, picked by its weight, and keeps its cooldown under its moment, so the same moment is
// not acted out the same way every time. One that goes `onto` its card plays there: the figure goes to the chat mark that finished, jumps
// onto it and celebrates on it, so it is plain what it celebrates.
export const REACTIONS = [
    {moment: "tests_passed", among: CELEBRATIONS, odds: 0.75, cooldown: 20, toward: "card", onto: true},
    {moment: "tests_failed", clip: "startled", odds: 0.75, cooldown: 20, toward: "card"},
    {moment: "committed", among: CELEBRATIONS, odds: 0.6, cooldown: 30, toward: "card", onto: true},
    // what the agent has just done in the journal, acted out now and then, never every time
    {moment: "messaged", clip: "post_dove", odds: 0.35, cooldown: 120},
    {moment: "task_finished", among: [{clip: "stamp", weight: 4}, ...CELEBRATIONS], odds: 0.5, cooldown: 90, toward: "card", onto: true},
    {moment: "task_filed", among: [{clip: "pin_note", weight: 3}, {clip: "nod", weight: 1}], odds: 0.4, cooldown: 90},
    {moment: "question_asked", among: [{clip: "ask_sign", weight: 3}, {clip: "think", weight: 1}], odds: 0.6, cooldown: 60},
    {moment: "worker_sent", among: [{clip: "whistle_runner", weight: 3}, {clip: "wave", weight: 1}], odds: 0.5, cooldown: 90},
    {moment: "reported", among: [{clip: "scroll", weight: 3}, {clip: "nod", weight: 1}], odds: 0.5, cooldown: 90},
    {moment: "fact_filed", among: [{clip: "file_card", weight: 3}, {clip: "nod", weight: 1}], odds: 0.4, cooldown: 120},
    {moment: "check_passed", among: CELEBRATIONS, odds: 0.25, cooldown: 120, toward: "card", onto: true},
    // standing still, it looks about now and then: to one side, the other, or up, so standing still is never the same loop
    {moment: "standing", among: [{clip: "look_left", weight: 2}, {clip: "look_right", weight: 2}, {clip: "look_up", weight: 1}], odds: 0.15, cooldown: 7},
    // landing from a launch it very rarely trips and falls to its knees
    {moment: "launched", clip: "tumble", odds: 0.06, cooldown: 300},
    // a break from the hammering now and then
    // the bar the figure was eager for has ended, as its card says: it jumps and celebrates, or, the more for having been eager, is crushed
    // and then fumes
    {moment: "bar_done", among: CELEBRATIONS, odds: 1, cooldown: 0},
    {moment: "bar_failed", clip: "fume", odds: 1, cooldown: 0},
    {moment: "building", among: [{clip: "wipe_brow", weight: 2}, {clip: "look_around", weight: 1}], odds: 0.08, cooldown: 30},
    {moment: "failed", clip: "shake", odds: 0.6, cooldown: 20, toward: "card"},
    {moment: "refused", clip: "shake", odds: 0.5, cooldown: 20},
    {moment: "work_done", clip: "stretch", odds: 0.4, cooldown: 120},
    {moment: "answered", look: "amused", odds: 0.6, cooldown: 15},
    {moment: "heard", voice: "butler", clip: "bow", odds: 0.5, cooldown: 30},
    {moment: "heard", voice: "squire", clip: "salute", odds: 0.5, cooldown: 30},
    {moment: "heard", voices: ["coach", "colleague", "homie"], clip: "nod", odds: 0.5, cooldown: 30},
    {moment: "long_walk", clip: "stumble", odds: 0.12, cooldown: 90},
    {moment: "card_arrived", clip: "glance", odds: 0.35, cooldown: 20, toward: "card"},
    {moment: "typing", look: "reading", odds: 0.2, cooldown: 60},
    // a face the user puts on a message is aimed at the figure, so it always answers
    {moment: "reacted:\u2764\ufe0f", look: "hearts", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\udc4d", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83c\udf89", look: "startled", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\ude04", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\udc40", look: "reading", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\ude4f", look: "hearts", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\udc4e", look: "worried", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\udc94", look: "worried", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83d\ude20", look: "angry", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83c\udfa9", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83e\uddd0", look: "reading", odds: 1, cooldown: 0},
    {moment: "reacted:\ud83e\udd42", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:🤙", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:😎", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:🔥", look: "startled", odds: 1, cooldown: 0},
    {moment: "reacted:💪", look: "amused", odds: 1, cooldown: 0},
    {moment: "reacted:🏆", look: "hearts", odds: 1, cooldown: 0},
    {moment: "reacted:⚔️", look: "angry", odds: 1, cooldown: 0},
    {moment: "reacted:🛡️", look: "worried", odds: 1, cooldown: 0},
    {moment: "reacted:🏰", look: "amused", odds: 1, cooldown: 0},
    // a face the agent puts on a message in its own voice is played out by the figure, every time
    ...Object.entries(VOICE_FACES).flatMap(([voice, faces]) =>
        Object.entries(faces).map(([face, clip]) => ({moment: `agent_reacted:${face}`, voice, clip, odds: 1, cooldown: 0}))
    ),
    ...Object.entries(EVERY_VOICE_FACES).map(([face, clip]) => ({moment: `agent_reacted:${face}`, clip, odds: 1, cooldown: 0})),
];

// how long the eyes keep a look, counted only while they are shown
export const LOOK_SECONDS = 3;

// whether a figure turned `facing` degrees shows its eyes: it faces no further than sideways from the viewer
export const eyesShown = (facing) => Math.abs(((((facing + 180) % 360) + 360) % 360) - 180) <= 90;

// how many times a second the eyes are drawn while they wear a look
export const LOOK_FPS = 12;

// a look the eyes take on at `now` seconds, not yet seen
export const lookOf = (mood, now) => ({mood, began: now, seen: 0});

// The look on the eyes of a figure turned `facing` degrees at `now` seconds: the look as it stands after this moment, null once it has
// been seen its time, and the eyes to draw with it, stepped as they are drawn, or none. Its clock runs only while the eyes are shown, so
// a look that comes while the figure faces away waits for it to turn round.
export function eyesAt(looking, facing, now) {
    if (!looking) return {looking: null, eyes: null};
    if (!eyesShown(facing)) return {looking: {...looking, began: now - looking.seen}, eyes: null};
    const seen = now - looking.began;
    if (seen >= LOOK_SECONDS) return {looking: null, eyes: null};
    return {looking: {...looking, seen}, eyes: {mood: looking.mood, seconds: Math.floor(seen * LOOK_FPS) / LOOK_FPS, lasts: LOOK_SECONDS}};
}

// whether a look makes the figure let go of where it is: it hangs there with its back to the viewer, so it lets go to turn round
export const letsGoFor = (place) => place.posture === "hang" && !eyesShown(place.face);

// Things it does by itself while it has nothing to do (FREE): once the state has lasted `after` seconds, every so often (a random number of seconds
// between the two in `every`), and then with chance `odds`
export const AMBIENT = [
    {clip: "look_around", after: 60, every: [25, 60], odds: 0.6},
    {clip: "stretch", after: 240, every: [90, 180], odds: 0.5},
    // after a long quiet it lies down on its back for a while, whistling, on any floor it stands on
    {clip: "rest", after: 300, every: [120, 240], odds: 0.6},
    {clip: "yawn", after: 120, every: [60, 150], odds: 0.4},
    // now and then it hops up the bubbles off the top of the screen and comes back down on a parachute (figure/skyward.js)
    {clip: "hop_up", flies: true, after: 90, every: [150, 360], odds: 0.4},
    {clip: "polish", voice: "butler", after: 90, every: [60, 150], odds: 0.5},
    ...[
        ["coach", "whistle"], ["colleague", "sip"], ["homie", "headphones"], ["squire", "shield_polish"],
    ].map(([voice, clip]) => ({voice, clip, after: 90, every: [60, 150], odds: 0.5})),
];

// The states in which the figure has nothing to do, and so plays its pastimes: idle, or waiting, on a run, a worker or the user alike
export const FREE = new Set(["idle", "waiting", "asking"]);

// the agent has worked for at least this many seconds when it settles, for "work_done" to be a moment
export const LONG_WALK_SECONDS = 5;

export function walkingMoment(trip, began, now) {
    if (!trip?.moves || trip.hopping) return {began: 0, moment: null};
    const since = began || now;
    return {began: since, moment: now - since >= LONG_WALK_SECONDS ? {beat: "long_walk", time: now} : null};
}

export const WORKED_SECONDS = 30;

// Now and then an edit sets the figure typing at its laptop for a spell of a random number of seconds between the two in `seconds`, kept
// while its agent works on, so the laptop is seen though an edit lasts a moment: with chance `odds`, and not again within `cooldown`
// seconds of the last roll
export const TYPING = {odds: 0.35, cooldown: 45, seconds: [8, 14]};

// The typing spell after this look at `now`, the agent's state being `state`: the spell in hand while it lasts, else a new one rolled for
// an edit, {began, until, next}, `next` being when the next may be rolled
export function typingSpell(state, spell, now, random) {
    if (spell && now < spell.until) return spell;
    if (state !== "writing" || now < (spell?.next ?? 0)) return spell;
    const [least, most] = TYPING.seconds;
    return random() < TYPING.odds ? {began: now, until: now + least + random() * (most - least), next: now + TYPING.cooldown} : {began: 0, until: 0, next: now + TYPING.cooldown};
}

// The held state as the figure plays it (figureState.js figureStateOf), writing for the spell while it lasts and its agent works
export const typingIn = (held, spell, now) => (spell && now < spell.until && WORKING.has(held.state) ? {state: "writing", since: spell.began} : held);

// Once a docked bar's run looks about `lead` seconds from its end at the pace it has gone, now and then, with chance `odds`, once a bar, the
// figure gets eager for it to end: it hurries onto the bar, taps its feet fast, then points down at it, bouncing, until it ends, and is
// never called off before. Only a slow run counts, one `after` seconds old by then, so a quick run never does.
export const EAGER = {lead: 5, odds: 0.4, after: 10};

// the seconds a run `elapsed` seconds old with `share` of it done has left, at the pace it has gone
export const secondsLeft = (elapsed, share) => (share > 0 ? (elapsed / share) * (1 - share) : Infinity);

// The figure's eagerness at `now` seconds for the bar docked over the compose box, `progress` (places.js progressOf), or null with none:
// the bar it rolled for and whether it is eager for it; and the moment the bar's end is once it ends while the figure is eager, a pass or
// a failure. Only the bar's end, or the bar going, ends it.
export function eagerFor(progress, eager, random, now) {
    const same = Boolean(progress) && progress.bar === eager?.bar;
    if (same && eager.on && progress.ended) return {eager: {...eager, on: false}, moment: {beat: progress.ended === "good" ? "bar_done" : "bar_failed"}};
    if (!progress || progress.ended) return {eager: eager && {...eager, on: false}, moment: null};
    if (same) return {eager, moment: null};
    const elapsed = now - progress.began;
    if (secondsLeft(elapsed, progress.share) > EAGER.lead) return {eager, moment: null};
    return {eager: {bar: progress.bar, on: elapsed >= EAGER.after && random() < EAGER.odds}, moment: null};
}

// A jump of more than this many of the figure's own heights sometimes turns over backwards on the way
export const FLIP_OVER = 1;
export const FLIP_ODDS = 0.35;

// what a reaction does, a clip, a look or one of several clips for its moment, which is what its cooldown is kept under
const doing = (reaction) => reaction.clip ?? (reaction.among ? `moment:${reaction.moment}` : `look:${reaction.look}`);

// whether the figure has what a reaction plays
const playable = (reaction, has) => (reaction.clip ? has(reaction.clip) : !reaction.among || reaction.among.some((each) => has(each.clip)));

// the reaction to this moment, or null: the first for it that is off cooldown and wins its roll, with the clip it plays picked when it has
// several. `memory` maps what a reaction does to when it last did it, in seconds, and is filled in here
export function reactionTo(moment, memory, now, random, voice = "", has = () => true) {
    const found = REACTIONS.find(
        (each) => each.moment === moment && (!each.voice || each.voice === voice) && (!each.voices || each.voices.includes(voice)) && playable(each, has) && now - (memory.get(doing(each)) ?? -Infinity) >= each.cooldown && random() < each.odds
    );
    if (!found) return null;
    memory.set(doing(found), now);
    return found.among ? {...found, clip: pick(found.among, random, has)} : found;
}

// the clip an ambient moment calls for after `held` seconds of `state`, or "": `next` maps a clip's name to when it may next play
export function ambientFor(state, held, next, now, random, voice = "", has = () => true) {
    const found = AMBIENT.find((each) => FREE.has(state) && (!each.voice || each.voice === voice) && has(each.clip) && held >= each.after && now >= (next.get(each.clip) ?? 0));
    if (!found) return "";
    const [least, most] = found.every;
    next.set(found.clip, now + least + random() * (most - least));
    return random() < found.odds ? found.clip : "";
}

// whether this jump up, `height` pixels for a figure `size` pixels tall, turns over on the way
export const flips = (height, size, random) => height > FLIP_OVER * size && random() < FLIP_ODDS;

// the moment each held clip is, every look while it is held: building while the figure hammers, standing while it stands idle
const WHILE = {work: "building", idle: "standing"};

// The moments of the agent's work and of the user at the compose box at `now`: typing since the last look, the moment of the held clip
// (WHILE), and the end of a stretch of work that lasted WORKED_SECONDS. `began` is when the work in hand began, 0 with none; it returns the moments and that time as it is now.
export function workMoments(state, typed, began, now) {
    const held = HELD[state];
    const moments = [...(typed ? [{beat: "typing", time: now}] : []), ...(WHILE[held] ? [{beat: WHILE[held], time: now}] : [])];
    if (WORKING.has(state)) return {moments, began: began || now};
    if (began && now - began >= WORKED_SECONDS) moments.push({beat: "work_done", time: now});
    return {moments, began: 0};
}

// What the figure does about a moment: the egg of `voice` that belongs to it, else its reaction when the roll says so, as a beat the body
// plays once ({beat: {clip, card}}), `card` being the chat mark it turns to, or a look its eyes take on ({look: mood}); null for nothing.
// `memory` holds when each reaction last played (`reacted`) and the eggs played so far (`played`), and is filled in here; `has(clip)`
// says whether the figure has a clip.
export function answerTo(moment, voice, memory, now, random, has) {
    const egg = eggFor(voice, moment, memory.played);
    if (egg && has(egg.clip)) {
        memory.played.push(egg);
        return {beat: {clip: egg.clip, card: ""}};
    }
    const reaction = reactionTo(moment.beat, memory.reacted, now, random, voice, has);
    if (reaction?.look) return {look: reaction.look};
    if (reaction && has(reaction.clip)) return {beat: {clip: reaction.clip, card: reaction.toward === "card" ? moment.card || "" : "", ...(reaction.onto && moment.card ? {onto: true} : {})}};
    return null;
}

// What the figure does by itself after `waited` ({state, lasted}), as a beat, `flies` when it is the run off the top of the screen, or null: only while it is calm, at rest in the idle state
// with nothing to play, its hands free and neither coming nor going. `scene` says where things stand; `due` when each pastime may next
// play, filled in here.
export function pastimeFor(scene, waited, due, now, random, has) {
    const calm = FREE.has(waited.state) && scene.place.posture !== "hang" && !scene.beats && !scene.arriving && !scene.leaving && !scene.moving;
    if (!calm) return null;
    const clip = ambientFor(waited.state, waited.lasted, due, now, random, scene.voice, has);
    return clip && has(clip) ? {clip, card: "", flies: Boolean(AMBIENT.find((each) => each.clip === clip).flies)} : null;
}
