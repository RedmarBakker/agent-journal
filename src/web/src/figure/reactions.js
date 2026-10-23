import {HELD, WORKING, eggFor} from "../domain/figureState.js";
import {draw} from "./pile.js";

// What the figure does about what happens around it, and when. Which animation plays is drawn from the one pile (pile.js); here are the
// moments it is drawn for, and how what is drawn is played, so the figure is a creature that notices things now and then, not a status icon.

// the carrier that comes this time to take the work away (pile.js carrier), the UFO or the claw crane, and the side the crane rolls in from
export const carrierOf = (random) => draw({moment: "carrier"}, random).name;
export const craneFrom = (random) => draw({moment: "crane_from"}, random).name;

// the clip a held clip is played as for this stretch of it (pile.js held:), itself when it is played one way only
export const variantOf = (clip, random, has) => draw({moment: `held:${clip}`, has}, random)?.name ?? clip;

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

// Now and then an edit, a read or a search, the work of `kept`, sets the figure typing at its laptop, reading its book or searching for a
// spell of a random number of seconds between the two in `seconds`, kept while its agent works on, so the act is seen though the tool lasts
// a moment; drawn from the pile (pile.js spell), and not drawn again within `every` seconds of the last draw, won or not
export const SPELL = {seconds: [10, 18], every: 30, kept: ["writing", "reading", "searching"]};

// The spell after this look at `now`, the agent's state being `state`: the spell in hand while it lasts, else one drawn for an edit or a
// read, {state, began, until, next}, `next` being when the next may be drawn
export function spellFor(state, spell, now, random, tally = null) {
    if (spell && now < spell.until) return spell;
    if (!SPELL.kept.includes(state) || now < (spell?.next ?? 0)) return spell;
    const drawn = draw({moment: "spell", state, tally}, random);
    const [least, most] = SPELL.seconds;
    return drawn ? {state: drawn.name, began: now, until: now + least + random() * (most - least), next: now + SPELL.every} : {state, began: 0, until: 0, next: now + SPELL.every};
}

// The held state as the figure plays it (figureState.js figureStateOf), the spell's while it lasts and its agent works
export const spellIn = (held, spell, now) => (spell && now < spell.until && WORKING.has(held.state) ? {state: spell.state, since: spell.began} : held);

// Once a docked bar's run looks about `lead` seconds from its end at the pace it has gone, now and then, as the pile draws it (pile.js
// eager), once a bar, the figure gets eager for it to end: it hurries onto the bar, taps its feet fast, then points down at it, bouncing,
// until it ends, and is never called off before. Only a slow run counts, one `after` seconds old by then, so a quick run never does. A run
// that has gone on `long` seconds is anticipated every time, and `urgent`ly: the figure drops whatever it does for it.
export const EAGER = {lead: 5, after: 10, long: 120};

// the seconds a run `elapsed` seconds old with `share` of it done has left, at the pace it has gone
export const secondsLeft = (elapsed, share) => (share > 0 ? (elapsed / share) * (1 - share) : Infinity);

// The figure's eagerness at `now` seconds for the bar docked over the compose box, `progress` (places.js progressOf), or null with none:
// the run it rolled for, known by when its card began so a bar drawn again is the same run, and whether it is eager for it; and the moment
// the bar's end is once it ends while the figure is eager, a pass or a failure, once for the run. Only the bar's end, or the bar going, ends it.
export function eagerFor(progress, eager, random, now) {
    const same = Boolean(progress) && progress.began === eager?.run;
    if (same && eager.on && progress.ended) return {eager: {...eager, on: false}, moment: {beat: progress.ended === "good" ? "bar_done" : "bar_failed"}};
    if (!progress || progress.ended) return {eager: eager && {...eager, on: false}, moment: null};
    if (same) return {eager, moment: null};
    const elapsed = now - progress.began;
    if (secondsLeft(elapsed, progress.share) > EAGER.lead) return {eager, moment: null};
    if (elapsed > EAGER.long) return {eager: {run: progress.began, on: true, urgent: true}, moment: null};
    return {eager: {run: progress.began, on: draw({moment: "eager", slow: elapsed >= EAGER.after}, random)?.name === "eager"}, moment: null};
}

// A jump of more than this many of the figure's own heights is high, and now and then turns over backwards on the way (pile.js jump)
export const FLIP_OVER = 1;

// The reaction to this moment drawn from the pile, or null when nothing is drawn: a clip the body plays or a look the eyes take on, and
// whether it turns toward its card or goes onto it. `memory` maps a moment to when it last played, in seconds, and is filled in here.
export function reactionTo(moment, memory, now, random, voice = "", has = () => true, tally = null) {
    const drawn = draw({moment, voice, has, memory, now, tally}, random);
    if (!drawn) return null;
    return {[drawn.kind === "look" ? "look" : "clip"]: drawn.name, toward: drawn.toward ?? "", onto: Boolean(drawn.onto)};
}

