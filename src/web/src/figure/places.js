import {GRAVITY} from "../domain/falls.js";
import {ACTS} from "./acts.js";
import {flips} from "./reactions.js";
import {PARCEL, PILED, PUSH} from "./parcels.js";

// Where the figure can stand, read from the page as it is laid out at this moment and never stored: the top edge of the main
// chat's compose box is home, and each of Home's tabs is a place it can go to point at what waits there.
export const HOME = "[data-figure-home]";

// the bars docked over the main chat's compose box, such as a report's, which the figure is pushed up onto while they are there
export const DOCKED_BARS = "[data-figure-docked-bars]";

// how far along its edge the figure may stand, as shares of the edge's width, the one it prefers first
const HOME_ALONG = [0.85, 0.6, 0.35, 0.15];

// What waits on the user, most pressing first; anything that merely happens never outranks these
export const POINT_RANK = ["question", "waiting", "suggestion"];

// The view to point at: the most pressing one that holds something for the user and has a tab open, but not in front
export const pointedView = (counts, tabs) => POINT_RANK.find((view) => counts[view] > 0 && tabs[view] === "behind") || null;

// Each tab on the page by its view: "front" when the user is looking at it, "behind" when another tab of its pane is
export function openTabs() {
    const tabs = {};
    for (const tab of document.querySelectorAll("[data-tab]")) {
        const shown = tab.getAttribute("aria-selected") === "true";
        tabs[tab.dataset.tab] = shown || tabs[tab.dataset.tab] === "front" ? "front" : "behind";
    }
    return tabs;
}

// What a figure standing somewhere must not hide: anything the user can press or type into
const CONTROLS = "button, a[href], input, select, textarea, [role=tab], [role=button], [tabindex]:not([tabindex='-1'])";

// How each posture meets the line it rests on: the share of the figure's height from that line down to the feet of its standing picture,
// and the posture it travels in to get there. It stands with its feet on the line, sits with its hips on it and hangs by its hands from
// it; it leaps straight to a hang. A rest is never a seat: see cornerAt. On the move it walks with its feet on the line.
const SEAT_DROP = 0.26;
// the gripping hand of every voice's hang is 2.91 of the picture's 5.4 units above its standing feet: the short arms of these figures
// reach no higher than the head, so the hand, not the hat, is what meets the bubble's corner
const HANG_DROP = 0.54;
// and 1.25 of those units to its own side of the middle, toward the viewer's right for the left hand of a figure facing them
const GRIP_ASIDE = 1.25 / 5.4;
export const POSTURES = {
    stand: {drop: 0, travels: "stand"},
    sit: {drop: SEAT_DROP, travels: "stand"},
    lounge: {drop: SEAT_DROP, travels: "stand"},
    composed: {drop: SEAT_DROP, travels: "stand"},
    hang: {drop: HANG_DROP, travels: "hang"},
    walk: {drop: 0, travels: "stand"},
};

// Where the gripping hand is in the picture of a figure hanging by its `side` hand, turned `facing` degrees, as shares of the picture's
// width and height; `below` is the share of the picture under the ground its feet stand on
export const gripIn = (side, facing, below) => ({
    x: 0.5 + (side === "l" ? 1 : -1) * GRIP_ASIDE * Math.cos((facing * Math.PI) / 180),
    y: 1 - below - HANG_DROP,
});

// the postures the figure sits in, on a floor or over a ledge's edge, in none of which it ever turns (turnStep)
export const SEATED = new Set(["sit", "lounge", "composed"]);

// The next posture and facing, each {posture, facing}, the figure is drawn in on its way from `from` to `to`: it never turns sitting, so
// from a seat it first stands up facing as it sat, then turns standing, and only sits again once it faces the way it sits; any other
// change is made at once
export function turnStep(from, to) {
    if (from.facing === to.facing || (!SEATED.has(from.posture) && !SEATED.has(to.posture))) return to;
    return {posture: "stand", facing: SEATED.has(from.posture) ? from.facing : to.facing};
}

// how long the figure takes to change from one clip, posture or facing to the next, easing out of the pose before it, in seconds
export const CHANGE_SECONDS = 0.25;

// A figure stepping out of the way sprints, at this many times its walking pace and with its steps that much quicker
export const SPRINT = 2;

