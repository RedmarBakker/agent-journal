<script setup>
import {computed, onMounted, onUnmounted, ref, watch} from "vue";
import {agent} from "../composables/leadAgent.js";
import {useHomeViews} from "../composables/homeViews.js";
import {figureStatus, figureVisible, shownIn} from "../composables/voiceFigure.js";
import {fallOf} from "../domain/falls.js";
import {
    KEPT_WITHIN,
    aimedAt,
    airborneFrame,
    chaseRoom,
    fallingFrom,
    floorAt,
    legAt,
    legEnded,
    liftedLegs,
    slideAt,
    underWalker,
} from "../domain/figureMotion.js";
import {footingNow, footingOn, groundUnder, landingOn, latestFloors} from "../figure/floors.js";
import {useFigureBody} from "../composables/figureBody.js";
import {
    beatsAfter,
    cardsAfter,
    canSwitch,
    clipFor,
    clipOf,
    modeOf,
    closeAt,
    facesAfter,
    figureStateOf,
    frameIn,
    testResultsAfter,
    waitingSinceAt,
    withSystemCards,
} from "../domain/figureState.js";
import {loadVoiceFigure} from "../figure/assets.js";
import {builds, keptClear, stayAtHome, stepAside, stayForLook, stayingAt, targetFor} from "../figure/perches.js";
import {PARCEL, PILE, PUSH, UFO, behind, blowsLanded, hammerMs, pileSlot, pushStand, pushedTo, stopsOf, ufoAt} from "../figure/parcels.js";
import CodeParcel from "./CodeParcel.vue";
import FlyingSaucer from "./FlyingSaucer.vue";
import {answerTo, eyesAt, lookOf, pastimeFor, walkingMoment, workMoments} from "../figure/reactions.js";
import {
    clickedBody,
    CHANGE_SECONDS,
    HOME,
    POSTURES,
    SPRINT,
    boxAt,
    composeEdge,
    worldBox,
    drawnIn,
    facingToward,
    gripIn,
    groundEdge,
    progressEdge,
    hiddenAt,
    spotOf,
    tripTo,
} from "../figure/places.js";
import {STILL, landedSwing, swung} from "../figure/pendulum.js";
import "../figure/falls.css";
import {rows} from "../sync/rows.js";
import {store} from "../state/store.js";

// The figure plays what the figure modules decide: what it does in figureState.js and reactions.js, where it goes in perches.js, and how
// it stands and travels in places.js. This component holds only the drawing and the clock.

// The figure is this many pixels square, as the chat's flat figure is
const SIZE = 112;
// how far the UFO comes in from beyond its world's right and goes off beyond its left, and how high above the world's top, in pixels
const UFO_OFF = {right: 40, left: 60, above: -30};
// how long the figure takes to step back once the UFO starts lifting, in milliseconds
const STEP_BACK_MS = 400;
// how often the figure looks again at what the agent does and where things are, in milliseconds
const LOOK_EVERY = 1000;
const COMPOSE_TURN = 30;
const MARK_COUNT = 3;
const MARK_DRIFT_SECONDS = 3;
const MARK_HEAD_OFFSET = 0.1;

const props = defineProps({voice: {type: String, required: true}});

const canvas = ref(null);
const voice = computed(() => props.voice);
const {views} = useHomeViews();
const counts = computed(() => Object.fromEntries(Object.entries(views.value).map(([key, view]) => [key, view.count || 0])));

let player = null;
let clips = [];
let frameTimer = 0;
let lookTimer = 0;
const now = ref(Date.now() / 1000);
const waitingSince = ref(0);
// below the figure's feet in its picture, as a share of its height: the clips' ground row (figure.js GROUND)
const below = ref(0);
const {body, start: startBody, stop: stopBody} = useFigureBody(() => watchFooting());
// the one-off clips the body waits to play, oldest first, each as {clip, card}, `card` the chat mark it turns to while it plays, or ""
const beats = ref([]);
// the look the eyes wear (reactions.js eyesAt), or null
let looking = null;
// what the figure remembers between looks: when each reaction last played and the eggs played so far, when each pastime may next play,
// and the state each test run's card had when last looked at
const memory = {reacted: new Map(), played: []};
const pastimesDue = new Map();
const testStates = new Map();
const knownCards = new Set();
let seenAt = Date.now() / 1000;
let playing = {name: "", started: 0, shown: null, index: 0, closing: null};
// the clip on screen, so the page can draw what the rig has no bones for, such as the bug the squire chases
const shownClip = ref(null);
const shownFacing = ref(0);
// the posture the clip on screen is drawn in
let drawn = "stand";
// whether the legs on screen walk, as the page marks it for whoever measures the figure, beside the name of the clip on screen
const walking = ref(false);

