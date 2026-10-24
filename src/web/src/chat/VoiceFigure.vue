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
    chuteFrom,
    fallingFrom,
    floorAt,
    goneUp,
    launchFrom,
    legAt,
    legEnded,
    liftedLegs,
    slideAt,
    underWalker,
} from "../domain/figureMotion.js";
import {footingNow, footingOn, groundUnder, keptOnFloor, landingOn, latestFloors, readFloors} from "../figure/floors.js";
import {useFigureBody} from "../composables/figureBody.js";
import {
    beatsAfter,
    cardsAfter,
    canSwitch,
    clipFor,
    clipOf,
    modeOf,
    closeAt,
    goesOnFacing,
    facesAfter,
    figureStateOf,
    frameIn,
    processEndsAfter,
    readingsAfter,
    sayingsAfter,
    writtenFacesAfter,
    testResultsAfter,
    waitingSinceAt,
    withSystemCards,
    callLines,
    stretchedFrame,
} from "../domain/figureState.js";
import {loadVoiceFigure} from "../figure/assets.js";
import {MARK_STAY, bubbleNear, builds, climbOf, climbs, discoBall, eagerSpot, keptClear, ladderShown, markSpot, nearerWay, mayLeave, perchedAfter, stayAtHome, stepAside, stayForLook, stayingAt, targetFor, wayUp} from "../figure/perches.js";
import StepLadder from "./StepLadder.vue";
import {SKYWARD, goneMs, skywardAt, skywardHops} from "../figure/skyward.js";
import {jumpMost} from "../figure/climbs.js";
import {BLINK, blinkOpenness, nextBlinkMs} from "../figure/blink.js";
import {IDLE_CLIPS, LAYER, PARCEL, PILE, PUSH, UFO, answeredWith, beamOf, behind, blowsLanded, boxGapSeconds, boxRisen, boxSway, boxTop, buildAim, buildRunAt, isPileLeft, grabberAt, grabsOf, hammering, inspecting, LIGHT_KINDS, litAfter, phasesOf, pileSlot, pushStand, pushedTo, pushWaits, stopsOf, ufoAt, unitsAfter, workLook} from "../figure/parcels.js";
import CodeParcel from "./CodeParcel.vue";
import FigureAct from "./FigureAct.vue";
import {KeptTimes} from "../figure/keptTimes.js";
import {environment} from "../state/environment.js";
import ComicBubble from "./ComicBubble.vue";
import {bubbleSize, phrasesOf, phrasesSeconds} from "../figure/comicBubble.js";
import ClawCrane from "./ClawCrane.vue";
import FlyingSaucer from "./FlyingSaucer.vue";
import {FRESH_SECONDS, READING, answerTo, barWatchAt, watchesBar, carrierOf, headBeat, heldCall, joinedCall, uncut, craneFrom, eagerFor, eyesAt, faces, freshBeats, gazeAfter, lookOf, isListening, pastimeFor, playedFrom, queuedFirst, queues, readingAt, readingFacing, roomFor, spellFor, stillGoing, spellIn, variantOf, walkingMoment, workMoments} from "../figure/reactions.js";
import {ACTS, hidesBelowFloor, squeezeOf, swingAngle, throwsFor} from "../figure/acts.js";
import {VISOR, discoScreen, lightOnce, visorAt, visorFor} from "../figure/visor.js";
import {NOT_ADMIRING, admiringAfter} from "../figure/admire.js";
import {UNTICKLED, movedTo, nearBody, tickling} from "../figure/tickle.js";
import {UPRIGHT, tiltAfter, tiltAt} from "../figure/headTilt.js";
import {SEQUENCES, alive, givesWay, sequenceIn} from "../figure/pile.js";
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
    bubbleSpot,
    middleOf,
    picturesNear,
    handsetSide,
    tailEnd,
    callSays,
    callStretch,
    wordsUnder,
    watchLook,
    progressOf,
    hiddenAt,
    nearestTell,
    USER_TURN,
    roomToStepAside,
    spotOf,
    SEATED,
    seatedFacing,
    tripTo,
    turnStep,
} from "../figure/places.js";
import {STILL, landedSwing, swung} from "../figure/pendulum.js";
import "../figure/falls.css";
import {holding, rows} from "../sync/rows.js";
import {store} from "../state/store.js";

// The figure plays what the figure modules decide: what it does in figureState.js and reactions.js, where it goes in perches.js, and how
// it stands and travels in places.js. This component holds only the drawing and the clock.

// The figure is this many pixels square, as the chat's flat figure is
const SIZE = 112;
// how far the UFO comes in from beyond its world's right and goes off beyond its left, and how high above the world's top, in pixels
const UFO_OFF = {right: 40, left: 60, above: -30};
// how long the figure takes to step back once the UFO starts lifting, in milliseconds
const STEP_BACK_MS = 400;

// The figure blinks every so often, a random few seconds apart, drawn at the screen's own frame rate (figure/blink.js), whatever rate the
// clip on screen runs at: `next` is when the next blink begins on the page's clock
const blinking = {next: 0};

// how open the eyes are this frame, 1 between blinks
function blinked() {
    const now = performance.now();
    if (!blinking.next) blinking.next = now + nextBlinkMs(Math.random);
    const open = blinkOpenness(now - blinking.next);
    if (now >= blinking.next + BLINK.close + BLINK.open) blinking.next = now + nextBlinkMs(Math.random);
    return open;
}
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
// the picture in a message near it that the figure admires now and then (figure/admire.js)
let admiring = NOT_ADMIRING;
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
// and the state each test run's card had when last looked at; the times kept in the browser's storage for the environment, so every
// cooldown holds through a reload (figure/keptTimes.js)
const memory = {reacted: new KeptTimes(`journal.figure.cooldowns.${environment.value}`, Date.now() / 1000), played: [], tally: {plain: 0, last: ""}};
const pastimesDue = new KeptTimes(`journal.figure.pastimes.${environment.value}`, Date.now() / 1000);
const testStates = new Map();
// whether each process card was running when last looked at, and the glow a card's end lit on the visor (figure/visor.js), or null
const processStates = new Map();
let visor = null;
// the soft glow about the lit visor this frame, its colour and strength, or null
const halo = ref(null);
// the pictures of a parcel's block for each kind of its lights (parcels.js LIGHT_KINDS), one for each step of their blink, drawn by the
// figure's own renderer; each parcel shows the kind its own run lit (parcels.js litAfter)
const blocks = ref(null);
// the UFO's saucer drawn in 3D as the figure is, its pictures one for each step of its rim lights' blink (figure.js Stage.drawSaucer)
const saucerPicture = ref(null);
// the parachute's canopy drawn in 3D as the figure is, and where its lines leave its rim (figure.js Stage.drawCanopy)
const canopyPicture = ref(null);
// a fixed run's bug drawn in 3D as the figure is, a picture for each step of its stride (figure.js Stage.drawBug)
const bugPicture = ref(null);
const knownCards = new Set();
let seenAt = Date.now() / 1000;
// when the figure began to watch: a run that began before it is never taken for one that has just ended
const watchedSince = seenAt;
let playing = {name: "", started: 0, shown: null, index: 0, closing: null};
// whether the beat on screen is broken off at the next step, as one shown during a state that is over, or one a first beat interrupts
let cutting = false;
// the clip on screen, so the page can draw what the rig has no bones for, such as the bug the squire chases
const shownClip = ref(null);
const shownFacing = ref(0);
// the posture the clip on screen is drawn in
let drawn = "stand";
// whether the legs on screen walk, as the page marks it for whoever measures the figure, beside the name of the clip on screen
const walking = ref(false);

// whether the figure hops on the leg it is on, and how far along a trip it is, as the page marks them for whoever measures the figure
const hopping = computed(() => Boolean(body.trip?.moves && body.trip.hopping));
const tripStage = computed(() => (body.trip ? (body.trip.started ? "walking" : "waiting to set off") : body.arriving ? "arriving" : ""));