// The figure walks this many pixels a second. A jump crouches this long before it leaves the ground and is in the air for this long, a
// little longer for a higher perch, in milliseconds; a fall takes as long as a body takes to drop that far.
const WALK_SPEED = 90;
const JUMP_CROUCH_MS = 280;
const JUMP_AIR_MS = 420;
const JUMP_AIR_PER_PIXEL = 0.25;
const FLIP_CROUCH_MS = 290;
const FLIP_AIR_MS = 600;
const JUMP_EASING = "cubic-bezier(0.2, 0.7, 0.4, 1)";
const FALL_EASING = "cubic-bezier(0.55, 0, 0.9, 0.6)";
// a difference smaller than this is no trip at all: a clip in motion can leave this much of a gap under the figure's feet, and the
// figure settles where it is rather than falling those few pixels
export const STEADY = 5;

// The trip of a picture `size` pixels tall from `from` to `to`, its left and top, or null when they are closer than STEADY: its way, -1
// left or 1 right, and its legs, each a move of the picture taking `ms` after `lead`. Up to a perch it walks to below it and then jumps,
// now and then turning over on a high jump, as the pile draws it with `memory` of when it last did at `now`, or bouncing up on the `pogo`
// stick; down from one it falls first
// and then walks, never walking on air. `straight` is for ground
// that came or went under it: it goes straight up or down where it is, then walks. It lands after a hop unless it `hangs` there, from a
// bubble's corner or on a rope swing's seat. It walks
// at `pace` times its walking speed, which the trip keeps.
export function tripBetween(from, to, size, {straight = false, hangs = false, pace = 1, random = Math.random, memory = null, now = 0, pogo = false} = {}) {
    if (Math.hypot(to.x - from.x, to.y - from.y) < STEADY) return null;
    const across = Math.abs(to.x - from.x);
    const walk = across < STEADY ? 0 : (across / (WALK_SPEED * pace)) * 1000;
    const height = Math.abs(to.y - from.y);
    const up = to.y < from.y;
    const flip = up && !pogo && flips(height, size, random, memory, now);
    const air = up ? JUMP_AIR_MS + Math.min(height, 400) * JUMP_AIR_PER_PIXEL : Math.sqrt((2 * height) / GRAVITY) * 1000;
    const hop = {
        x: to.x,
        y: to.y,
        ms: height > STEADY ? (flip ? FLIP_AIR_MS : air) : 0,
        lead: flip ? FLIP_CROUCH_MS : up ? JUMP_CROUCH_MS : 0,
        easing: up ? JUMP_EASING : FALL_EASING,
        hopping: true,
        clip: flip ? "backflip" : up ? "jump" : "fall",
    };
    const stroll = {x: to.x, y: to.y, ms: walk, lead: 0, easing: "linear"};
    const rise = pogo ? pogoLeg(to, size) : hop;
    const legs = up && !straight ? [{...stroll, y: from.y}, rise] : [{...hop, x: from.x}, stroll];
    return {way: Math.sign(to.x - from.x) || 1, legs, lands: !hangs, pace};
}

// the leg up to `to` on the pogo stick, for a picture `size` pixels tall: as long as the stick's act (acts.js pogo), stepped by pogoAt
const pogoLeg = (to, size) => ({x: to.x, y: to.y, ms: (ACTS.pogo.frames / ACTS.pogo.fps) * 1000, lead: 0, easing: "linear", hopping: true, pogo: true, size, clip: "pogo"});

// The posture a clip is drawn in at a place of `posture`: that one when the clip can be drawn in it, else the first the clip can
export const postureOf = (clip, posture) => (clip.postures.includes(posture) ? posture : clip.postures[0]);

// The posture the clip on screen is drawn in at a place of `posture`: on the move only while the figure `moves`, so its legs stop walking
// the moment it stops, whatever the clip over them still has to play
export const drawnIn = (shown, posture, moves) => (shown.posture === "walk" && moves ? "walk" : postureOf(shown.clip, posture));