// the agent's row with the system's cards that are its own, which the figure's beats are read from
const lead = computed(() => withSystemCards(agent.value, rows("messages")));
const held = computed(() => figureStateOf(agent.value, waitingSince.value, now.value));
// whether the figure belongs in the chat now: its agent is here, in a state Settings shows it in
const belongs = computed(() => Boolean(agent.value) && shownIn(store.settings?.voices?.avatar_shown, held.value.state));
// the stay the figure keeps while nothing calls it anywhere, and the box it was last clicked out of, kept clear of it (perches.js)
let stay = {where: "rest", until: 0};
let cleared = {until: 0};
// the sides, "l" or "r", of the hands this voice carries nothing in, which it can hang by
let hands = [];
// the user has typed in the compose box since the last look, and when the agent's work in hand began
let typed = false;
let workBegan = 0;
let walkBegan = 0;
// The parcels of code the figure has built (figure/parcels.js), oldest first, each {id, along, up, state, until, blows}: on the compose
// box's top `along` pixels from its left end and `up` pixels up the pile; "building" while the figure hammers it, until `until` on the
// page's clock, a random few seconds after it popped in, with `blows` blows landed on it; "built" once that time is up, until it is pushed
// onto the pile, and then "piled". `beside` is how far the blows land from the figure's feet, in pixels toward the viewer's right.
const parcels = ref([]);
let made = 0;
let beside = 0;
// how long one blow of the hammering is and where in it the blow lands (figure.js WORK), and the blows counted of the hammering on screen
let blow = {frames: 1, lands: 0};
let counted = {started: 0, landed: 0};
// The UFO once the work is committed, or null: when it set off, the stops it makes for the parcels it takes (parcels.js stopsOf), and
// where it comes from and goes off to; and what is drawn of it and of the parcels this frame
const ufo = ref(null);
const saucer = ref(null);
const drawnParcels = ref([]);
// how the figure watching the UFO stands this frame (figure.js watch), or null
let sky = null;
const shownFrame = ref(0);
const headAt = ref({x: 0.5, y: 0.3});

// the clip of this name the figure has, or idle when it has none
const clipNamed = (name) => clips.find((clip) => clip.name === name) || clips.find((clip) => clip.name === "idle");
const hasClip = (name) => clips.some((clip) => clip.name === name);
const canDraw = (name, posture) => clipNamed(name).postures.includes(posture);
// a clip the figure has and can draw in the posture it rests in, as a pastime must be
const drawnHere = (name) => hasClip(name) && canDraw(name, body.place.posture);
const figureSize = () => ({size: SIZE, below: below.value});

// the clip the figure's body shows for what its agent does: pushing a parcel it built while it stands behind it, standing by on its way
// round behind it, and while its agent runs a command and it has yet to get to where it builds, so it never hammers on the way there
function doing() {
    const pushing = parcels.value.find((each) => each.state === "built");
    if (pushing) return behind(parcelX(pushing), feetX()) ? "push" : "idle";
    if (parcels.value.some((each) => each.state === "building")) return "work";
    return builds(held.value.state) && !body.place.stays ? "idle" : clipOf(held.value.state);
}

// what plays now, as figureState.js clipFor decides it, with the clip itself in place of its name
function current() {
    if (!body.trip?.moves || body.trip.hopping) beats.value = beats.value.filter((beat) => beat.clip !== "stumble");
    const first = beats.value[0];
    const beat = first && {clip: first.clip, facing: facingToward(first.card, body.at.x + SIZE / 2)};
    const scene = {
        mode: modeOf(body),
        leaving: body.leaving,
        arriving: body.arriving,
        trip: body.trip,
        landing: body.landing,
        place: body.airborne ? {...body.place, posture: body.airborne.posture} : body.place,
        beat,
        state: held.value.state,
        doing: doing(),
        watching: Boolean(ufo.value),
        composeFacing: composeFacing(),
    };
    const wanted = clipFor(scene, canDraw);
    return {...wanted, clip: clipNamed(wanted.clip)};
}

function composeFacing() {
    const box = document.querySelector(HOME)?.getBoundingClientRect();
    return box ? (box.left + box.width / 2 >= body.at.x + SIZE / 2 ? COMPOSE_TURN : -COMPOSE_TURN) : 0;
}

const keyOf = (shown) => `${shown.clip.name}/${shown.facing}`;
// the frames a second a clip on screen plays at: its own, quickened on a sprint
const fpsOf = (shown) => shown.clip.fps * (shown.pace ?? 1);
// the clip's frame now, as a fraction between its drawn frames, so a pose moves on every display frame; the whole frame counts the play-out rules
const exactFrameOf = (shown) => ((performance.now() - playing.started) / 1000) * fpsOf(shown);
const frameOf = (shown) => Math.floor(exactFrameOf(shown));

// A clip plays out before another starts, or gives way at once when it is interruptible (figureState.js canSwitch). It is the one rule every
// clip goes through, so no clip needs its own check.
const playedOut = () =>
    !playing.shown ||
    (playing.closing !== null
        ? frameOf(playing.shown) >= playing.closing + playing.shown.clip.outro
        : canSwitch(playing.shown.clip, frameOf(playing.shown), playing.index));

// how far through its step the walk under a clip on the move is, stepped as the walk's own frames are, `pace` times as quick
function strideNow(pace) {
    const {frames, fps} = clipNamed("walk");
    return (((performance.now() / 1000) * fps * pace) % frames) / frames;
}