// the agent's row with the system's cards that are its own, which the figure's beats are read from
const lead = computed(() => withSystemCards(agent.value, rows("messages")));
// what the agent does, and what the figure plays of it: the work of the spell an edit, a read or a search set it (reactions.js spellSpell)
const doings = computed(() => figureStateOf(agent.value, waitingSince.value, now.value));
const spell = ref(null);
const held = computed(() => spellIn(doings.value, spell.value, now.value));
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
// The carrier that takes the work away once it is committed, or null: which it is, the UFO or the claw crane (reactions.js carrierOf), when
// it set off, the stops it makes for the parcels it takes and where it comes from and goes off to; and what is drawn of it and of the
// parcels this frame
const taking = ref(null);
const saucer = ref(null);
const crane = ref(null);
const drawnParcels = ref([]);
// how the figure watching the UFO stands this frame (figure.js watch), or null
let sky = null;
const shownFrame = ref(0);
const headAt = ref({x: 0.5, y: 0.3});
const handAt = ref({x: 0.75, y: 0.6, out: 1, other: {x: 0.25, y: 0.6}});
// The figure's run up the bubbles and off the top of the screen (figure/skyward.js), or null: when it set off, its hops, and once it is out of
// sight, when its parachute brings it back; and where the run is this frame, which the clip on screen turns by
let flight = null;
const flying = ref(null);
// the figure's eagerness for the bar docked under its feet to end (reactions.js eagerFor)
let eager = null;
// the clip the figure plays while its UFO or crane is here (reactions.js VARIANTS watch), picked for each visit
let watching = "watch";
// the clip the held state is played as for this stretch of it (reactions.js variantOf), picked again each time the state changes
let variant = {state: "", clip: ""};
// the chat marks of the workers given work while the telephone's cooldown runs, all called together once it is over (reactions.js heldCall)
let heldCalls = [];
// the stretch the figure is in while a progress bar runs, watching it or with its eyes elsewhere (reactions.js barWatchAt), or null
let barWatch = null;

// the clip of this name the figure has, or idle when it has none
const clipNamed = (name) => clips.find((clip) => clip.name === name) || clips.find((clip) => clip.name === "idle");
const hasClip = (name) => clips.some((clip) => clip.name === name);
const canDraw = (name, posture) => clipNamed(name).postures.includes(posture);
// a clip the figure has and can draw in the posture it rests in, as a pastime must be
const drawnHere = (name) => hasClip(name) && canDraw(name, body.place.posture);
const figureSize = () => ({size: SIZE, below: below.value});

// the clip the figure's body shows for what its agent does: pushing a parcel it built while it stands behind it facing it, standing by on its way
// round behind it, and while its agent runs a command with no unit to build or it has yet to get to where it builds, so it never hammers
// on the way there or with nothing to build
function doing() {
    const pushing = parcels.value.find((each) => each.state === "built");
    if (pushing) return facesToPush(pushing) ? "push" : "idle";
    const building = parcels.value.find((each) => each.state === "building");
    if (building) return inspecting(building, performance.now()) ? "inspect" : "work";
    if (making) return body.place.stays ? "work" : "idle";
    if (builds(held.value.state)) return "idle";
    return heldClip();
}

// whether the figure is set to push `parcel`: behind it, and standing or on its way toward it, never walking away from it round behind it,
// so it never leans in before it faces the parcel
const facesToPush = (parcel) => behind(parcelX(parcel), feetX()) && (!body.trip || body.trip.way === Math.sign(parcelX(parcel) - feetX()));

// the way the figure faces for what its body does: toward the parcel it pushes, else the viewer
function pushFacing() {
    const pushing = parcels.value.find((each) => each.state === "built");
    if (!pushing || !facesToPush(pushing)) return 0;
    return parcelX(pushing) > feetX() ? 90 : 270;
}

// whether the figure sleeps, as it does while its agent is asleep or stopped
const asleep = () => clipOf(held.value.state) === "sleep";

function heldClip() {
    const {state} = held.value;
    if (variant.state !== state) {
        variant = {state, clip: variantOf(clipOf(state), Math.random, drawnHere, {memory: memory.reacted, now: now.value, home: body.footing?.id === "home", bubble: Boolean(nearBubble())})};
        // the rummage goes to the window's edge nearest the figure, leaning out that way, or to the other when it cannot lean out that way
        if (variant.clip === "rummage") stay = {where: "rummage", until: now.value + RUMMAGE_STAY_SECONDS, way: player.reachWay(nearerWay(body.place.x, worldBox()))};
    }
    if (body.place.swings) return "rope_swing";
    // at a wall with nothing to do it leans against it (perches.js leanSpot)
    if (body.place.lean && ["idle", "waiting"].includes(clipOf(state))) return "lean";
    // the rummage waits until the figure stands at the window's edge, its stay there, and the glass search until it stands
    if (variant.clip === "rummage" && (stay.where !== "rummage" || body.trip)) return "idle";
    if (variant.clip === "search" && !body.trip && !drawnHere("search")) return "idle";
    // the glass held up to a bubble only while one is within reach and the figure stands still
    if (variant.clip === "glass_bubble" && (body.trip || !nearBubble())) return "idle";
    return body.place.leans ? (LEANING[variant.clip] ?? variant.clip) : variant.clip;
}

// how long the figure keeps to the window's edge for a rummage, its walk there and the rummage itself, in seconds
const RUMMAGE_STAY_SECONDS = 25;

// what a held clip is played as while the figure sits on the edge of a floor facing the viewer: standing idle, it leans back on its hands
const LEANING = {idle: "ledge_sit"};

// how a beat's clip is held longer: the telephone's talk, until the bubble has said all it says (places.js callStretch); null for any other
const stretchOf = (beat) => (beat.clip === "phone_call" ? callStretch(phrasesSeconds(callPhrases())) : null);