// The box a figure's picture takes in `posture` on a spot's line: `size` pixels square, `below` the share of its picture under its feet
export const boxAt = (spot, {size, below}, posture = spot.posture) => {
    const top = spot.y - (1 - below - POSTURES[posture].drop) * size;
    return {left: spot.x - size / 2, right: spot.x + size / 2, top, bottom: top + size};
};

export const overlaps = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
// whether an element is drawn at all, its own and its ancestors' opacity and visibility counted, as a turn's tools are not until it is
// hovered; where the page cannot say, it is taken as drawn
const visible = (element) => element.checkVisibility?.({opacityProperty: true, visibilityProperty: true}) ?? true;

// The box the figure lives in, which no part of it is ever drawn outside: the main chat's window, else the window
export function worldBox() {
    const world = document.querySelector(HOME)?.closest(".thread");
    return world ? world.getBoundingClientRect() : {left: 0, top: 0, right: window.innerWidth, bottom: window.innerHeight};
}

// how far past its world's edge a figure may be drawn, in pixels, for the rounding of a spot kept just inside it
const EDGE = 0.5;

// how far inside the chat's left and right sides a figure on a bubble keeps its picture, in pixels, so the sides never cut its frame
export const WALL_ROOM = 20;

// whether a figure on a spot keeps WALL_ROOM inside its world's left and right sides
export function offWalls(spot, figure, world = worldBox()) {
    const box = boxAt(spot, figure);
    return box.left >= world.left + WALL_ROOM && box.right <= world.right - WALL_ROOM;
}

// Whether a figure on a spot is inside its world: its picture within the world's left, right and top, and the line it rests on at or
// above the world's foot, as a seated figure's legs hang past any edge it sits on; a hanging figure is inside it whole. A seated figure
// needs only its body inside, as it sits on the very corner of a box with its legs hanging past the end, the empty sides of its picture
// over the world's edge
export function inWorld(spot, figure, world = worldBox()) {
    const box = boxAt(spot, figure);
    const width = box.right - box.left;
    const [left, right] = spot.posture === "sit" ? [box.left + BODY.left * width, box.left + BODY.right * width] : [box.left, box.right];
    const foot = spot.posture === "hang" ? box.bottom : spot.y;
    return left >= world.left - EDGE && right <= world.right + EDGE && box.top >= world.top - EDGE && foot <= world.bottom + EDGE;
}

// Where across a figure's picture it looks for words and controls under its body, as shares of the picture's width and height: the
// middle of it, where the body is drawn, from the hat to the feet
const BODY_XS = [0.35, 0.5, 0.65];
const BODY_YS = [0.15, 0.3, 0.45, 0.6, 0.75, 0.9];
// the part of the picture the body is drawn in, as shares of its width and height, which is what the user can click
export const BODY = {left: BODY_XS[0], right: BODY_XS.at(-1), top: BODY_YS[0], bottom: BODY_YS.at(-1)};

// how far in from a floor's end a figure standing at its corner has its middle, as a share of its height: half its body's width and a
// margin more, so both feet are on the floor and well clear of its end, never one over the edge
export const FEET_INBOARD = (BODY.right - BODY.left) / 2 + 0.08;

// the part of the body that takes the click: above the line the figure rests on, as hiddenAt counts it, so a figure sitting on the chat
// box never takes a press meant for the box below its seat
export function clickedBody(posture, below) {
    if (posture === "hang") return BODY;
    return {...BODY, bottom: Math.min(BODY.bottom, 1 - below - POSTURES[posture].drop)};
}

// whether a word is drawn at this point of the page: the character the page has there holds ink, is drawn, and its box holds the point
function onWord(x, y) {
    const caret = document.caretRangeFromPoint?.(x, y);
    if (!caret || caret.startContainer.nodeType !== Node.TEXT_NODE || !visible(caret.startContainer.parentElement)) return false;
    const text = caret.startContainer;
    const at = Math.min(caret.startOffset, text.length - 1);
    for (const from of [at - 1, at].filter((each) => each >= 0)) {
        if (!text.data[from].trim()) continue;
        const glyph = document.createRange();
        glyph.setStart(text, from);
        glyph.setEnd(text, from + 1);
        if ([...glyph.getClientRects()].some((box) => x >= box.left && x <= box.right && y >= box.top && y <= box.bottom)) return true;
    }
    return false;
}