function step() {
    cancelAnimationFrame(frameTimer);
    if (!player || document.hidden) return;
    const wanted = current();
    if (playing.shown?.clip.outro && wanted.clip.name !== playing.shown.clip.name && playing.closing === null) {
        playing.closing = closeAt(playing.shown.clip, frameOf(playing.shown));
    }
    if (playing.closing !== null && wanted.clip.name === playing.shown.clip.name && frameOf(playing.shown) < playing.closing)
        playing.closing = null;
    // a clip that cuts in, as watching the UFO, takes over at once from whatever plays
    const finished = playedOut() || (wanted.clip.cuts && playing.shown?.clip.name !== wanted.clip.name);
    const continuing = keyOf(wanted) === playing.name && playing.closing === null;
    const shown = continuing || finished ? wanted : playing.shown;
    const key = keyOf(shown);
    if (playing.name !== key || (playing.closing !== null && finished)) {
        const turning = shown.clip.intro && playing.shown?.clip.name === shown.clip.name && playing.closing === null;
        playing = {name: key, started: turning ? playing.started : performance.now(), shown, index: 0, closing: null};
    }
    shownClip.value = shown.clip;
    shownFacing.value = shown.facing;
    const index = frameOf(shown);
    playing.index = index;
    if (shown.once && index >= shown.clip.frames) {
        if (shown.departure) {
            body.leaving = false;
            body.here = false;
            return;
        }
        if (shown.arrival) body.arriving = false;
        else if (shown.landed) body.landing = false;
        else beats.value = beats.value.slice(1);
        playing = {name: "", started: 0, shown: null, index: 0, closing: null};
        return step();
    }
    // the leg waiting for the clip it sets off with goes in the frame that clip goes on screen, so the walk is never drawn on the spot
    if (shown === wanted && wanted.startsLeg && !body.trip.moves) depart();
    drawn = drawnIn(shown, body.trip ? POSTURES[body.place.posture].travels : body.place.posture, body.trip?.moves);
    if (!body.trip?.started && !body.airborne) rest();
    flyUfo();
    const look = eyesAt(looking, shown.facing, performance.now() / 1000);
    looking = look.looking;
    const pace = shown.pace ?? 1;
    const stride = drawn === "walk" ? strideNow(pace) : null;
    walking.value = stride !== null || shown.clip.name === "walk";
    shownFrame.value = frameIn(shown.clip, exactFrameOf(shown), playing.closing);
    player.show(shown.clip, shownFrame.value, shown.facing, {
        posture: drawn,
        eyes: look.eyes,
        stride,
        sky: shown.clip.name === "watch" ? sky : null,
        at: lookingAt(),
    });
    headAt.value = player.headAt();
    keepParcels(shown);
    frameTimer = requestAnimationFrame(step);
}

// the picture's left and top for a figure on a spot in `posture`
const placed = (spot, posture) => {
    const box = boxAt(spot, figureSize(), posture);
    return {x: box.left, y: box.top};
};
// The picture kept where the figure rests, in the posture of the clip on screen; when that posture changes where it rests, as it sits down
// or gets up, the picture slides to its new place while the body eases into the posture, stepped each frame (slideOn)
const rest = () => {
    // a figure arriving at a hang keeps the picture its hop ended in, already hanging, until its hands take the grip
    if (body.place.posture === "hang" && drawn !== "hang") return;
    const to = placed(body.place, drawn);
    if (drawn !== body.rested) slide();
    body.rested = drawn;
    if (body.slide) body.slide = {...body.slide, to};
    else body.at = to;
};

// the picture's next move eases over the time a change of posture takes, from where it is now
function slide() {
    body.slide = {from: {...body.at}, to: {...body.at}, began: performance.now()};
}

// those waiting for the slide under way to end, as a trip does before it sets off
const slideWaits = [];
function endSlide() {
    body.slide = null;
    slideWaits.splice(0).forEach((done) => done());
}

function slideOn() {
    const {at, done} = slideAt(body.slide, performance.now(), CHANGE_SECONDS * 1000);
    body.at = at;
    if (done) endSlide();
}

// the trip to a spot, from where the figure is in the posture it travels in to that spot in the one it travels in there (places.js); the
// clip on screen is drawn in that posture first, so the figure gets to its feet or takes its grip where it is before the first leg
async function moveTo(spot, {straight = false, pace = 1} = {}) {
    if (!tripTo(body.place, spot, figureSize(), {straight, pace})) return restOn(spot);
    body.trip = {to: spot, straight, pace, footing: footingOn(spot)};
    // read back, since the ref hands out its reactive copy, never the object it was given
    const trip = body.trip;
    step();
    if (body.slide) await new Promise((done) => slideWaits.push(done));
    if (body.trip === trip) setOff();
}

// Until it sets off the figure keeps to its ground, so the trip's legs are drawn then, from where it is now to where the spot is now
function setOff() {
    const {to, straight, pace, footing: held} = body.trip;
    const there = landingOn(to, held, figureSize());
    const trip = tripTo(body.place, there, figureSize(), {straight, pace});
    body.way = Math.sign(there.x - body.place.x);
    stopSwinging();
    if (trip) {
        body.trip = {...body.trip, ...trip};
        return nextLeg();
    }
    body.footing = null;
    body.trip = null;
    settle(there, held);
    step();
}

// the trip waits for its next leg to set off (depart), or ends at its spot when no leg is left
function nextLeg() {
    const legs = body.trip.legs;
    const next = legs.find((each) => each.ms > 0);
    if (!next) {
        const {to, footing: held} = body.trip;
        const landed = landingOn(to, held, figureSize());
        body.trip = null;
        if (Math.hypot(landed.x - to.x, landed.y - to.y) >= 1) slide();
        settle(landed, held);
        return step();
    }
    const left = legs.slice(legs.indexOf(next));
    body.trip = {...body.trip, started: true, moves: false, hopping: Boolean(next.hopping), clip: next.clip, legs: left};
    step();
}

// the next leg carries the picture to its end, stepped each frame (watchFooting) until it has run its course (endLeg)
function depart() {
    const [next, ...legs] = body.trip.legs;
    // the first walk of a trip sets off on its feet from the line the figure rests on: from a seat the picture first eases up onto them
    // (slideOn), and the walk sets off once it is there; every later leg sets off where the one before it ended
    const from = next.hopping || body.trip.departed ? {...body.at} : placed(body.place, POSTURES[body.place.posture].travels);
    if (Math.hypot(from.x - body.at.x, from.y - body.at.y) > 1) {
        if (body.trip.rising) return;
        body.trip = {...body.trip, rising: true};
        const rising = body.trip;
        body.slide = {from: {...body.at}, to: from, began: performance.now()};
        return void slideWaits.push(() => body.trip === rising && depart());
    }
    body.trip = {...body.trip, moves: true, departed: true, legs};
    body.footing = null;
    const feet = feetOf(from);
    body.walk = {
        from,
        began: performance.now(),
        on: next.hopping ? null : (floorAt(latestFloors().floors, feet.x, feet.y, KEPT_WITHIN)?.id ?? null),
    };
    body.leg = next;
}