// The act drawn for `held` seconds of `state`, as its entry, or null: the idle acts while the figure has nothing to do, and the
// shenanigans in any state; `memory` holds when each act last played and `tally` the acts since the last shenanigan, filled in here, and
// `ball` where a disco ball may hang over the figure (perches.js discoBall), "" with no room
export const pastimeOf = (state, held, memory, now, random, voice = "", has = () => true, tally = null, ball = "") =>
    draw({moment: "pastime", free: FREE.has(state), lasted: held, voice, has, memory, now, tally, ball}, random);

// whether this jump up, `height` pixels for a figure `size` pixels tall, turns over on the way, as the pile draws it; `memory` holds when the
// salto last turned, `now` being the time, so it waits its cooldown (pile.js SHOWPIECES)
export const flips = (height, size, random, memory, now) => draw({moment: "jump", high: height > FLIP_OVER * size, memory, now}, random).name === "backflip";

// the moment each held clip is, every look while it is held: building while the figure hammers, standing while it stands idle or thinks
const WHILE = {work: "building", idle: "standing", think: "standing"};

// The moments of the agent's work and of the user at the compose box at `now`: typing since the last look, the moment of the held clip
// (WHILE), the end of a stretch of thinking, the state having been `was` at the last look, and the end of a stretch of work that lasted
// WORKED_SECONDS. `began` is when the work in hand began, 0 with none; it returns the moments and that time as it is now.
export function workMoments(state, typed, began, now, was = state) {
    const held = HELD[state];
    const moments = [...(typed ? [{beat: "typing", time: now}] : []), ...(WHILE[held] ? [{beat: WHILE[held], time: now}] : [])];
    if (was === "thinking" && state !== "thinking") moments.push({beat: "thought", time: now});
    if (WORKING.has(state)) return {moments, began: began || now};
    if (began && now - began >= WORKED_SECONDS) moments.push({beat: "work_done", time: now});
    return {moments, began: 0};
}

// What the figure does about a moment: the egg of `voice` that belongs to it, else its reaction when the roll says so, as a beat the body
// plays once ({beat: {clip, card, mark}}), `card` being the chat mark it turns to and `mark` the one that set it off, as the call says whom
// it calls (figureState.js callLines), or a look its eyes take on ({look: mood}); null for nothing.
// `memory` holds when each reaction last played (`reacted`), the eggs played so far (`played`) and the acts since the last shenanigan
// (`tally`), and is filled in here; `has(clip)`
// says whether the figure has a clip.
export function answerTo(moment, voice, memory, now, random, has) {
    const egg = eggFor(voice, moment, memory.played);
    if (egg && has(egg.clip)) {
        memory.played.push(egg);
        return {beat: {clip: egg.clip, card: ""}};
    }
    const reaction = reactionTo(moment.beat, memory.reacted, now, random, voice, has, memory.tally);
    if (reaction?.look) return {look: reaction.look};
    if (reaction?.clip) return {beat: {clip: reaction.clip, card: reaction.toward === "card" ? moment.card || "" : "", ...(moment.card ? {mark: moment.card} : {}), ...(reaction.onto && moment.card ? {onto: true} : {})}};
    return null;
}

// What the figure does by itself after `waited` ({state, lasted}), as a beat, `flies` when it is the run off the top of the screen, or
// null: only while it is calm, nothing to play, off any hang or swing and neither coming nor going. `scene` says where things stand; `memory` when
// each act last played and `tally` the acts since the last shenanigan, filled in here.
export function pastimeFor(scene, waited, memory, now, random, has, tally = null) {
    const calm = scene.place.posture !== "hang" && !scene.place.swings && !scene.beats && !scene.arriving && !scene.leaving && !scene.moving;
    if (!calm) return null;
    const drawn = pastimeOf(waited.state, waited.lasted, memory, now, random, scene.voice, has, tally, scene.ball);
    return drawn && {clip: drawn.name, card: "", flies: Boolean(drawn.flies)};
}

// The beat queue with `beat` put before every other: the beat at its head, when it is the clip playing now, `playingClip`, is broken off
// and dropped, so it never plays again from its start once `beat` has played
export const queuedFirst = (beats, beat, playingClip) => [beat, ...(beats[0]?.clip === playingClip ? beats.slice(1) : beats)];

// How fast the figure's head can swing its look, in radians a second: a pointer moved faster is followed at this pace
export const LOOK_TURN_SPEED = 2 * Math.PI;

// The point the head looks at next, from the one it looked at, `previous`, toward `target`, both on the page: turned about the head,
// `center`, by at most `largest` radians, at the target's own distance
export function headTurned(previous, target, center, largest) {
    const from = Math.atan2(previous.y - center.y, previous.x - center.x);
    const to = Math.atan2(target.y - center.y, target.x - center.x);
    const gap = Math.atan2(Math.sin(to - from), Math.cos(to - from));
    const angle = from + Math.max(-largest, Math.min(largest, gap));
    const reach = Math.hypot(target.x - center.x, target.y - center.y);
    return {...target, x: center.x + reach * Math.cos(angle), y: center.y + reach * Math.sin(angle)};
}

// Whether the figure answers a moment with `eager` as it stands (eagerFor): while it is eager for a run's end nothing takes it off,
// neither an act, a look nor a tickle; only the end itself, which eagerFor answers once the eagerness is over
export const isListening = (eager) => !eager?.on;