// the points across a box where the figure's body is drawn
const bodyPoints = (box) =>
    BODY_YS.flatMap((down) =>
        BODY_XS.map((across) => [box.left + across * (box.right - box.left), box.top + down * (box.bottom - box.top)])
    );

// How many of the points of its body a figure at this spot draws over a control or a word: the part of it above the line it stands or
// sits on, as below that line it only hangs over the thing it rests on, and all of a figure hanging from its line
export function hiddenAt(spot, figure) {
    const picture = boxAt(spot, figure);
    const box = spot.posture === "hang" ? picture : {...picture, bottom: Math.min(picture.bottom, spot.y)};
    const controls = [...document.querySelectorAll(CONTROLS)]
        .map((control) => ({control, rect: control.getBoundingClientRect()}))
        .filter(({control, rect}) => rect.width && rect.height && overlaps(box, rect) && visible(control))
        .map(({rect}) => rect);
    const onControl = (x, y) =>
        controls.some((control) => x >= control.left && x <= control.right && y >= control.top && y <= control.bottom);
    return bodyPoints(box).filter(([x, y]) => onControl(x, y) || onWord(x, y)).length;
}

// The spot of those inside the figure's world that hides the fewest controls and words, none where it can, or null when none is inside
// it; of spots alike, the one nearest `near`, where the figure stands now, so it does not wander between equally good places
export function freeSpot(spots, figure, near) {
    const world = worldBox();
    const away = (spot) => (near ? Math.hypot(spot.x - near.x, spot.y - near.y) : 0);
    const ranked = spots
        .filter((spot) => inWorld(spot, figure, world))
        .map((spot) => ({spot, covered: hiddenAt(spot, figure), away: away(spot)}));
    if (!ranked.length) return null;
    return ranked.reduce((best, each) =>
        each.covered < best.covered || (each.covered === best.covered && each.away < best.away) ? each : best
    ).spot;
}

// The spots on an element's top edge at each share of its width
const alongTop = (box, shares) => shares.map((share) => ({x: box.left + box.width * share, y: box.top, posture: "stand"}));

// Where a figure goes to point at a tab: standing on top of it, at its middle or toward either end, so its feet are on the tab and some
// spot on it is clear of whatever else is open beside the tabs
const ON_TAB = [0.5, 0.25, 0.75];

const tabSpots = (tab) => alongTop(tab.getBoundingClientRect(), ON_TAB);

// Where a figure rests at the end of an edge: standing on the corner of a box, its feet on the top, turned along the edge and a third of
// the way back toward the viewer, a little inboard of the corner so it stands on the surface. Sitting there it sits just inside the corner
// (seatAt), its seat on the box and its knees past the end, as a seat further in hangs the legs over the face of the box, so it looks as if
// it sinks into it to the knees.
const CORNER_SIDES = {
    right: {along: 1, inboard: -1, face: 60},
    left: {along: 0, inboard: 1, face: 300},
};
const CORNER_INBOARD = FEET_INBOARD;

// The place on one corner of a box's top edge, `side` being "left" or "right", the feet `reach` of the figure's height inside the corner;
// `face` turns the figure along the edge, 0 faces the viewer
export function cornerAt(box, side, {size}, reach = CORNER_INBOARD) {
    const {along, inboard, face} = CORNER_SIDES[side];
    return {x: box.left + box.width * along + inboard * reach * size, y: box.top, face, posture: "stand"};
}

// Where a figure sits now and then at a corner of the edge: back from the end on the floor's top, lounging (POSTURES lounge), side-on with
// its legs straight out along the floor away from the end and its hands flat behind it, its middle FEET_INBOARD inside the corner and a
// share more, so it never seems to slide off the end
export const SEAT_INBOARD = FEET_INBOARD + 0.12;

export function seatAt(box, side, {size}) {
    const inboard = side === "right" ? -1 : 1;
    return {x: box.left + box.width * (side === "right" ? 1 : 0) + inboard * SEAT_INBOARD * size, y: box.top, face: loungeFacing(inboard), posture: "lounge"};
}

// the way a lounging figure faces, side-on with its legs along the floor toward `way` (1 to the right, -1 to the left), never the viewer
export const loungeFacing = (way) => (way > 0 ? 90 : 270);