// a leg that has run its course hands on to the next, landing the figure when it hopped
function endLeg() {
    if (body.trip.hopping) body.landing = Boolean(body.trip.lands);
    nextLeg();
}

// a look that finds the figure already at its spot keeps the footing it stands by on that floor, so a look never re-anchors a resting figure
function restOn(spot) {
    const held = footingOn(spot);
    if (held && body.footing && held.id === body.footing.id) return;
    settle(spot, held);
}

function settle(spot, held = footingOn(spot)) {
    body.place = spot;
    body.footing = held;
    covering = hiddenAt(spot, figureSize());
}

// Each frame the figure keeps to what it rests on as that moves (figure/floors.js groundUnder), falling with the bars under it or lifted by them;
// when the ground went from under it, it goes at once, without waiting for its clip, as gravity does not, straight up or down to the
// ground at home and on to its place there
function watchFooting() {
    if (body.slide && !body.trip?.moves && !body.airborne) slideOn();
    if (body.airborne) return fallOn();
    if (body.trip?.moves) {
        if (body.trip.hopping) hopOn();
        else walkOn();
        if (body.trip?.moves && legEnded(body.leg, body.walk.began, performance.now())) endLeg();
        return;
    }
    if (!body.footing) return;
    sway();
    const ground = groundUnder(body.footing, body.place, figureSize());
    if (!ground) return uprooted();
    body.footing = ground.footing;
    if (ground.motion === "dropping") return fallFrom(body.place, null);
    const spot = ground.spot;
    if (Math.hypot(spot.x - body.place.x, spot.y - body.place.y) <= 0.3) return;
    if (ground.motion === "launched" && !body.arriving) groundMoved("launched");
    if (body.trip) body.trip = {...body.trip, legs: liftedLegs(body.trip.legs, spot.x - body.place.x, spot.y - body.place.y)};
    body.place = spot;
    rest();
}

// whether the user asks for motion to be kept still: then a fall or a hop stepped in code is where it ends at once
const keptStill = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const feetOf = (picture) => ({x: picture.x + SIZE / 2, y: picture.y + (1 - below.value) * SIZE});

// A walk is stepped here, frame by frame, against the floors the floors loop read (figure/floors.js): the walker keeps to its floor as
// it rises, and falls from where it is the moment its floor drops away or goes, then lands and sets off again for where it was going
function walkOn() {
    const feet = feetOf(legAt(body.leg, body.walk.from, performance.now() - body.walk.began));
    const under = underWalker(latestFloors().floors, body.walk.on, feet.x, feet.y);
    if (under.falls) return fallFrom({...feet, posture: "stand"}, body.trip.to);
    if (Math.abs(under.dx) > 0.3 || Math.abs(under.dy) > 0.3) carryWalk(under.dx, under.dy);
    body.at = legAt(body.leg, body.walk.from, performance.now() - body.walk.began);
}

function carryWalk(dx, dy) {
    const [from, leg] = liftedLegs([body.walk.from, body.leg], dx, dy);
    body.walk = {...body.walk, from};
    body.leg = leg;
    body.trip = {...body.trip, legs: liftedLegs(body.trip.legs, dx, dy)};
}

// The figure falls from the line it rests on at `spot`, in its posture there, never from below the ground at home, and goes on to `to`
// once it lands
function fallFrom(spot, to) {
    endSlide();
    body.airborne = fallingFrom(spot, to, latestFloors().floors, performance.now(), Math.random);
    body.trip = null;
    body.footing = null;
    body.at = placed(body.airborne, body.airborne.posture);
    step();
}

function fallOn() {
    const {airborne, landed} = airborneFrame(body.airborne, latestFloors().floors, performance.now(), fall.value, SIZE, keptStill());
    body.at = placed(airborne ?? landed.spot, (airborne ?? landed.spot).posture);
    body.airborne = airborne;
    if (!landed) return;
    body.landing = landed.standing;
    groundMoved("dropping");
    settle(landed.spot);
    rest();
    step();
    if (landed.to) moveTo(landed.to);
}

// A hop is stepped here, frame by frame, toward the ground it is headed for as that moves (aimedAt), so it lands where the ground is now
// rather than where it was; and once that ground has gone it falls from where it is in the air
function hopOn() {
    const trip = body.trip;
    if (trip.footing && !footingNow(trip.footing, figureSize())) return fallFrom({...feetOf(body.at), posture: "stand"}, null);
    const landed = trip.footing ? landingOn(trip.to, trip.footing, figureSize()) : trip.to;
    const aimed = aimedAt(trip, body.leg, body.walk.from, landed);
    if (aimed.trip !== trip) {
        body.trip = aimed.trip;
        body.leg = aimed.leg;
        body.walk = {...body.walk, from: aimed.from};
    }
    body.at = legAt(body.leg, body.walk.from, performance.now() - body.walk.began, keptStill());
}

// The figure landed or was launched, and its body squashes and bounces as the flat figure's did (falls.css) until that animation ends
// (domain/falls.js FALLS)
const moved = ref("");
const fall = computed(() => fallOf(voice.value));
const groundMoved = (motion) => (moved.value = motion);
const squashed = (event) => event.target === event.currentTarget && (moved.value = "");

// The figure hanging by a hand swings about it (pendulum.js): out the way its trip went as it lands, and with the hand as the ground under
// it carries it sideways
const tilt = ref(0);
let swing = STILL;
let swungAt = 0;
let swungFrom = null;
function sway() {
    if (body.place.posture !== "hang" || body.trip) return stopSwinging();
    const time = performance.now() / 1000;
    swing = swungFrom === null ? landedSwing(body.way) : swung(swing, time - swungAt, time, body.place.x - swungFrom, SIZE);
    swungAt = time;
    swungFrom = body.place.x;
    tilt.value = swing.angle;
}