// what plays now, as figureState.js clipFor decides it, with the clip itself in place of its name
function current() {
    if (!body.trip?.moves || body.trip.hopping) beats.value = beats.value.filter((beat) => beat.clip !== "stumble");
    const first = headBeat(beats.value, sequenceNow());
    const beat = first && {clip: first.clip, facing: facingToward(first.card, body.at.x + SIZE / 2), onto: first.onto, holds: first.holds, stretch: stretchOf(first)};
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
        doingFacing: pushFacing(),
        watching: taking.value ? watching : "",
        flying: flying.value,
        eager: Boolean(eager?.on),
        chute: Boolean(body.airborne?.chute),
        composeFacing: composeFacing(),
        readingFacing: readingTurn(),
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
const rawFrameOf = (shown) => ((performance.now() - playing.started) / 1000) * fpsOf(shown);
const exactFrameOf = (shown) => stretchedFrame(rawFrameOf(shown), shown.stretch);
const frameOf = (shown) => Math.floor(exactFrameOf(shown));

// A clip plays out before another starts, or gives way at once when it is interruptible (figureState.js canSwitch). It is the one rule every
// clip goes through, so no clip needs its own check.
const playedOut = () =>
    !playing.shown ||
    (playing.closing !== null
        ? frameOf(playing.shown) >= playing.closing + playing.shown.clip.outro
        : canSwitch(playing.shown.clip, frameOf(playing.shown), playing.index));

// whether the clip on screen may be cut off now by what is wanted instead (pile.js givesWay): a loop, held by a state, may; an act played
// once only as the pile says it may and once it has played its least, so the figure never flickers between acts; anything, for a `trip`
// that drops everything
const mayCut = (shown, trip = null) => givesWay(shown, (performance.now() - playing.started) / 1000, trip);

// how far through its step the walk under a clip on the move is, stepped as the walk's own frames are, `pace` times as quick
function strideNow(pace) {
    const {frames, fps} = clipNamed("walk");
    return (((performance.now() / 1000) * fps * pace) % frames) / frames;
}

// how the head leans while the figure rests idle, now to one side, now the other (figure/headTilt.js)
let headTilt = UPRIGHT;

function step() {
    cancelAnimationFrame(frameTimer);
    if (!player || document.hidden) return;
    const wanted = current();
    if (playing.shown?.clip.outro && wanted.clip.name !== playing.shown.clip.name && playing.closing === null) {
        playing.closing = closeAt(playing.shown.clip, frameOf(playing.shown));
    }
    if (playing.closing !== null && wanted.clip.name === playing.shown.clip.name && frameOf(playing.shown) < playing.closing)
        playing.closing = null;
    // a clip that cuts in, as watching the UFO, takes over at once from whatever plays, and so does a trip out of something's way, the
    // beat it breaks off dropped
    const breaking = Boolean(wanted.startsLeg && body.trip?.pressing && playing.shown && !playing.shown.clip.interruptible && playing.name !== keyOf(wanted)) && mayCut(playing.shown, body.trip);
    if (breaking && playing.shown.once && !playing.shown.arrival && !playing.shown.departure && !playing.shown.landed) beats.value = beats.value.slice(1);
    const finished = cutting || playedOut() || breaking || (wanted.clip.cuts && playing.shown?.clip.name !== wanted.clip.name && mayCut(playing.shown));
    cutting = false;
    const sameAct = goesOnFacing(wanted, playing.shown, finished);
    const continuing = (keyOf(wanted) === playing.name || sameAct) && playing.closing === null;
    const shown = sameAct ? {...wanted, facing: playing.shown.facing} : continuing || finished ? wanted : playing.shown;
    const key = keyOf(shown);
    if (playing.name !== key || (playing.closing !== null && finished)) {
        const turning = shown.clip.intro && playing.shown?.clip.name === shown.clip.name && playing.closing === null;
        playing = {name: key, started: turning ? playing.started : performance.now(), shown, index: 0, closing: null};
    }
    shownClip.value = shown.clip;
    shownFacing.value = shown.facing;
    const index = frameOf(shown);
    playing.index = index;
    // a swat played out while the tickling goes on starts again, so the figure swats for as long as it is tickled
    if (shown.once && index >= shown.clip.frames && shown.clip.name === "tickle_swat" && tickling(pointer, performance.now())) {
        playing.started = performance.now();
        return step();
    }
    if (shown.once && index >= shown.clip.frames) {
        if (shown.departure) {
            body.leaving = false;
            body.here = false;
            return;
        }
        if (shown.arrival) body.arriving = false;
        else if (shown.landed) body.landing = false;
        else beats.value = playedFrom(beats.value, shown.clip.name);
        playing = {name: "", started: 0, shown: null, index: 0, closing: null};
        return step();
    }
    const posture = drawnIn(shown, body.trip ? POSTURES[body.place.posture].travels : body.place.posture, body.trip?.moves);
    // seated, it faces as its seat does, whatever the clip still on screen faced, and turned aside at its laptop (places.js seatedFacing)
    poseToward({posture, facing: SEATED.has(posture) ? seatedFacing(shown.clip, body.place.face) : shown.facing});
    // the leg waiting for the clip it sets off with goes in the frame that clip goes on screen, so the walk is never drawn on the spot
    if (shown === wanted && wanted.startsLeg && !body.trip.moves) depart();
    drawn = posed.posture;
    // until a trip sets off the picture keeps to the figure's place in the posture it is drawn in, so it gets to its feet where it is
    if (!body.trip?.departed && !body.airborne && !flight) rest();
    carry();
    const look = eyesAt(looking, shown.facing, performance.now() / 1000);
    // dancing the disco its visor flashes through the colours, else it lights as a run's end says, once the head faces the run's mark
    visor = lightOnce(visor, facesMark(shown), performance.now() / 1000);
    const lit = shown.clip.name === "disco" ? discoScreen(frameOf(shown) / shown.clip.frames, ACTS.disco.beats) : visorAt(visor, performance.now() / 1000, asleep());
    halo.value = lit && {colour: lit.colour, strength: VISOR.halo * lit.glow * lit.open};
    looking = look.looking;
    const pace = shown.pace ?? 1;
    const stride = drawn === "walk" ? strideNow(pace) : null;
    walking.value = stride !== null || shown.clip.name === "walk";
    shownFrame.value = frameIn(shown.clip, exactFrameOf(shown), playing.closing);
    const seconds = performance.now() / 1000;
    headTilt = tiltAfter(headTilt, seconds, Math.random);
    player.show(posed.turning ? clipNamed("idle") : shown.clip, posed.turning ? 0 : shownFrame.value, posed.facing, {
        posture: drawn,
        eyes: look.eyes,
        stride,
        sky: shown.clip.name === watching ? sky : null,
        throws: shown.clip.name === "rummage" ? (shown.throws ??= throwsFor(Math.random)) : null,
        leanWay: shown.clip.name === "rummage" && stay.where === "rummage" ? stay.way : shown.clip.name === "lean" ? (body.place.lean?.way ?? 0) : 0,
        at: lookingAt(shown),
        open: blinked(),
        screen: lit,
        tilt: shown.clip.name === "idle" ? Math.round(tiltAt(headTilt, seconds) * 4) / 4 : 0,
    });
    headAt.value = player.headAt();
    handAt.value = player.handAt();
    keepParcels(shown);
    keepBall(shown);
    keepLadder();
    frameTimer = requestAnimationFrame(step);
}

// The posture and facing the figure is drawn in, on its way to those of the clip on screen, `target`, through standing whenever it turns
// at a seat (places.js turnStep); while such a turn is `turning` it stands idle, each step waiting until the body has eased into the last
let posed = {posture: "stand", facing: 0, turning: false};

function poseToward(target) {
    if (posed.turning && player.blending()) return;
    const next = turnStep(posed, target);
    const there = (pose) => pose.posture === target.posture && pose.facing === target.facing;
    posed = {...next, turning: !there(next) || (posed.turning && !there(posed))};
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
// a trip that is `pressing`, as one out of the way of a new message, sets off at once, breaking off whatever clip plays
async function moveTo(spot, {straight = false, pace = 1, pressing = false, urgent = false} = {}) {
    if (!tripTo(body.place, spot, figureSize(), {straight, pace})) return restOn(spot);
    body.trip = {to: spot, straight, pace, pressing, urgent, footing: footingOn(spot), legs: []};
    // read back, since the ref hands out its reactive copy, never the object it was given
    const trip = body.trip;
    step();
    if (body.slide) await new Promise((done) => slideWaits.push(done));
    if (body.trip === trip) setOff();
}

// Until it sets off the figure keeps to its ground, so the trip's legs are drawn then, from where it is now to where the spot is now
function setOff() {
    const {to, straight, pace, footing: held} = body.trip;
    const there = keptOnFloor(landingOn(to, held, figureSize()), latestFloors().floors, figureSize());
    const room = roomNow();
    const way = straight ? {via: [], pogo: false} : wayUp(readFloors(), figureSize(), body.place, there, {memory: memory.reacted, now: now.value, room}, Math.random);
    // grown out of its reach since the look sent it, it stays where it is until the next look sends it elsewhere
    if (!way) {
        body.trip = null;
        return step();
    }
    const trip = tripTo(body.place, there, figureSize(), {straight, pace, ...way, memory: memory.reacted, now: now.value, room});
    body.way = Math.sign(there.x - body.place.x);
    stopSwinging();
    if (trip) {
        body.trip = {...body.trip, ...trip, climbs: climbs(trip.legs)};
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
        const {to, footing: held, climbs: climbed} = body.trip;
        const landed = landingOn(to, held, figureSize());
        body.trip = null;
        perched = perchedAfter(Boolean(climbed), latestFloors().floors.find((floor) => floor.id === held?.id)?.kind, performance.now() / 1000);
        if (Math.hypot(landed.x - to.x, landed.y - to.y) >= 1) slide();
        settle(landed, held);
        // round behind a box it built, it sets off pushing it at once
        if (pushWaits(parcels.value)) setTimeout(look);
        return step();
    }
    const left = legs.slice(legs.indexOf(next));
    body.trip = {...body.trip, started: true, moves: false, hopping: Boolean(next.hopping), clip: next.clip, facing: next.facing, legs: left};
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
    // risen from a seat, it turns the way it goes before it sets off
    if (posed.turning) return;
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
    covering = hiddenAt(spot, figureSize(), USER_TURN);
}

// Each frame the figure keeps to what it rests on as that moves (figure/floors.js groundUnder), falling with the bars under it or lifted by them;
// when the ground went from under it, it goes at once, without waiting for its clip, as gravity does not, straight up or down to the
// ground at home and on to its place there
function watchFooting() {
    if (flight) return flyOn();
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
    if (ground.motion === "flung") return flung(ground.speed);
    body.footing = ground.footing;
    // the bars under it drop: it falls, unless it landed a moment ago, when it goes down with them rather than play the fall again, as
    // the bars docked over the compose box go down in steps when a card closes and goes
    if (ground.motion === "dropping" && performance.now() - landedAt >= SETTLED_MS) return fallFrom(body.place, null);
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
// the run up the bubbles above the figure and out over the top of the chat sets off from where it stands, when the bubbles reach that high
function takeOff() {
    const from = {x: body.place.x, y: body.place.y};
    const top = worldBox().top;
    const up = climbOf(readFloors(), figureSize(), from, top);
    if (!up) return;
    flight = {began: performance.now(), hops: skywardHops(from, up, top), back: 0};
    body.footing = null;
}

// Each frame of the run: the figure hops on up; once it has gone off the top it stays out of sight a random few seconds, and then comes
// down on its parachute from above the screen, somewhere over its world, to whatever it falls onto
function flyOn() {
    const now = performance.now();
    const at = skywardAt(flight.hops, now - flight.began, SIZE);
    flying.value = at.gone ? null : at;
    if (!at.gone) return void (body.at = placed({...at, posture: "stand"}, "stand"));
    flight.back ||= now + goneMs(Math.random);
    if (now < flight.back) return;
    const world = worldBox();
    const x = world.left + SIZE / 2 + Math.random() * Math.max(world.right - world.left - SIZE, 0);
    flight = null;
    body.airborne = chuteFrom(x, world.top - SIZE / 4, SKYWARD.chute * SIZE, now, Math.random);
    body.at = placed(body.airborne, "stand");
    step();
}

// when the figure last landed from a fall, on the page's clock; a fall within SETTLED_MS of it is no new fall onto a bubble, and a drop of
// the bars under it then carries it down rather than playing the fall again
let landedAt = -Infinity;
const SETTLED_MS = 1500;

function fallFrom(spot, to) {
    airborneFrom(fallingFrom(spot, to, latestFloors().floors, performance.now(), Math.random, performance.now() - landedAt >= SETTLED_MS));
}

// the figure in the air from this frame, as `airborne` has it
function airborneFrom(airborne) {
    endSlide();
    body.airborne = airborne;
    body.trip = null;
    body.footing = null;
    body.at = placed(body.airborne, body.airborne.posture);
    step();
}

function fallOn() {
    const {airborne, landed} = airborneFrame(body.airborne, latestFloors().floors, performance.now(), keptStill());
    if (airborne && goneUp(airborne, worldBox().top)) return goneOff();
    body.at = placed(airborne ?? landed.spot, (airborne ?? landed.spot).posture);
    body.airborne = airborne;
    if (!landed) return;
    landedAt = performance.now();
    body.landing = landed.standing;
    groundMoved("dropping");
    settle(landed.spot);
    rest();
    step();
    if (landed.to) moveTo(landed.to);
}

// A hop is stepped here, frame by frame, toward the ground it is headed for as that moves (aimedAt), so it lands where the ground is now
// rather than where it was, going higher for ground that rose, within the jump's limit (climbs.js jumpMost); and once that ground has gone,
// or risen out of its reach, it falls from where it is in the air
function hopOn() {
    const trip = body.trip;
    if (trip.footing && !footingNow(trip.footing, figureSize())) return fallFrom({...feetOf(body.at), posture: "stand"}, null);
    const landed = trip.footing ? landingOn(trip.to, trip.footing, figureSize()) : trip.to;
    const aimed = aimedAt(trip, body.leg, body.walk.from, landed, jumpMost(figureSize()));
    if (aimed.lost) return fallFrom({...feetOf(body.at), posture: "stand"}, null);
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
// a launch or a drop has played out; landing from a launch, it very rarely trips (reactions.js "launched")
function squashed(event) {
    if (event.target !== event.currentTarget) return;
    if (moved.value === "launched") react({beat: "launched", time: now.value});
    moved.value = "";
}

// The figure hanging by a hand swings about it (pendulum.js): out the way its trip went as it lands, and with the hand as the ground under
// it carries it sideways
const tilt = ref(0);
// where the disco ball hangs over the figure while it dances (perches.js discoBall)
const ball = ref(null);

// the disco ball found again every frame of the dance, so its string stays tied to the bubble above as the chat scrolls or that bubble
// moves; the dance stops the moment no bubble is above to hang it from
// the ladder against the window's side, set there while the figure goes up it, stands on it and comes down it (perches.js ladderShown)
const ladder = ref(null);
function keepLadder() {
    const shown = ladderShown(body.place, body.trip);
    if (shown !== ladder.value) ladder.value = shown;
}

function keepBall(shown) {
    if (shown.clip.name !== "disco") return;
    ball.value = discoBall(body.place, figureSize(), latestFloors());
    if (!ball.value && beats.value[0]?.clip === "disco") beats.value = beats.value.slice(1);
}
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

// The figure lets go of where it rested, the stay there and whatever it was playing, for a stay at home
function letGo() {
    stay = stayAtHome(stay);
    playing = {name: "", started: 0, shown: null, index: 0, closing: null};
    beats.value = [];
    body.landing = false;
}

// The bubble the figure rides or hangs from is flung up by a fast scroll (floors.js FLUNG): it is thrown off it from its feet, up into the
// air at `speed`, and falls back home, or past the top of the screen it comes back on its parachute (goneOff)
function flung(speed) {
    letGo();
    groundMoved("launched");
    airborneFrom(launchFrom({...feetOf(body.at), face: body.place.face}, speed, performance.now()));
}

// thrown up off the top of the screen: out of sight a while, then down on its parachute as after the run up the bubbles (flyOn)
function goneOff() {
    body.airborne = null;
    flight = {began: performance.now(), hops: [], back: 0};
}

// The floor under a resting figure went, so it falls from where it is and, once it lands, goes on to a stay at home
function uprooted() {
    letGo();
    const spot = stayingAt(stay, figureSize(), body.place);
    const clear = {state: held.value.state, now: Date.now() / 1000, near: body.place, figure: figureSize(), cleared};
    fallFrom({...feetOf(body.at), posture: "stand"}, keptClear(spot, clear));
}

// the scene the reactions are decided in
const scene = () => ({
    voice: voice.value,
    moving: Boolean(body.trip || flight),
    place: body.place,
    beats: beats.value.length,
    held: Boolean(sequenceNow()),
    room: roomNow(),
    arriving: body.arriving,
    leaving: body.leaving,
});

// the sequence that holds the figure now (pile.js sequenceIn): the build, while it has a box in hand, unless the UFO or the crane has come
const sequenceNow = () => sequenceIn({box: parcels.value.some((each) => each.state !== "piled"), carrier: taking.value?.by ?? ""});

// the seconds the figure may be off its spot now for a shenanigan (reactions.js roomFor), as its agent's state and the bar docked under it say
function roomNow() {
    const docks = groundEdge();
    return roomFor(held.value.state, docks.docked ? progressOf(docks.element) : null, now.value);
}

function look() {
    clearTimeout(lookTimer);
    now.value = Date.now() / 1000;
    waitingSince.value = waitingSinceAt(counts.value, waitingSince.value, now.value);
    spell.value = spellFor(doings.value.state, spell.value, now.value, Math.random, memory.tally);
    admiring = admiringAfter(admiring, asleep() || eager?.on ? [] : picturesNear(headCenter()), now.value, Math.random);
    const ongoing = stillGoing(beats.value, doings.value.state, beatOnScreen());
    beats.value = freshBeats(ongoing.beats, beatOnScreen(), now.value);
    cutting ||= ongoing.cut;
    const ground = groundEdge();
    barWatch = barWatchAt(barWatch, Boolean(ground.docked && progressEdge(ground.element)), now.value, Math.random);
    const called = heldCall(heldCalls, beats.value, memory.reacted, now.value);
    if (called) {
        beats.value = [...beats.value, {...called, queuedAt: now.value}];
        heldCalls = [];
    }
    // only what happened in the last few seconds is acted on
    const recent = Math.max(seenAt, now.value - FRESH_SECONDS);
    const happened = [
        ...beatsAfter(lead.value, recent),
        ...cardsAfter(lead.value, knownCards, Math.max(watchedSince, recent)),
        ...testResultsAfter(lead.value, testStates, watchedSince),
        ...facesAfter(rows("reactions"), recent),
        ...sayingsAfter(lead.value, rows("messages"), recent),
        ...readingsAfter(rows("messages"), recent),
        ...writtenFacesAfter(lead.value, rows("messages"), recent),
    ];
    const ends = processEndsAfter(lead.value, processStates);
    if (ends.length) parcels.value = parcels.value.map((each) => ({...each, lit: litAfter(each, ends)}));
    if (happened.length) seenAt = Math.max(seenAt, ...happened.map((fire) => fire.time));
    if (committed(happened)) sendAway();
    const stroll = walkingMoment(body.trip, walkBegan, now.value);
    walkBegan = stroll.began;
    if (stroll.moment && !beats.value.some((beat) => beat.clip === "stumble")) react(stroll.moment);
    const docks = groundEdge();
    // held by a sequence, it gets eager for no run's end until the sequence is over
    const sequence = sequenceNow();
    const eagerness = sequence ? {eager, moment: null} : eagerFor(docks.docked ? progressOf(docks.element) : null, eager, Math.random, now.value);
    eager = eagerness.eager;
    if (eagerness.moment) react(eagerness.moment);
    const work = workMoments(held.value.state, typed, workBegan, now.value);
    typed = false;
    workBegan = work.began;
    [...happened, ...answeredWith(work.moments, parcels.value)].forEach(react);
    // the visor lights at a run's end, unless the figure shoots or smashes a bug for it instead
    visor = visorFor(asleep() || beats.value.some((beat) => ["bug_shot", "bug_smash"].includes(beat.clip)) ? [] : ends, visor, performance.now() / 1000);
    const waited = {state: held.value.state, since: held.value.since, lasted: now.value - held.value.since};
    const pushing = pushWaits(parcels.value);
    // held by a sequence, pushing a box, or eager for a run's end, it takes up nothing else
    const quiet = Boolean(sequence) || pushing || Boolean(eager?.on);
    const egg = quiet ? null : answerTo(waited, voice.value, memory, now.value, Math.random, hasClip)?.beat;
    const over = body.trip ? null : discoBall(body.place, figureSize(), latestFloors());
    const pastime = quiet ? null : pastimeFor({...scene(), ball: over ? over.kind : ""}, waited, pastimesDue, now.value, Math.random, drawnHere, memory.tally);
    if (pastime?.clip === "disco") ball.value = over;
    if (pastime?.flies) takeOff();
    const after = [egg, pastime?.flies ? null : pastime].filter(Boolean);
    if (after.length) beats.value = [...beats.value, ...after];
    if (coveredSince() && !body.airborne && !body.place.stays && !uncut(beats.value, beatOnScreen()) && roomToStepAside(body.place)) stepOutOf(boxAt(body.place, figureSize(), drawn));
    grantUnit();
    clearLeftPile();
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
        pile: pileOf(),
        tally: memory.tally,
        memory: memory.reacted,
        room: roomNow(),
    });
    stay = target.stay;
    // while the UFO or the crane is here the figure stands watching it, and goes nowhere
    // eager for a docked bar to end, it hurries onto the bar and stays there until the bar has ended; for a long run it drops what it does
    const going = eager?.on ? eagerSpot(body.place, figureSize()) : target.spot;
    // a trip that waits to set off gives way to one that drops everything
    if (eager?.urgent && going && body.trip && !body.trip.urgent && !body.trip.moves) body.trip = null;
    if (!body.trip && !body.arriving && !body.airborne && !taking.value && !flight && going && mayLeave(perched, performance.now() / 1000, Boolean(eager?.urgent))) {
        if (eager?.urgent) beats.value = beats.value.slice(0, 1);
        // round behind a box it built and pushing it, it sets off at once, breaking off what it plays, so the build flows into the push
        moveTo(going, {pace: hurried || eager?.on ? SPRINT : 1, pressing: hurried || pushing || Boolean(eager?.urgent), urgent: Boolean(eager?.urgent)});
        hurried = false;
    }
    if (!document.hidden) lookTimer = setTimeout(look, LOOK_EVERY);
}

// what the figure hid where it came to rest, so something that appears under it since, as a new message, is told apart from what it
// could not help covering there
let covering = 0;
// the figure sprints on its next trip, out of the way
let hurried = false;
// the stay on a bubble the figure jumped up onto on purpose, which no trip but an urgent one takes it from before it ends (perches.js
// PERCHED), or null
let perched = null;

// The figure steps out of the way of what is under `box`, its picture, and sprints there, as when it is clicked or a new message appears
// under it (perches.js stepAside)
function stepOutOf(box) {
    ({stay, cleared} = stepAside(stay, box, Date.now() / 1000));
    hurried = true;
}

// whether something has appeared under the figure since it came to rest, as a new message of the agent's under its feet; the user's own
// messages never send it aside
const coveredSince = () => !body.trip && body.footing && hiddenAt(body.place, figureSize(), USER_TURN) > covering;

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
// the way the figure goes: the way its trip takes it while it is on one, else toward the pile
const goingWay = () => (body.trip?.moves ? body.way : Math.sign(slotX(piled()) - feetX()) || 1);
const slotX = (index) => {
    const {edge} = composeEdge();
    return edge.left + edge.width + pileSlot(index).left;
};

// the parcel pile's left and right ends and the top of the floor it stands on, on the page, or null while there is none
function pileOf() {
    const piles = parcels.value.filter((each) => each.state === "piled").map(parcelX);
    return piles.length ? {left: Math.min(...piles) - PARCEL.width / 2, right: Math.max(...piles) + PARCEL.width / 2, top: composeEdge().edge.top} : null;
}

// Where the figure goes to work on the parcels (perches.js targetFor): round behind a parcel it built and on along to the pile with it,
// beside the parcel it builds, or for a new one, a place whose parcel stands clear of the pile
function workOf() {
    const pushing = parcels.value.find((each) => each.state === "built");
    if (pushing) return {x: pushStand(parcelX(pushing), slotX(piled()), body.place.x)};
    const building = parcels.value.find((each) => each.state === "building");
    if (building) return {x: parcelX(building) - beside};
    return making ? {beside, before: slotX(piled() + PILE.high) - PARCEL.width / 2, aim} : null;
}

// the boxes of the run the figure builds for (parcels.js unitsAfter), and whether it builds one now, until it is piled, due since `dueAt`;
// where along the floor it aims to begin the next (parcels.js buildAim), and the time before which it rests after the last was piled
let units = null;
let making = false;
let dueAt = 0;
let aim = null;
let nextBoxAt = 0;

// at a look: with no box in hand the figure builds the next while the run going on is granted boxes, and gives up one not yet begun once
// it ends, or once the build's lifetime is over since it was due (pile.js SEQUENCES build), the run then waiting the build's cooldown
function grantUnit() {
    const inHand = parcels.value.some((each) => each.state !== "piled");
    units = unitsAfter(units, buildRunAt(lead.value?.data?.cards || [], shellRun(), now.value), memory.reacted, now.value, Math.random);
    if (inHand) return;
    const starting = Boolean(units?.granted) && now.value >= nextBoxAt;
    if (starting && !making) {
        aim = nextAim();
        dueAt = now.value;
    }
    making = starting && alive(SEQUENCES.build, dueAt, now.value);
    if (starting && !making) units = {...units, granted: false};
}

// when no run has built since, in seconds, null while one builds; a pile left that long goes as at a commit (parcels.js isPileLeft)
let runEndAt = null;

function clearLeftPile() {
    runEndAt = units ? null : (runEndAt ?? now.value);
    if (isPileLeft(parcels.value, Boolean(units), runEndAt, now.value)) sendAway();
}

// a new place along the floor to begin the next box, clear of the last
function nextAim() {
    const {edge} = composeEdge();
    return buildAim(edge.left, slotX(piled() + PILE.high) - PARCEL.width, aim, Math.random);
}

// the shell command going on that reads as a test run or a build, with the process card it runs under, as a run the figure builds for
const shellRun = () => (builds(held.value.state) ? {card: runningCard(), since: held.value.since} : null);

// The box the figure builds is done: it goes straight round behind it to push it, at once, its idle looks about that wait dropped but the
// one on screen
function builtUp(parcel) {
    parcel.state = "built";
    const shown = playing.shown?.once ? 1 : 0;
    beats.value = beats.value.filter((beat, index) => index < shown || !IDLE_CLIPS.has(beat.clip));
    setTimeout(look);
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
        parcels.value = [...list, {id: ++made, along, up: 0, state: "building", ...hammering(performance.now(), Math.random), blows: 0, lit: "amber", run: units?.card || runningCard()}];
    }
    const building = parcels.value.find((each) => each.state === "building");
    if (building && hammers) countBlows(building, shown);
    if (building && performance.now() >= building.until && !taking.value) builtUp(building);
    const pushing = list.find((each) => each.state === "built");
    if (pushing && !taking.value) {
        const to = slotX(piled());
        if (body.trip?.moves) pushing.along = pushedTo(parcelX(pushing), feetX(), to, body.way) - edge.left;
        if (Math.abs(parcelX(pushing) - to) < PUSH.room) {
            Object.assign(pushing, {along: to - edge.left, state: "piled", up: pileSlot(piled()).up});
            making = false;
            nextBoxAt = now.value + boxGapSeconds(Math.random);
        }
    }
    if (!taking.value) drawnParcels.value = parcels.value.map((each) => ({id: each.id, x: parcelX(each), y: edge.top, up: each.up, scale: 1, opacity: 1, blows: each.blows, lit: each.lit, state: each.state}));
}

// the process card of the run going on now, the last one started, whose end lights a parcel made now; "" with none
const runningCard = () => (lead.value?.data?.cards || []).filter((card) => card.process && card.active).at(-1)?.key ?? "";

// each blow that lands on the parcel being built is counted on it, so the parcel puffs dust at it (CodeParcel.vue)
function countBlows(building, shown) {
    if (counted.started !== playing.started) counted = {started: playing.started, landed: 0};
    const landed = blowsLanded(exactFrameOf(shown), blow.frames, blow.lands);
    building.blows += Math.max(landed - counted.landed, 0);
    counted.landed = landed;
}

// the work is committed: the UFO or the crane comes for every parcel, on the pile or not, and the one the figure is hammering counts as
// finished, so it never stays away because the figure is busy
const committed = (happened) => happened.some((fire) => fire.beat === "committed");

function sendAway() {
    const taken = parcels.value;
    if (taking.value || !taken.length) return;
    for (const each of taken) if (each.state === "building") each.state = "built";
    if (keptStill()) {
        parcels.value = parcels.value.filter((each) => !taken.includes(each));
        return;
    }
    const by = carrierOf(Math.random);
    watching = variantOf("watch", Math.random, hasClip);
    taking.value = {by, began: performance.now(), ids: taken.map((each) => each.id), ...CARRY[by].start(taken.map((each) => ({id: each.id, x: parcelX(each), up: each.up})), worldBox())};
}

// the kinds of the crane's grabbers on its last visit, so the next is never the same sequence (parcels.js kindsOf)
let lastGrabs = [];

// How each carrier sets off for the parcels `items` (each {id, x, up}) in the chat window `world`, and its frame `ms` into its visit: the
// UFO flies in from far off to the right and away to the left, its stops the groups one beam takes; the crane sends a grabber for each box
// along the window's top from one side, the left or the right, and out at the other, or its arm in from the right edge (parcels.js grabsOf)
const CARRY = {
    ufo: {
        start: (items, world) => ({
            stops: stopsOf(items),
            from: {x: world.right + UFO_OFF.right, y: world.top + UFO_OFF.above},
            away: {x: world.left - UFO_OFF.left, y: world.top + UFO_OFF.above},
        }),
        frame: flyUfo,
    },
    crane: {
        start: (items, world) => {
            const [from, away] = craneFrom(Math.random) === "left" ? [world.left - CRANE_OFF, world.right + CRANE_OFF] : [world.right + CRANE_OFF, world.left - CRANE_OFF];
            const grabs = grabsOf(items, {from, away, top: world.top, floor: composeEdge().edge.top, right: world.right}, Math.random, lastGrabs);
            lastGrabs = grabs.map((grab) => grab.kind);
            return {grabs};
        },
        frame: runCrane,
    },
};

// how far past the chat window's side the crane rolls in from and out to, in pixels
const CRANE_OFF = 40;

// Each frame of the carrier taking the work away; once it is gone the parcels it took are gone, and the figure steps forward again over as
// long as it took to step back
function carry() {
    if (!taking.value) return stepForward();
    const done = CARRY[taking.value.by].frame(performance.now() - taking.value.began);
    if (!done) return;
    parcels.value = parcels.value.filter((each) => !taking.value.ids.includes(each.id));
    taking.value = null;
    saucer.value = null;
    crane.value = null;
    sky = {shade: 0, back: sky.back, at: performance.now()};
}

// A frame of the UFO's flight (parcels.js ufoAt): where it and its beam are drawn (parcels.js beamOf), the parcels of the stop it is at
// drawn up the beam into the lamp under its belly one by one, the top one first, swaying and shrinking, those of the stops it has made gone,
// and what the figure watches: the UFO, with a hand shading its eyes while it is still coming in, and stepped back once it first lifts;
// true once it is gone
function flyUfo(ms) {
    const {edge} = composeEdge();
    const at = ufoAt(taking.value.stops, ms, edge.top, taking.value.from, taking.value.away);
    const gone = new Set(taking.value.stops.slice(0, at.taken).flatMap((stop) => stop.ids));
    const rising = parcels.value.filter((each) => taking.value.stops[at.stop].ids.includes(each.id)).sort((one, other) => other.up - one.up);
    const lifted = (each) => {
        const rank = rising.indexOf(each);
        const k = rank >= 0 ? boxRisen(at.risen, rank, rising.length) : 0;
        const x = parcelX(each);
        const y = edge.top + (beamOf(at, edge.top).top + PARCEL.height / 2 + each.up - edge.top) * k;
        return {id: each.id, x: x + (at.x - x) * k + boxSway(k, each.id), y, up: each.up, scale: 1 - 0.65 * k, opacity: k > 0.85 ? (1 - k) / 0.15 : 1, lit: each.lit};
    };
    drawnParcels.value = parcels.value.filter((each) => !gone.has(each.id)).map(lifted);
    saucer.value = {x: at.x, y: at.y, beam: at.beam, width: at.width, reach: beamOf(at, edge.top).reach};
    const lifting = ms - UFO.enter - UFO.beamOn;
    sky = {
        shade: at.coming ? Math.min(ms / STEP_BACK_MS, 1 - ms / UFO.enter) : 0,
        back: Math.min(Math.max(lifting / STEP_BACK_MS, 0), 1),
    };
    return at.gone;
}

// A frame of the crane's visit (parcels.js grabberAt): its grabbers drawn on the rail along the chat window's top and its arm on the right
// edge, each reaching its own box where it is now; a box lifted with its grabber fading as it goes out past the window's top, one pulled
// out sideways fading past its right edge, those taken gone; and the figure watching the first grabber out; true once all are done
function runCrane(ms) {
    const {edge} = composeEdge();
    const world = worldBox();
    const boxes = new Map(parcels.value.map((each) => [each.id, each]));
    const grabbers = taking.value.grabs.map((grab) => {
        const box = boxes.get(grab.id);
        return {id: grab.id, ...grabberAt(grab, ms, {top: world.top, right: world.right, box: {x: parcelX(box), top: boxTop(box, edge.top)}})};
    });
    const of = new Map(grabbers.map((grabber) => [grabber.id, grabber]));
    const moved = (each) => {
        const grabber = of.get(each.id);
        const y = edge.top - (grabber.lifted ?? 0);
        const x = parcelX(each) + (grabber.carried ?? 0);
        const above = (y - each.up - PARCEL.height - world.top) / PARCEL.height + 1;
        const beside = (world.right - x + PARCEL.width / 2) / PARCEL.width;
        return {id: each.id, x, y, up: each.up, scale: 1, opacity: Math.min(Math.max(Math.min(above, beside), 0), 1), lit: each.lit};
    };
    drawnParcels.value = parcels.value.filter((each) => of.has(each.id) && !of.get(each.id).done).map(moved);
    const out = grabbers.filter((grabber) => grabber.out);
    crane.value = {box: world, grabbers: out, look: out[0] && lookOfGrabber(out[0], world)};
    sky = {shade: 0, back: 0};
    return grabbers.every((grabber) => grabber.done);
}

// where the figure looks at a grabber that is out: the end of its cable, or the arm's tongs
const lookOfGrabber = (grabber, world) => (grabber.kind === "arm" ? {x: grabber.tip, y: grabber.y} : {x: grabber.x, y: world.top + Math.max(grabber.chain, 0)});

function stepForward() {
    if (!sky) return;
    const now = performance.now();
    const back = Math.max(sky.back - (now - sky.at) / STEP_BACK_MS, 0);
    sky = back ? {shade: 0, back, at: now} : null;
}

// What the figure looks at on the page: the UFO while it flies, or the crane's claw, else the box it builds, pushes or stacks while it works
// (parcels.js workLook), else, in a stretch it chose to watch it (reactions.js barWatchAt) and with no act played once on screen, the
// leading edge of a progress bar running on the bars docked over the compose box, so its head follows the
// edge as it moves, along the bar and never straight down (places.js watchLook): looking down at it, facing the viewer, standing on the
// bars, and turned to it, its back to the viewer, from the compose box's top under them; null when there is nothing to look at
function lookedAt(shown) {
    if (shown.clip.name === "tickle_swat") return pointerAt;
    if (shown.clip.ownLook) return null;
    const mark = waitingMark();
    if (mark) return mark;
    const flying = saucer.value ?? crane.value?.look;
    if (flying) return flying;
    const read = readingNow();
    if (read) return read;
    const scanned = shown.clip.name === "glass_bubble" && nearBubble();
    if (scanned) return scanningAt(scanned);
    const work = workLook(parcels.value, making, parcelX, composeEdge().edge.top, goingWay());
    if (work) return work.at;
    if (admiring.picture) return {...middleOf(admiring.picture.getBoundingClientRect()), mood: "admiring"};
    // the bar is watched only in a stretch the figure chose to watch it, and never while an act played once is on screen
    if (!watchesBar(barWatch, shown)) return null;
    const docks = groundEdge();
    const edge = onDocks() && (body.footing?.home || body.place.stays) ? progressEdge(docks.element) : null;
    return edge && watchLook(edge, {x: feetX(), y: body.place.y}, docks.element.getBoundingClientRect(), figureSize());
}

// the bubble within reach of where the figure stands to hold its magnifying glass up to (perches.js bubbleNear), or null
const nearBubble = () => bubbleNear(latestFloors(), body.place, figureSize());

// where the figure looks through its glass along the bubble `bubble` beside it: along its text as one reads it (reactions.js readingAt),
// on the part of the bubble nearest the figure
function scanningAt(bubble) {
    const reach = SIZE * 0.8;
    const box = {left: Math.max(bubble.left, body.place.x - reach), right: Math.min(bubble.right, body.place.x + reach), top: bubble.top, bottom: bubble.bottom};
    return readingAt(box, performance.now() / 1000);
}

// the message the figure reads along, its chat mark, while it reads, {card, began, until} in seconds, or null
let reading = null;

// the box of the message's bubble the figure reads now, or null once its time is up or the bubble is not on the page
function readBubble() {
    if (!reading || now.value >= reading.until) return (reading = null);
    return document.querySelector(`[data-figure-mark="${CSS.escape(reading.card)}"]`)?.getBoundingClientRect() ?? null;
}

// where the figure looks reading its message's bubble now (reactions.js readingAt), or null while it reads none
function readingNow() {
    const bubble = readBubble();
    return bubble && readingAt(bubble, Date.now() / 1000 - reading.began);
}

// the way the figure turns to the bubble it reads, its message's or the one it holds its glass up to (reactions.js readingFacing), or null
// while it reads none
function readingTurn() {
    const bubble = readBubble() ?? (heldClip() === "glass_bubble" ? nearBubble() : null);
    return bubble && readingFacing(bubble, body.at.x + SIZE / 2, SIZE);
}

// What told the figure of the run whose end the visor waits to light (figure/visor.js lightOnce), which the head turns to first, whatever
// the figure goes on doing: the run's chat mark, or the bar docked over the compose box when that is nearer (places.js nearestTell); null
// when it waits for none or neither is on the page
function waitingMark() {
    if (!visor || visor.at !== null) return null;
    const mark = document.querySelector(`[data-figure-mark="${CSS.escape(visor.card)}"]`)?.getBoundingClientRect() ?? null;
    const docks = groundEdge();
    const bar = docks.docked ? (progressOf(docks.element)?.bar.getBoundingClientRect() ?? null) : null;
    return nearestTell(mark, bar, headCenter());
}

// whether the head faces the mark of the run whose end the visor waits to light, or cannot turn to it, its clip looking as it does itself
// or the mark not on the page
function facesMark(shown) {
    const mark = waitingMark();
    return !mark || Boolean(shown.clip.ownLook) || (gaze.amount === 1 && Boolean(gaze.point) && faces(gaze.point, mark, headCenter()));
}

// whether the figure is at rest by the bars docked over the compose box
const onDocks = () => groundEdge().docked && !body.trip;

// how far down the figure's picture its head's middle sits, as a share of the picture's height
const HEAD_HEIGHT = 0.3;
let gaze = {point: null, toward: null, amount: 0, at: 0};
// once the figure has loaded, how its head looks at the page, in the page's pixels: from how far before it (figure.js LOOK_REACH), its
// eyes how far above its pivot (figure.js eyesAboveOf), and how far it tips (figure.js HEAD_TIP); and how far down its picture the head
// turns about (figure.js headPivotOf)
let lookHead = null;
let lookPivot = HEAD_HEIGHT;

// where in its picture the figure looks this frame, and how far into the look (figure.js lookToward), or null to look as its clip does
function lookingAt(shown) {
    gaze = gazeAfter(gaze, lookedAt(shown), {x: body.at.x + SIZE / 2, y: body.at.y + SIZE * lookPivot}, performance.now(), lookHead);
    if (!gaze.amount || !gaze.point) return null;
    const eased = gaze.amount * gaze.amount * (3 - 2 * gaze.amount);
    return {x: (gaze.point.x - body.at.x) / SIZE, y: (gaze.point.y - body.at.y) / SIZE, amount: eased, behind: Boolean(gaze.point.behind), mood: gaze.point.mood ?? ""};
}

// the middle of the figure's head on the page, about which its look turns
const headCenter = () => ({x: body.at.x + SIZE / 2, y: body.at.y + SIZE * HEAD_HEIGHT});

const onType = (event) => {
    if (event.target.closest?.(HOME)) typed = true;
};

// what the figure does about a moment, as reactions.js answerTo decides: a beat the body plays, or a look the eyes take on
// The mouse pointer over the figure or near it (figure/tickle.js): moved back and forth it tickles the figure, which swats at it, aiming
// each swat at where the pointer is, and keeps swatting for as long as the tickling goes on; a move that overshoots the figure still counts,
// and one far from it is not heard at all, so the tickle ends only once the pointer has stopped or gone a while
const bodyArea = ref(null);
let pointer = UNTICKLED;
let pointerAt = null;
function pointerMoved(event) {
    const area = bodyArea.value?.getBoundingClientRect();
    if (!area || !nearBody(area, event.clientX, event.clientY)) return;
    pointer = movedTo(pointer, event.clientX, performance.now());
    pointerAt = {x: event.clientX, y: event.clientY};
    if (tickling(pointer, performance.now()) && !beats.value.some((beat) => beat.clip === "tickle_swat")) react({beat: "tickled", time: now.value});
}

// the clip of the beat on screen, or "" while no beat plays: an arrival, a departure or a landing is no beat
const beatOnScreen = () => (playing.shown?.once && !playing.shown.arrival && !playing.shown.departure && !playing.shown.landed ? playing.shown.clip.name : "");

// the moments answered before any beat already waiting: a stumble on a long walk, and a tickle, which the figure swats at at once
const FIRST = new Set(["long_walk", "tickled", "bar_failed"]);

function react(moment) {
    if (!isListening(eager)) return;
    // a worker given work while a call waits or plays is named in that call instead of ringing again
    const joined = moment.beat === "messaged" && moment.card ? joinedCall(beats.value, moment.card) : null;
    if (joined) {
        beats.value = joined;
        return;
    }
    const answer = answerTo(moment, voice.value, memory, now.value, Math.random, hasClip);
    if (moment.beat === "messaged" && moment.card && !answer && !heldCalls.includes(moment.card)) heldCalls = [...heldCalls, moment.card];
    if (answer?.beat && queues(beats.value, answer.beat)) {
        const beat = {...answer.beat, queuedAt: now.value};
        const queued = FIRST.has(moment.beat) ? queuedFirst(beats.value, beat, beatOnScreen()) : {beats: [...beats.value, beat], cut: false};
        beats.value = queued.beats;
        cutting ||= queued.cut;
    }
    // a celebration on its chat mark: off to stand on it, when it has a stand free and no sequence holds the figure, else played where it is
    if (answer?.beat?.onto && !sequenceNow() && markSpot(answer.beat.card, figureSize())) {
        stay = {where: "mark", card: answer.beat.card, until: now.value + MARK_STAY};
        hurried = true;
    }
    // a message to read: the figure looks up at its bubble and reads along it a while (reactions.js readingAt)
    if (answer?.gaze) reading = {card: answer.gaze.card, began: now.value, until: now.value + READING.seconds};
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
        lookHead = {depth: module.LOOK_REACH * SIZE, above: module.eyesAboveOf(loaded) * SIZE, tip: module.HEAD_TIP};
        lookPivot = module.headPivotOf(loaded);
        testResultsAfter(lead.value, testStates);
        processEndsAfter(lead.value, processStates);
        cardsAfter(lead.value, knownCards);
        below.value = module.GROUND;
        canvas.value.width = canvas.value.height = Math.round(SIZE * (window.devicePixelRatio || 1));
        player = new FigurePlayer(loaded, canvas.value);
        drawBlocks();
        drawSaucer();
        drawCanopy();
        drawBug();
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

// the block's pictures for each kind of lights, through the player's stage, so the parcels are drawn as the figure is
function drawBlocks() {
    const ratio = window.devicePixelRatio || 1;
    const blockOf = (lit) => {
        const drawn = Array.from({length: phasesOf(lit)}, (_, phase) => player.stage.drawBlock(lit, phase, SIZE, ratio));
        return {pictures: drawn.map((each) => each.canvas.toDataURL()), width: drawn[0].canvas.width / ratio, height: drawn[0].canvas.height / ratio, below: drawn[0].below};
    };
    blocks.value = Object.fromEntries(LIGHT_KINDS.map((lit) => [lit, blockOf(lit)]));
}

// the saucer's pictures for each step of its lights' blink, through the player's stage
function drawSaucer() {
    const ratio = window.devicePixelRatio || 1;
    const drawn = Array.from({length: UFO.blink}, (_, phase) => player.stage.drawSaucer(phase, SIZE, ratio));
    saucerPicture.value = {pictures: drawn.map((each) => each.canvas.toDataURL()), width: drawn[0].canvas.width / ratio, height: drawn[0].canvas.height / ratio, at: drawn[0].at};
}

// the canopy's picture, through the player's stage
function drawCanopy() {
    const ratio = window.devicePixelRatio || 1;
    const drawn = player.stage.drawCanopy(SIZE, ratio);
    canopyPicture.value = {picture: drawn.canvas.toDataURL(), width: drawn.canvas.width / ratio, height: drawn.canvas.height / ratio, at: drawn.at, ends: drawn.ends};
}

// the bug's pictures, one for each step of its stride, through the player's stage
function drawBug() {
    const ratio = window.devicePixelRatio || 1;
    const drawn = [0, 0.5].map((phase) => player.stage.drawBug(phase, SIZE, ratio));
    bugPicture.value = {pictures: drawn.map((each) => each.canvas.toDataURL()), width: drawn[0].canvas.width / ratio, height: drawn[0].canvas.height / ratio, at: drawn[0].at};
}

watch(voice, load);
watch(belongs, present);
onMounted(() => {
    document.addEventListener("visibilitychange", seen);
    document.addEventListener("input", onType, true);
    window.addEventListener("resize", look);
    window.addEventListener("mousemove", pointerMoved, {passive: true});
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
    window.removeEventListener("mousemove", pointerMoved);
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

// the act on screen, with how far through it the figure is, which the page draws what it holds for (figure/acts.js), or null
const acting = computed(() => (ACTS[shownClip.value?.name] ? {name: shownClip.value.name, u: shownFrame.value / shownClip.value.frames} : null));
const room = computed(() => ({left: body.at.x, right: window.innerWidth - body.at.x - SIZE}));

// What the figure says on the telephone, while it says it (places.js callSays): the lines of the chat mark that set off the call
// (figureState.js callLines), a phrase at a time from the talk's start, in a comic bubble beside its head on the side where it hides the fewest words, else on the handset's side,
// that side chosen once a call, its tail to the handset in the free hand, or to the head when the handset is on its other side
// the chat marks of the workers the call on screen is to, the one that set it off and any it gathered since
const callMarks = () => {
    const call = beats.value[0];
    const keys = call?.clip === "phone_call" ? (call.marks ?? [call.mark]) : [];
    const cards = lead.value?.data?.cards || [];
    return keys.map((key) => cards.find((card) => card.key === key)).filter(Boolean);
};
const calling = () => callMarks()[0];
const callPhrases = () => phrasesOf(callMarks().flatMap((card) => callLines(card, rows("workers"))));
let callSide = {mark: "", side: 0};
const callBubble = computed(() => {
    if (shownClip.value?.name !== "phone_call" || !callSays(shownFrame.value / shownClip.value.frames)) return null;
    const card = calling();
    const phrases = callPhrases();
    if (!phrases.length) return null;
    const {width, height} = bubbleSize(phrases);
    const clip = shownClip.value;
    const seconds = (rawFrameOf(playing.shown) - ACTS.phone_call.talk[0] * clip.frames) / fpsOf(playing.shown);
    const head = {x: body.at.x + headAt.value.x * SIZE, y: body.at.y + headAt.value.y * SIZE};
    const handset = {x: body.at.x + handAt.value.x * SIZE, y: body.at.y + handAt.value.y * SIZE};
    if (callSide.mark !== card.key) callSide = {mark: card.key, side: bubbleSpot(head, width, height, handsetSide(head, handset, width, window.innerWidth), wordsUnder).side};
    const spot = bubbleSpot(head, width, height, callSide.side > 0 ? {left: 0, right: 1} : {left: 1, right: 0}, () => 0);
    const tip = tailEnd(head, handset, callSide.side, SIZE);
    return {phrases, seconds, left: spot.left, top: spot.top, tip: {x: tip.x - spot.left, y: tip.y - spot.top}};
});

// the rows the call's words are read from, the workers the call is to, fetched as the call is set off or gathers another
watch(
    () => callMarks().map((card) => card.key).join(" "),
    async () => {
        const ids = callMarks().map((card) => String(card.row).split(":")).filter(([table]) => table === "workers").map(([, id]) => Number(id));
        if (ids.length) await holding("workers", ids);
    },
);
// the picture squeezed by the act on screen, as the box it is packed in shrinks, or null
const squeezed = computed(() => acting.value && squeezeOf(acting.value.name, acting.value.u));

// the soft glow about the lit visor, centred on the eyes it lights over (figure/visor.js VISOR.halo)
const haloStyle = computed(() => ({
    left: `${headAt.value.x * 100}%`,
    top: `${headAt.value.y * 100}%`,
    opacity: halo.value.strength,
    "--halo": `rgb(${halo.value.colour.map((part) => Math.round(part * 255)).join(" ")})`,
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
    ...(squeezed.value && {scale: `${squeezed.value.x} ${squeezed.value.y}`, transformOrigin: `50% ${(1 - below.value) * 100}%`}),
    ...(chasing.value && {animationDuration: `${chaseMs.value}ms`, "--chase": `${chaseRun.value}px`}),
    ...(grip.value && {rotate: `${tilt.value}rad`, transformOrigin: `${grip.value.x * 100}% ${grip.value.y * 100}%`}),
    ...(acting.value?.name === "rope_swing" && {rotate: `${swingAngle(acting.value.u)}deg`, transformOrigin: `50% ${(1 - below.value - POSTURES.sit.drop - ACTS.rope_swing.rope) * 100}%`}),
}));

// the figure and all it holds are drawn inside the chat alone, cut off at its walls, as when it climbs out over the top
const style = computed(() => {
    const world = worldBox();
    const {x, y} = body.at;
    return {
        width: `${SIZE}px`,
        height: `${SIZE}px`,
        zIndex: LAYER.figure,
        transform: `translate(${x}px, ${y}px)`,
        clipPath: `inset(${world.top - y}px ${x + SIZE - world.right}px ${y + SIZE - world.bottom}px ${world.left - x}px)`,
    };
});
</script>

<template>
    <div
        v-show="figureVisible(body.here)"
        class="voice-figure"
        :style="style"
        aria-hidden="true"
        :data-walking="walking"
        :data-hopping="hopping"
        :data-trip="tripStage"
        :data-clip="shownClip?.name"
        :data-beats="beats.map((beat) => beat.clip).join(' ')"
    >
        <div class="voice-figure-body" :style="bodyStyle" @mousedown.prevent @click="clicked" ref="bodyArea" />
        <div :class="['voice-figure-actor', moved, {chasing}]" :style="actorStyle" @animationend="squashed">
            <canvas ref="canvas" class="voice-figure-canvas" :style="passing || hidesBelowFloor(acting?.name) ? {clipPath: `inset(0 0 ${below * 100}% 0)`} : null" />
            <template v-if="halo">
                <span class="voice-figure-halo" :style="haloStyle" />
            </template>
            <template v-if="mark">
                <span class="voice-figure-marks" :style="markStyle">
                    <template v-for="index in MARK_COUNT" :key="index">
                        <span :style="{animationDelay: `${(-(index - 1) * MARK_DRIFT_SECONDS) / MARK_COUNT}s`}">{{ mark }}</span>
                    </template>
                </span>
            </template>
            <template v-if="acting">
                <FigureAct :name="acting.name" :u="acting.u" :hand="handAt" :head="headAt" :feet="1 - below" :size="SIZE" :room="room" :ball="ball" :canopy="canopyPicture" :bug="bugPicture" />
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
        <template v-if="blocks">
            <CodeParcel
                :x="drawing.x"
                :y="drawing.y"
                :up="drawing.up"
                :scale="drawing.scale"
                :opacity="drawing.opacity"
                :blows="drawing.blows ?? 0"
                :block="blocks[drawing.lit]"
                :ahead="drawing.state === 'built'"
                :piled="drawing.state === 'piled'"
            />
        </template>
    </template>
    <Transition name="step-ladder">
        <StepLadder v-if="ladder" :foot="ladder.foot" :top="ladder.top" />
    </Transition>
    <template v-if="crane">
        <ClawCrane :box="crane.box" :grabbers="crane.grabbers" />
    </template>
    <template v-if="callBubble">
        <ComicBubble :phrases="callBubble.phrases" :seconds="callBubble.seconds" :left="callBubble.left" :top="callBubble.top" :tip="callBubble.tip" :frame="shownFrame" />
    </template>
    <template v-if="saucer && saucerPicture">
        <FlyingSaucer :x="saucer.x" :y="saucer.y" :saucer="saucerPicture" :beam="saucer.beam" :reach="saucer.reach" :width="saucer.width" />
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

/* a soft glow of the visor's colour about it, light added over the figure and the page */
.voice-figure-halo {
    position: absolute;
    width: 46px;
    height: 30px;
    margin: -15px 0 0 -23px;
    border-radius: 50%;
    background: radial-gradient(closest-side, var(--halo), transparent);
    filter: blur(3px);
    mix-blend-mode: screen;
    pointer-events: none;
}

.voice-figure-actor {
    width: 100%;
    height: 100%;
    transform-origin: 50% 100%;
}

.voice-figure-actor.dropping {
    animation: figure-land calc(var(--fall-ms) * 0.5) ease-out both;
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