// the least a figure at its laptop is turned from the viewer, in degrees: three-quarters
export const ASIDE = 60;

// the way a figure seated playing `clip` faces on a spot facing `face`: the spot's way, turned to three-quarters for a clip drawn aside
// (figure.js CLIPS aside) where the spot faces nearer the viewer, to the side it already leans to
export function seatedFacing(clip, face) {
    const turn = ((((face + 180) % 360) + 360) % 360) - 180;
    if (!clip.aside || Math.abs(turn) >= ASIDE) return face;
    return turn < 0 ? 360 - ASIDE : ASIDE;
}

// Where the figure sits at home: on a corner of the edge it stands on, beside the pile (freeEdge), whose seat is inside its world and hides
// nothing, the one nearest `near`; null when neither corner holds a seat
export function seatOf(figure, near) {
    const {element, edge} = freeEdge();
    const seats = ["left", "right"]
        .map((side) => seatAt(edge, side, figure))
        .filter((seat) => element && inWorld(seat, figure) && !hiddenAt(seat, figure));
    const away = (seat) => (near ? Math.abs(seat.x - near.x) : 0);
    const seat = seats.sort((a, b) => away(a) - away(b))[0];
    return seat ? {...seat, view: null, on: element} : null;
}

// A spot on its feet on the floor the parcel pile stands on (`pile`, its left and right ends and the top of its floor, in pixels), moved
// beside the pile so the figure never stands in front of the parcels; a seat on the edge, or a spot on another floor, as it is
export function besidePile(spot, pile, {size}) {
    const half = ((BODY.right - BODY.left) / 2) * size;
    const onIt = pile && spot.posture === "stand" && Math.abs(spot.y - pile.top) < 1 && spot.x + half > pile.left && spot.x - half < pile.right;
    return onIt ? {...spot, x: pile.left - half - PILE_GAP} : spot;
}

// how far beside the pile a figure stands, in pixels, past its body, enough to keep its hands off the parcels
const PILE_GAP = 7;

// The box the boxes on the pile take on the page (parcels.js PILED, marked by chat/CodeParcel.vue), or null with none piled
export function pileBox() {
    const boxes = [...document.querySelectorAll(PILED)].map((each) => each.getBoundingClientRect()).filter((box) => box.width && box.height);
    if (!boxes.length) return null;
    return {left: Math.min(...boxes.map((box) => box.left)), right: Math.max(...boxes.map((box) => box.right)), top: Math.min(...boxes.map((box) => box.top)), bottom: Math.max(...boxes.map((box) => box.bottom))};
}

// whether a figure at `spot` keeps clear of the pile, the part of its picture its body is drawn in (BODY) overlapping none of the boxes on it
export function clearOfPile(spot, figure) {
    const pile = pileBox();
    if (!pile) return true;
    const box = boxAt(spot, figure);
    const width = box.right - box.left;
    return !overlaps({left: box.left + BODY.left * width, right: box.left + BODY.right * width, top: box.top + BODY.top * width, bottom: box.bottom}, pile);
}

// how far from the edge at home the pile's foot may be and still stand on it, in pixels, as the boxes' pictures reach a little below it
const PILE_FOOT = 4;

// The edge at home the figure rests, sits and strolls on (groundEdge), with the pile's corner cut off when the pile stands on it: the free
// part of it beside the pile, PILE_GAP clear of the boxes, as the corner is the pile's
export function freeEdge() {
    const ground = groundEdge();
    const pile = pileBox();
    const {left, width, top} = ground.edge;
    if (!pile || Math.abs(pile.bottom - top) > PILE_FOOT || pile.left > left + width || pile.right < left) return ground;
    return {...ground, edge: {...ground.edge, width: Math.max(pile.left - PILE_GAP - left, 0)}};
}

// the pixels of a figure standing on an edge above it
export const standRise = ({size, below}) => (1 - below) * size;

// A spot at home standing or sitting, moved inside the figure's world: its picture within the world's left, right and top, and the line
// it rests on at or above the world's foot
function insideWorld(spot, {size, below}) {
    const world = worldBox();
    const drop = POSTURES[spot.posture].drop * size;
    return {
        ...spot,
        x: Math.min(Math.max(spot.x, world.left + size / 2), world.right - size / 2),
        y: Math.min(Math.max(spot.y, world.top + (1 - below) * size - drop), world.bottom),
    };
}