function stopSwinging() {
    swing = STILL;
    swungFrom = null;
    tilt.value = 0;
}

// where the hand it hangs by is in its picture, which the swing turns about
const grip = computed(() => {
    const name = shownClip.value?.name ?? "";
    return /^hang_[lr]$/.test(name) ? gripIn(name.slice(-1), shownFacing.value, below.value) : null;
});

// The floor under a resting figure went, so it falls from where it is and, once it lands, goes on to a stay at home
function uprooted() {
    stay = stayAtHome(stay);
    playing = {name: "", started: 0, shown: null, index: 0, closing: null};
    beats.value = [];
    body.landing = false;
    const spot = stayingAt(stay, figureSize(), body.place);
    const clear = {state: held.value.state, now: Date.now() / 1000, near: body.place, figure: figureSize(), cleared};
    fallFrom({...feetOf(body.at), posture: "stand"}, keptClear(spot, clear));
}

// the scene the reactions are decided in
const scene = () => ({
    voice: voice.value,
    moving: Boolean(body.trip),
    place: body.place,
    beats: beats.value.length,
    arriving: body.arriving,
    leaving: body.leaving,
});

function look() {
    clearTimeout(lookTimer);
    now.value = Date.now() / 1000;
    waitingSince.value = waitingSinceAt(counts.value, waitingSince.value, now.value);
    const happened = [
        ...beatsAfter(lead.value, seenAt),
        ...cardsAfter(lead.value, knownCards),
        ...testResultsAfter(lead.value, testStates),
        ...facesAfter(rows("reactions"), seenAt),
    ];
    if (happened.length) seenAt = Math.max(seenAt, ...happened.map((fire) => fire.time));
    if (committed(happened)) sendUfo();
    const stroll = walkingMoment(body.trip, walkBegan, now.value);
    walkBegan = stroll.began;
    if (stroll.moment && !beats.value.some((beat) => beat.clip === "stumble")) react(stroll.moment);
    const work = workMoments(held.value.state, typed, workBegan, now.value);
    typed = false;
    workBegan = work.began;
    [...happened, ...work.moments].forEach(react);
    const waited = {state: held.value.state, since: held.value.since, lasted: now.value - held.value.since};
    const egg = answerTo(waited, voice.value, memory, now.value, Math.random, hasClip)?.beat;
    const pastime = pastimeFor(scene(), waited, pastimesDue, now.value, Math.random, drawnHere);
    const after = [egg, pastime].filter(Boolean);
    if (after.length) beats.value = [...beats.value, ...after];
    if (coveredSince() && !body.airborne && !body.place.stays) stepOutOf(boxAt(body.place, figureSize(), drawn));
    const target = targetFor({
        state: held.value.state,
        counts: counts.value,
        stay,
        now: now.value,
        near: body.place,
        figure: figureSize(),
        hands,
        cleared,
        work: workOf(),
    });
    stay = target.stay;
    // while the UFO is here the figure stands watching it, and goes nowhere
    if (!body.trip && !body.arriving && !body.airborne && !ufo.value) {
        moveTo(target.spot, {pace: hurried ? SPRINT : 1});
        hurried = false;
    }
    if (!document.hidden) lookTimer = setTimeout(look, LOOK_EVERY);
}

// what the figure hid where it came to rest, so something that appears under it since, as a new message, is told apart from what it
// could not help covering there
let covering = 0;
// the figure sprints on its next trip, out of the way
let hurried = false;

// The figure steps out of the way of what is under `box`, its picture, and sprints there, as when it is clicked or a new message appears
// under it (perches.js stepAside)
function stepOutOf(box) {
    ({stay, cleared} = stepAside(stay, box, Date.now() / 1000));
    hurried = true;
}

// whether something has appeared under the figure since it came to rest, as a new message under its feet
const coveredSince = () => !body.trip && body.footing && hiddenAt(body.place, figureSize()) > covering;

function clicked(event) {
    stepOutOf(event.currentTarget.parentElement.getBoundingClientRect());
    look();
}

// the part of the picture the body is drawn in above the line it rests on, which takes the click
const bodyStyle = computed(() => {
    const clickable = clickedBody(body.place.posture, below.value);
    return {
        left: `${clickable.left * 100}%`,
        width: `${(clickable.right - clickable.left) * 100}%`,
        top: `${clickable.top * 100}%`,
        height: `${(clickable.bottom - clickable.top) * 100}%`,
        // where it builds the figure stands over the bars docked above the compose box, and lets every click through to them
        ...(body.place.stays && {pointerEvents: "none"}),
    };
});

// where the figure's feet are now, and a parcel's middle and the pile's places, on the page
const feetX = () => body.at.x + SIZE / 2;
const parcelX = (parcel) => composeEdge().edge.left + parcel.along;
const piled = () => parcels.value.filter((each) => each.state === "piled").length;
const slotX = (index) => {
    const {edge} = composeEdge();
    return edge.left + edge.width + pileSlot(index).left;
};

// Where the figure goes to work on the parcels (perches.js targetFor): round behind a parcel it built and on along to the pile with it,
// beside the parcel it builds, or for a new one, a place whose parcel stands clear of the pile
function workOf() {
    const pushing = parcels.value.find((each) => each.state === "built");
    if (pushing) return {x: pushStand(parcelX(pushing), slotX(piled()), body.place.x)};
    const building = parcels.value.find((each) => each.state === "building");
    if (building) return {x: parcelX(building) - beside};
    return {beside, before: slotX(piled() + PILE.high) - PARCEL.width / 2};
}