// the places on either corner of the edge at home, and the places along it, each moved inside the figure's world
const homeCorners = (edge, figure) => Object.keys(CORNER_SIDES).map((side) => insideWorld(cornerAt(edge, side, figure), figure));
const homeStands = (edge, figure) => alongTop(edge, HOME_ALONG).map((spot) => insideWorld(spot, figure));

// Where the figure rests at home: on a corner of the edge it stands on, beside the pile (freeEdge), on its feet; with nothing there, on the
// foot of its world
export function restOf(figure, near) {
    const {element, edge} = freeEdge();
    return {...freeSpot(homeCorners(edge, figure), figure, near), view: null, on: element};
}

// Where a figure that steps out of the way goes at home, its picture clear of `box`, the one it stepped aside from: a corner while it
// rests, else a corner or a place along the edge. The first free one on the right of the box is taken, free being that it hides nothing,
// else the one on either side that hides least; null when none at home is clear of the box.
export function clearOf(box, figure, near, resting) {
    const {element, edge} = freeEdge();
    const spots = (resting ? homeCorners(edge, figure) : [...homeCorners(edge, figure), ...homeStands(edge, figure)]).filter(
        (each) => !overlaps(boxAt(each, figure), box)
    );
    const right = freeSpot(
        spots.filter((each) => each.x > (box.left + box.right) / 2),
        figure,
        near
    );
    const spot = right && !hiddenAt(right, figure) ? right : freeSpot(spots, figure, near);
    return spot && {...spot, view: null, on: element};
}

// The edge a figure stands on at home: the bars docked over the main chat's compose box while there are any, `docked` then, else the
// compose box, else the foot of the window
export function groundEdge() {
    const home = document.querySelector(HOME);
    const bars = home?.closest(".thread")?.querySelector(DOCKED_BARS);
    if (!bars) return {...composeEdge(), docked: false};
    const box = bars.getBoundingClientRect();
    return {element: bars, docked: true, edge: {left: box.left, width: box.width, top: box.top}};
}

// Whether the figure resting at `place` has room to step aside from what appeared under it: never while it stands on bars docked over the
// compose box that span the box whole, `within` pixels, as a full-width card does, with nowhere beside them to step to; on narrower bars,
// or anywhere else, it has
export const SPANS = {within: 2};
export function roomToStepAside(place) {
    const {element, docked, edge} = groundEdge();
    if (!docked || place.on !== element) return true;
    const home = composeEdge().edge;
    return edge.left > home.left + SPANS.within || edge.left + edge.width < home.left + home.width - SPANS.within;
}

// A docked card that has finished and closes by itself soon is marked for the figure; while the top one of the bars docked over the compose
// box, the one the figure would stand on, is such a card, the ground at home is about to go
export const CLOSING = "[data-figure-closing]";
export function homeCloses() {
    const {element, docked} = groundEdge();
    return docked && Boolean(element.firstElementChild?.matches(CLOSING));
}

// a progress bar's fill marked for the figure, which it watches while it runs
export const PROGRESS = "[data-figure-progress]";

// The leading edge of the progress bar running on `element`, as bars docked over the compose box, as the point on the page where its fill
// ends, half way down it; null when none runs there
export function progressEdge(element) {
    const fill = element.querySelector(PROGRESS);
    if (!fill) return null;
    const box = fill.getBoundingClientRect();
    return {x: box.right, y: box.top + box.height / 2};
}

// whether the figure says whom it calls at `u` of its call (acts.js phone_call): from the talk's start until the handset is down
export const callSays = (u) => u >= ACTS.phone_call.talk[0] && u < ACTS.phone_call.hang[1];

// The call's talk held longer so its bubble is up for `seconds` at least (timeline.js stretchedFrame): the talk played round again as
// many more times as that takes, none when the call is long enough as it is; the talk's frames are where the act's own time is in it,
// its last frame at 1 (figure.js onceTime)
export function callStretch(seconds) {
    const act = ACTS.phone_call;
    const [from, to] = act.talk.map((u) => u * (act.frames - 1));
    const said = ((act.hang[1] - act.talk[0]) * act.frames) / act.fps;
    const rounds = Math.max(Math.ceil(((seconds - said) * act.fps) / (to - from)), 0);
    return {from, to, extra: rounds * (to - from)};
}

// The speech bubble the figure says something in beside its head at `head`, a page point, `width` by `height` pixels: up and out to one side
// of the head, the side where it hides the fewest words, as `hides(box)` counts them, toward the side with more `room` when both hide as
// many; its box on the page and the side, 1 to the right
export const BUBBLE = {gap: 10, rise: 14, ear: 0.2};
export function bubbleSpot(head, width, height, room, hides) {
    const box = (side) => {
        const left = side > 0 ? head.x + BUBBLE.gap : head.x - BUBBLE.gap - width;
        const top = head.y - BUBBLE.rise - height;
        return {left, right: left + width, top, bottom: top + height};
    };
    const sides = room.right >= room.left ? [1, -1] : [-1, 1];
    const side = sides.reduce((best, each) => (hides(box(each)) < hides(box(best)) ? each : best));
    return {...box(side), side};
}

// the room to hand bubbleSpot for the call's bubble `width` wide: the side of the head the handset at `handset` is on, so the tail is short
// and never crosses the face, when the bubble fits there on the page `page` wide, else the other side
export function handsetSide(head, handset, width, page) {
    const toward = handset.x < head.x ? -1 : 1;
    const side = (toward > 0 ? page - head.x : head.x) - BUBBLE.gap >= width ? toward : -toward;
    return side > 0 ? {left: 0, right: 1} : {left: 1, right: 0};
}

// where the tail of a call bubble standing on `side` of the head ends: at the handset when the handset is on that side, else at the head's
// edge on that side, `ear` of the figure's `size` out from the eyes, so the tail never crosses the face
export function tailEnd(head, handset, side, size) {
    return Math.sign(handset.x - head.x) === side ? handset : {x: head.x + side * BUBBLE.ear * size, y: head.y};
}

// how many words of the chat the box `box` on the page covers, at the points of a grid over it
export const wordsUnder = (box) => bodyPoints(box).filter(([x, y]) => onWord(x, y)).length;

// a progress bar marked for the figure, its value how it ended, as the card's tone, and empty while it runs
export const BAR = "[data-figure-bar]";

// How the figure watches a bar running on the bars docked over the compose box: it stands on them `aside` of its picture to the left of
// the bar's end, where the bar is heading, so it looks along the bar and never straight down on it, standing back `back` pixels from the
// bar's end, about the figure's own width, so it looks down along the bar at a gentle angle; and it looks at the leading edge kept at
// least `along` of its picture to one side of where it stands, toward the bar's end
export const WATCH = {back: 112, along: 0.4};

// the spot the figure watches the running bar from (WATCH), on top of the docked bars; null with no bar running there
export function watchSpot(figure) {
    const {element, docked, edge} = groundEdge();
    const track = docked ? element.querySelector(BAR) : null;
    if (!track?.querySelector(PROGRESS)) return null;
    const end = track.getBoundingClientRect().right;
    return {...insideWorld({x: end - WATCH.back, y: edge.top, face: 0, posture: "stand"}, figure), view: null, on: element};
}

// What the figure looks at while it watches the bar whose leading edge is `edge`, standing at `feet`, page points, its picture `figure`:
// the edge, kept to one side of it toward the bar's end (WATCH along) so the look runs along the bar; and `behind`, when it stands in
// front of the mark, `mark` its box on the page, its feet below the mark, as on the compose box under a dock covering it: then it turns
// its head to the mark on the page behind it, its back to the viewer, as one looking at a screen; on top of the mark it looks down at it
// facing the viewer
export function watchLook(edge, feet, mark, figure) {
    const near = Math.abs(edge.x - feet.x) < WATCH.along * figure.size;
    return {x: near ? feet.x + WATCH.along * figure.size : edge.x, y: edge.y, behind: feet.y > mark.bottom + 1};
}