// Each frame: a parcel pops in the first frame the figure hammers where it builds, where its blows land, kept inside the compose box's
// top; it is built once the figure has stopped hammering and its agent runs no command; a built one is pushed along in front of the
// figure as it walks behind it, and once it meets the pile it is piled, hopping up onto it. They stay on that floor as the box moves.
function keepParcels(shown) {
    const {edge} = composeEdge();
    const list = parcels.value;
    const hammers = shown.clip.name === "work" && drawn === "stand" && body.place.stays && !body.trip;
    if (hammers && !list.some((each) => each.state !== "piled")) {
        const along = Math.min(Math.max(feetX() + beside - edge.left, PARCEL.inside), edge.width - PARCEL.inside);
        parcels.value = [...list, {id: ++made, along, up: 0, state: "building", until: performance.now() + hammerMs(Math.random), blows: 0}];
    }
    const building = parcels.value.find((each) => each.state === "building");
    if (building && hammers) countBlows(building, shown);
    if (building && performance.now() >= building.until && !ufo.value) building.state = "built";
    const pushing = list.find((each) => each.state === "built");
    if (pushing && !ufo.value) {
        const to = slotX(piled());
        if (body.trip?.moves) pushing.along = pushedTo(parcelX(pushing), feetX(), to, body.way) - edge.left;
        if (Math.abs(parcelX(pushing) - to) < PUSH.room) Object.assign(pushing, {along: to - edge.left, state: "piled", up: pileSlot(piled()).up});
    }
    if (!ufo.value) drawnParcels.value = parcels.value.map((each) => ({id: each.id, x: parcelX(each), y: edge.top, up: each.up, scale: 1, opacity: 1, blows: each.blows}));
}

// each blow that lands on the parcel being built is counted on it, so the parcel puffs dust at it (CodeParcel.vue)
function countBlows(building, shown) {
    if (counted.started !== playing.started) counted = {started: playing.started, landed: 0};
    const landed = blowsLanded(exactFrameOf(shown), blow.frames, blow.lands);
    building.blows += Math.max(landed - counted.landed, 0);
    counted.landed = landed;
}

// the work is committed: the UFO comes for every parcel that is built, on the pile or not
const committed = (happened) => happened.some((fire) => fire.beat === "committed");

function sendUfo() {
    const taken = parcels.value.filter((each) => each.state !== "building");
    if (ufo.value || !taken.length) return;
    if (keptStill()) {
        parcels.value = parcels.value.filter((each) => !taken.includes(each));
        return;
    }
    const world = worldBox();
    const stops = stopsOf(taken.map((each) => ({id: each.id, x: parcelX(each)})));
    ufo.value = {
        began: performance.now(),
        stops,
        from: {x: world.right + UFO_OFF.right, y: world.top + UFO_OFF.above},
        away: {x: world.left - UFO_OFF.left, y: world.top + UFO_OFF.above},
    };
}

// Each frame of the UFO's flight (parcels.js ufoAt): where it and its beam are drawn, the parcels of the stop it is at rising up the beam
// to its middle, shrinking, those of the stops it has made gone, and what the figure watches: the UFO, with a hand shading its eyes while
// it is still coming in, and stepped back once it first lifts; once it is gone the figure steps forward again over as long as it took to
// step back
function flyUfo() {
    if (!ufo.value) return stepForward();
    const {edge} = composeEdge();
    const ms = performance.now() - ufo.value.began;
    const at = ufoAt(ufo.value.stops, ms, edge.top, ufo.value.from, ufo.value.away);
    const gone = new Set(ufo.value.stops.slice(0, at.taken).flatMap((stop) => stop.ids));
    const rising = new Set(ufo.value.stops[at.stop].ids);
    const lifted = (each) => {
        const k = rising.has(each.id) ? at.risen : 0;
        const x = parcelX(each);
        const y = edge.top + (at.y + PARCEL.height / 2 + each.up - edge.top) * k;
        return {id: each.id, x: x + (at.x - x) * k, y, up: each.up, scale: 1 - 0.65 * k, opacity: k > 0.85 ? (1 - k) / 0.15 : 1};
    };
    drawnParcels.value = parcels.value.filter((each) => !gone.has(each.id)).map(lifted);
    saucer.value = {x: at.x, y: at.y, beam: at.beam, width: at.width, reach: Math.max(edge.top - at.y, 0)};
    const lifting = ms - UFO.enter - UFO.beamOn;
    sky = {
        shade: at.coming ? Math.min(ms / STEP_BACK_MS, 1 - ms / UFO.enter) : 0,
        back: Math.min(Math.max(lifting / STEP_BACK_MS, 0), 1),
    };
    if (!at.gone) return;
    parcels.value = parcels.value.filter((each) => !ufo.value.stops.some((stop) => stop.ids.includes(each.id)));
    ufo.value = null;
    saucer.value = null;
    sky = {shade: 0, back: sky.back, at: performance.now()};
}

function stepForward() {
    if (!sky) return;
    const now = performance.now();
    const back = Math.max(sky.back - (now - sky.at) / STEP_BACK_MS, 0);
    sky = back ? {shade: 0, back, at: now} : null;
}

// What the figure looks at on the page: the UFO while it flies, else, standing on the bars docked over the compose box, the leading edge
// of a progress bar on them while it runs, so its head follows the edge as it moves; null when there is nothing to look at
function lookedAt() {
    const docks = groundEdge();
    return saucer.value ?? (docks.docked && body.footing?.home && !body.trip ? progressEdge(docks.element) : null);
}