// How the progress bar on `element` stands, as the bars docked over the compose box: the bar itself, how far its fill has run, 0 to 1,
// how it ended, "" while it runs, and when its run began, in seconds; null when there is none
export function progressOf(element) {
    const bar = element.querySelector(BAR);
    const fill = bar?.firstElementChild;
    if (!fill) return null;
    const share = fill.getBoundingClientRect().width / Math.max(bar.getBoundingClientRect().width, 1);
    return {bar, share, ended: bar.dataset.figureBar, began: Number(bar.dataset.figureBegan)};
}

// The main chat's compose box and its top edge, whatever is docked over it, else the foot of the window: the floor the figure builds on
export function composeEdge() {
    const element = document.querySelector(HOME);
    if (!element) return {element: null, edge: {left: 0, width: window.innerWidth, top: window.innerHeight}};
    const box = element.getBoundingClientRect();
    return {element, edge: {left: box.left, width: box.width, top: box.top}};
}

// Where the figure stands to build or to push what it built: on its feet on the compose box's top edge, whatever is docked over it, and
// kept there as bars dock and go (`stays`, floors.js footingOn); at `x` on the page when given, beside the parcel it builds or behind one
// it pushes, else at a free place along the edge whose parcel, `beside` pixels from its feet, stands clear of the pile from `before` on
// and with room behind it, on its left, for the figure to stand and push it, the one nearest `aim` across the page when given
export function buildSpot(figure, near, {x = null, beside = 0, before = Infinity, aim = null} = {}) {
    const {element, edge} = composeEdge();
    const spot = x === null ? freeBuildSpot(edge, figure, aim === null ? near : {x: aim, y: edge.top}, beside, before) : insideWorld({x, y: edge.top, posture: "stand"}, figure);
    return spot && {...spot, view: null, on: element, stays: true};
}

function freeBuildSpot(edge, figure, near, beside, before) {
    const stands = homeStands(edge, figure);
    const leftmost = Math.min(...stands.map((spot) => spot.x));
    const clear = stands.filter((spot) => spot.x + beside + PARCEL.width < before && spot.x + beside - PUSH.reach - PUSH.room >= leftmost);
    return freeSpot(clear.length ? clear : stands, figure, near);
}

// The trip of a figure resting at `place` to `spot` (tripBetween), from its picture in the posture it travels in where it is to its picture
// in the posture it travels in there; on a climb it hops on up from each foothold of `via` (perches.js climbOf) to the next, and on to the
// spot, or goes up in one on the `pogo` stick
export function tripTo(place, spot, figure, {straight = false, pace = 1, random = Math.random, via = [], memory = null, now = 0, pogo = false} = {}) {
    const corner = (each) => {
        const box = boxAt(each, figure, POSTURES[each.posture].travels);
        return {x: box.left, y: box.top};
    };
    const [from, ...stops] = [place, ...via, spot].map(corner);
    const trip = tripBetween(from, stops[0], figure.size, {straight, hangs: spot.posture === "hang" || Boolean(spot.swings), pace, random, memory, now, pogo});
    const hops = stops.slice(1).map((to, index) => tripBetween(stops[index], to, figure.size, {random, memory, now})?.legs.find((leg) => leg.hopping));
    return trip && {...trip, legs: [...trip.legs, ...hops.filter(Boolean)]};
}

// The way a figure whose middle is at `x` turns to look at a chat mark, by its key: to its right or its left, or toward the viewer when
// the mark is not on the page
export function facingToward(key, x) {
    const mark = key && document.querySelector(`[data-figure-mark="${CSS.escape(key)}"]`);
    if (!mark) return 0;
    const box = mark.getBoundingClientRect();
    return box.left + box.width / 2 > x ? 90 : 270;
}

// Where the figure stands at a view's tab, or null when the tab is gone or no spot on it is inside the figure's world; with no view, where
// it stands at home, on the main chat's compose box or the bars docked over it. Each spot names the element it rests on as
// `on`, so the figure can tell when that element has gone or moved.
export function spotOf(view, figure, near) {
    if (view) {
        const tab = document.querySelector(`[data-tab="${CSS.escape(view)}"]`);
        const spot = tab && freeSpot(tabSpots(tab), figure, near);
        return spot ? {...spot, view, on: tab} : null;
    }
    const {element, edge} = freeEdge();
    return {...freeSpot(homeStands(edge, figure), figure, near), view: null, on: element};
}