// The look eases in over LOOK_EASE_MS once there is something to look at, and back out over as long from the last place looked at once
// there is not, as the UFO goes or the bar ends, so the head never snaps; `amount` is how far into it the figure is, 0 to 1
const LOOK_EASE_MS = 500;
const gaze = {point: null, amount: 0, at: 0};

// where in its picture the figure looks this frame, and how far into the look (figure.js lookToward), or null to look as its clip does
function lookingAt() {
    const now = performance.now();
    const point = lookedAt();
    const step = (now - (gaze.at || now)) / LOOK_EASE_MS;
    gaze.at = now;
    gaze.amount = Math.min(Math.max(gaze.amount + (point ? step : -step), 0), 1);
    if (point) gaze.point = point;
    if (!gaze.amount || !gaze.point) return null;
    const eased = gaze.amount * gaze.amount * (3 - 2 * gaze.amount);
    return {x: (gaze.point.x - body.at.x) / SIZE, y: (gaze.point.y - body.at.y) / SIZE, amount: eased};
}

const onType = (event) => {
    if (event.target.closest?.(HOME)) typed = true;
};

// what the figure does about a moment, as reactions.js answerTo decides: a beat the body plays, or a look the eyes take on
function react(moment) {
    const answer = answerTo(moment, voice.value, memory, now.value, Math.random, hasClip);
    if (answer?.beat) beats.value = moment.beat === "long_walk" ? [answer.beat, ...beats.value] : [...beats.value, answer.beat];
    if (!answer?.look) return;
    looking = lookOf(answer.look, performance.now() / 1000);
    stay = stayForLook(stay, body.place);
}

// the figure appears at home on its feet, where its entrance plays, keeping to that ground from the start, so a compose box that mounts
// after it, as on coming back to Home, carries it up from the floor rather than leaving it there
let homeFrame = 0;

// The figure takes its place at home, on the chat's compose box or the bars docked over it, waiting for the chat to be drawn, as on coming
// back to Home the page can be drawn a frame or more before it.
function home() {
    cancelAnimationFrame(homeFrame);
    if (!document.querySelector(HOME)) {
        homeFrame = requestAnimationFrame(home);
        return;
    }
    settle(spotOf(null, figureSize()));
    rest();
}

// the environment's agent arriving or going: the figure enters, or makes its exit and is gone
function present(live) {
    if (!player || live === body.here) return;
    if (live) {
        body.here = true;
        home();
    }
    body.leaving = !live;
    body.arriving = live;
    step();
}

const seen = () => {
    if (document.hidden) return;
    look();
    step();
};

async function load(name) {
    player = null;
    if (!name) return;
    try {
        const [loaded, module] = await Promise.all([loadVoiceFigure(name), import("../figure/figure.js")]);
        if (name !== voice.value || !canvas.value) return;
        const {FigurePlayer} = await import("../figure/player.js");
        clips = module.CLIPS.filter((clip) => !clip.voices || clip.voices.includes(name));
        hands = [...loaded.stance.free];
        beside = module.blowsLandAt(loaded.stance) * SIZE;
        blow = {frames: module.WORK.blowFrames, lands: module.WORK.lands};
        testResultsAfter(lead.value, testStates);
        cardsAfter(lead.value, knownCards);
        below.value = module.GROUND;
        canvas.value.width = canvas.value.height = Math.round(SIZE * (window.devicePixelRatio || 1));
        player = new FigurePlayer(loaded, canvas.value);
        home();
        body.here = belongs.value;
        body.arriving = body.here;
        figureStatus.value = "shown";
        startBody();
        look();
        step();
    } catch (error) {
        console.error(error);
        figureStatus.value = "failed";
    }
}

watch(voice, load);
watch(belongs, present);
onMounted(() => {
    document.addEventListener("visibilitychange", seen);
    document.addEventListener("input", onType, true);
    window.addEventListener("resize", look);
    load(voice.value);
});
onUnmounted(() => {
    stopBody();
    cancelAnimationFrame(homeFrame);
    cancelAnimationFrame(frameTimer);
    clearTimeout(lookTimer);
    document.removeEventListener("visibilitychange", seen);
    document.removeEventListener("input", onType, true);
    window.removeEventListener("resize", look);
});

// the mark the clip on screen draws drifting up from the head in this frame (figure.js CLIPS marks), or ""
const mark = computed(() => {
    const marks = shownClip.value?.marks;
    return marks?.frames.some(([from, to]) => shownFrame.value >= from && shownFrame.value < to) ? marks.mark : "";
});
const markStyle = computed(() => ({
    left: `${headAt.value.x * 100}%`,
    top: `${(headAt.value.y - MARK_HEAD_OFFSET) * 100}%`,
    "--mark-seconds": `${MARK_DRIFT_SECONDS}s`,
}));

const chasing = computed(() => shownClip.value?.name === "squire_chase");
// during an entrance or exit what is below the edge the figure stands on is hidden, as the box it climbs over or drops past would hide it
const passing = computed(() => ["enter", "exit"].includes(shownClip.value?.name));
const chaseMs = computed(() => (chasing.value ? (shownClip.value.frames / shownClip.value.fps) * 1000 : 0));
// the most the squire runs out after the bug, and how far it may run now, along the floor it stands on
const CHASE_MOST = 160;
const chaseRun = ref(0);
watch(chasing, (now) => {
    if (!now) return;
    const {floors, world} = latestFloors();
    chaseRun.value = world ? chaseRoom(floors, world, feetOf(body.at), boxAt(body.place, figureSize(), drawn), CHASE_MOST) : 0;
});

// how the picture moves with the bars under it, as the flat figure's did: down over the voice's fall, falling faster as it goes, or up
// quickly, easing out
// the body squashes and bounces as the flat figure's did when the bars under it move, `moved` naming which way
const actorStyle = computed(() => ({
    "--size": `${SIZE}px`,
    "--fall-ms": `${fall.value.ms}ms`,
    "--squash": fall.value.squash,
    "--bounce": `${fall.value.bounce}px`,
    ...(chasing.value && {animationDuration: `${chaseMs.value}ms`, "--chase": `${chaseRun.value}px`}),
    ...(grip.value && {rotate: `${tilt.value}rad`, transformOrigin: `${grip.value.x * 100}% ${grip.value.y * 100}%`}),
}));

const style = computed(() => ({
    width: `${SIZE}px`,
    height: `${SIZE}px`,
    transform: `translate(${body.at.x}px, ${body.at.y}px)`,
}));
</script>

<template>
    <div
        v-show="figureVisible(body.here)"
        class="voice-figure"
        :style="style"
        aria-hidden="true"
        :data-walking="walking"
        :data-hopping="Boolean(body.trip?.moves && body.trip.hopping)"
        :data-trip="body.trip ? (body.trip.started ? 'walking' : 'waiting to set off') : body.arriving ? 'arriving' : ''"
        :data-clip="shownClip?.name"
    >
        <div class="voice-figure-body" :style="bodyStyle" @mousedown.prevent @click="clicked" />
        <div :class="['voice-figure-actor', moved, {chasing}]" :style="actorStyle" @animationend="squashed">
            <canvas ref="canvas" class="voice-figure-canvas" :style="passing ? {clipPath: `inset(0 0 ${below * 100}% 0)`} : null" />
            <template v-if="mark">
                <span class="voice-figure-marks" :style="markStyle">
                    <template v-for="index in MARK_COUNT" :key="index">
                        <span :style="{animationDelay: `${(-(index - 1) * MARK_DRIFT_SECONDS) / MARK_COUNT}s`}">{{ mark }}</span>
                    </template>
                </span>
            </template>
            <template v-if="chasing">
                <svg class="voice-figure-bug" :style="{animationDuration: `${chaseMs}ms`}" viewBox="0 0 16 12" width="16" height="12">
                    <path d="M3 3 1 1M3 6H0M3 9 1 11M13 3l2-2M13 6h3M13 9l2 2" stroke="currentColor" stroke-width="1.2" />
                    <ellipse cx="8" cy="6" rx="5" ry="4" fill="currentColor" />
                </svg>
            </template>
        </div>
    </div>
    <template v-for="drawing in drawnParcels" :key="drawing.id">
        <CodeParcel :x="drawing.x" :y="drawing.y" :up="drawing.up" :scale="drawing.scale" :opacity="drawing.opacity" :blows="drawing.blows ?? 0" />
    </template>
    <template v-if="saucer">
        <FlyingSaucer :x="saucer.x" :y="saucer.y" :beam="saucer.beam" :reach="saucer.reach" :width="saucer.width" />
    </template>
</template>

<style scoped>
.voice-figure-marks {
    position: absolute;
    color: var(--text);
    pointer-events: none;
    font-family: inherit;
    font-size: 10px;
    font-weight: 600;
    line-height: 1;
}

.voice-figure-marks > span {
    position: absolute;
    opacity: 0;
    animation: voice-figure-marks var(--mark-seconds) linear infinite;
}

@keyframes voice-figure-marks {
    0% {
        transform: translate(0, 0) scale(0.65);
        opacity: 0;
    }
    20% {
        opacity: 0.65;
    }
    100% {
        transform: translate(14px, -28px) scale(1);
        opacity: 0;
    }
}

@media (prefers-reduced-motion: reduce) {
    .voice-figure-marks > span {
        animation: none;
    }
    .voice-figure-marks > span:first-child {
        opacity: 0.5;
    }
}

.voice-figure {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 40;
    pointer-events: none;
}

.voice-figure-body {
    position: absolute;
    z-index: 1;
    pointer-events: auto;
    cursor: pointer;
}

/* one thin edge in the page's own text colour, so the figure reads on a dark page and a light one alike; a wider
   second shadow reads as a halo around it rather than an edge on it */
.voice-figure-canvas {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
}

.voice-figure-actor {
    width: 100%;
    height: 100%;
    transform-origin: 50% 100%;
}

.voice-figure-actor.dropping {
    animation: figure-land calc(var(--fall-ms) * 0.9) ease-out both;
}

.voice-figure-actor.launched {
    animation: figure-launch calc(var(--fall-ms) * 2) both;
}

@media (prefers-reduced-motion: reduce) {
    .voice-figure-actor.dropping,
    .voice-figure-actor.launched {
        animation: none;
    }

    .voice-figure-actor {
        rotate: none !important;
    }
}

/* the squire runs out across the pane after the bug and comes back */
.voice-figure-actor.chasing {
    animation-name: voice-figure-chase;
    animation-timing-function: ease-in-out;
}

@keyframes voice-figure-chase {
    0%,
    100% {
        transform: none;
    }

    50% {
        transform: translateX(var(--chase));
    }
}

/* the bug runs off ahead of the squire and gets away while he turns back */
.voice-figure-bug {
    position: absolute;
    bottom: 8%;
    left: 60%;
    color: var(--text);
    animation-name: voice-figure-bug;
    animation-timing-function: linear;
    animation-fill-mode: forwards;
}

@keyframes voice-figure-bug {
    0% {
        transform: translateX(0);
        opacity: 1;
    }

    45% {
        transform: translateX(120%) translateX(60px);
        opacity: 1;
    }

    60% {
        transform: translateX(120%) translateX(90px);
        opacity: 0;
    }

    100% {
        transform: translateX(120%) translateX(90px);
        opacity: 0;
    }
}
</style>
