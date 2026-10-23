import {RESTS, clipOf} from "../domain/figureState.js";
import {climbStops, jumpMost} from "./climbs.js";
import {holds, readFloors} from "./floors.js";
import {besidePile, boxAt, buildSpot, clearOf, groundEdge, hiddenAt, homeCloses, openTabs, overlaps, pointedView, cornerAt, restOf, seatOf, standRise, spotOf} from "./places.js";
import {FREE, letsGoFor} from "./reactions.js";
import {PILE, draw} from "./pile.js";

// Where a figure perches on a message bubble now and then, instead of the compose box's edge: on top of it with its legs over the side,
// or hanging from its top corner by its hands. A perch names its bubble's floor (figure/floors.js), so it rides the bubble as the thread
// scrolls, and is let go when the bubble leaves the thread's view.
export const STANDS = "stand";
export const HANGS = "hang";

// A hang from a bubble's corner is short, as hanging is work, in seconds between the two
export const HANG_STAY = [8, 20];

// The next place to go and for how many seconds to stay, as {where, stay}, drawn from the pile (pile.js roam): mostly it strolls along the
// compose box's edge and stands a while on a corner of it, now and then sits on the corner itself with its legs hanging past the end
// (places.js seatAt), perches on a message bubble or crosses to stand on one of the page's tabs, and whatever the agent is doing it does
// from there; with nothing to do it may sit on the edge of the floor it stands on, facing the viewer. `tally` counts the acts since the
// last shenanigan, a perch on a bubble being one, and the figure is `free` while it has nothing to do.
export function roamNext(random, tally, free = false) {
    const drawn = draw({moment: "roam", tally, free}, random);
    return {where: drawn.name, stay: between(drawn.stay, random)};
}

// a number between the two in `range`
export const between = ([least, most], random) => least + random() * (most - least);

// the side of a bubble with more room outside it, so a figure there stays off the bubbles' text
const sideOf = (rect, scroller) => (rect.left - scroller.left > scroller.right - rect.right ? "left" : "right");

// whether a figure perched on this bubble's top corner stays inside the thread's view `scroller`
const inView = (rect, scroller, figure) => rect.top - standRise(figure) >= scroller.top && rect.top <= scroller.bottom - 8;

// a figure standing on a bubble's corner has its feet this share of its height inside the corner, over the bubble's padding rather than
// its words
const PERCH_INBOARD = 0.05;

// the corner each hand takes facing the viewer; the body hangs outside the bubble so it never covers its words
const HAND_CORNER = {l: "left", r: "right"};
const HANG_OUT = 0.3;
const TURNED_TO_THE_BUBBLE = 180;

// The perch a figure takes now on the bubbles of the floors snapshot `floors`, or null when no bubble in view has one free: the newest
// bubble first, as the thread keeps it in view while older ones scroll away, and on each the kind the pile draws first (pile.js perch), a
// hang only with a free hand, then the other. `hands` are the sides, "l" or "r", of the hands that carry nothing; `random` is a function
// returning 0 up to 1.
export function perchOn(floors, figure, hands, random) {
    const open = floors.floors.filter((floor) => floor.kind === "bubble" && inView(floor, floors.view, figure));
    const first = draw({moment: "perch", hands: hands.length > 0}, random).name;
    const kinds = !hands.length ? [STANDS] : first === HANGS ? [HANGS, STANDS] : [STANDS, HANGS];
    const perches = open.reverse().flatMap((floor) => kinds.map((kind) => perchAt(floor, kind, floors.view, hands)));
    return perches.find((perch) => perchSpot(perch, floors, figure)) ?? null;
}

// A perch of `kind` on a bubble's floor, on its side with more room. A hang there is by the hand on that side, facing the viewer; with
// only the other hand free it turns to face the bubble, as one hangs from a ledge facing the wall, so that hand comes to the corner.
function perchAt(floor, kind, view, hands) {
    const side = sideOf(floor, view);
    if (kind === STANDS) return {floor: floor.id, kind, side, grip: ""};
    const grip = hands.find((hand) => HAND_CORNER[hand] === side);
    return grip ? {floor: floor.id, kind, side, grip, face: 0} : {floor: floor.id, kind, side, grip: hands[0], face: TURNED_TO_THE_BUBBLE};
}

// Where the perch's figure stands now, with the way it faces, or null when its bubble is no floor of `floors` or out of the thread's view,
// when any part of the figure there would be outside its world, or when it would hide words or controls, such as those of the message above
export function perchSpot(perch, floors, figure) {
    const floor = floors.floors.find((each) => each.id === perch.floor);
    if (!floor || !inView(floor, floors.view, figure)) return null;
    const spot = spotOn(perch, floor, figure);
    return holds(spot, figure, floors.floors) && !hiddenAt(spot, figure) ? spot : null;
}

function spotOn(perch, floor, figure) {
    if (perch.kind === STANDS)
        return {...cornerAt({...floor, width: floor.right - floor.left}, perch.side, figure, PERCH_INBOARD), on: floor.element};
    const out = (perch.side === "left" ? -1 : 1) * HANG_OUT * figure.size;
    const x = (perch.side === "left" ? floor.left : floor.right) + out;
    return {x, y: floor.top, face: perch.face, posture: "hang", grip: perch.grip, on: floor.element};
}

// The floors a figure sits on the edge of, and how wide one must be, in the figure's heights, to have a place along it away from its ends
const LEDGES = new Set(["bubble", "dock", "compose"]);
export const LEDGE_WIDTH = 1.6;

// the places along a floor a figure sits on its edge, as shares of the way across, as the pile has them (pile.js ledge_at)
export const LEDGE_ALONG = PILE.filter((entry) => entry.when.moment === "ledge_at").map((entry) => entry.along);

// Where the figure sits on the edge of the floor it stands at, `near`, a bubble or the composer, facing the viewer with its legs over the
// edge: `along` of the way across it, or, where a figure sitting there would hide words or be outside its world, the next of LEDGE_ALONG
// that would not, never by an end; null when it stands on no such floor, the floor is too narrow, or no place along it is free
export function ledgeSpot(along, figure, near) {
    const floors = readFloors();
    const floor = floors.floors.find((each) => each.element && each.element === near.on && LEDGES.has(each.kind));
    if (!floor || floor.right - floor.left < LEDGE_WIDTH * figure.size) return null;
    const spots = [along, ...LEDGE_ALONG.filter((each) => each !== along)].map((share) => ({
        x: floor.left + (floor.right - floor.left) * share, y: floor.top, face: 0, posture: "sit", leans: true, on: floor.element,
    }));
    return spots.find((spot) => holds(spot, figure, floors.floors) && !hiddenAt(spot, figure)) ?? null;
}

// how long the figure keeps to the chat mark it went to celebrate on, in seconds
export const MARK_STAY = 20;

// Where the figure stands on the chat mark `card`, a message's key: on a corner of the bubble it is in, the side with more room first, or
// at home when it is docked over the compose box; null when it is not on the page or its bubble has no free stand
export function markSpot(card, figure) {
    const mark = document.querySelector(`[data-figure-mark="${CSS.escape(card)}"]`);
    if (!mark) return null;
    if (groundEdge().element?.contains(mark)) return spotOf(null, figure);
    const floors = readFloors();
    const floor = floors.floors.find((each) => each.kind === "bubble" && each.element.contains(mark));
    if (!floor) return null;
    const roomier = sideOf(floor, floors.view);
    const sides = [roomier, roomier === "left" ? "right" : "left"];
    return sides.map((side) => perchSpot({floor: floor.id, kind: STANDS, side, grip: ""}, floors, figure)).find(Boolean) ?? null;
}

// The footholds a figure with its feet at `from` hops onto to climb up to feet at height `y` (climbs.js climbStops): the corners of the
// bubbles in the thread's view on the way with a free stand, each a place it stands at; null when it cannot climb that high
export function climbOf(floors, figure, from, y) {
    const bubbles = floors.floors.filter((floor) => floor.kind === "bubble" && floor.top < from.y);
    const stands = bubbles.map((floor) => perchSpot({floor: floor.id, kind: STANDS, side: sideOf(floor, floors.view), grip: ""}, floors, figure)).filter(Boolean);
    return climbStops(from, y, stands, jumpMost(figure));
}

// the spot, when a figure at `near` can climb to it, else null
export const climbable = (spot, figure, near) => (spot && climbOf(readFloors(), figure, near, spot.y) ? spot : null);

// The next stay, drawn at `now` seconds from the pile: where, until when, and what it holds for the stay, the perch on a bubble, the
// tab it stands on, of those with a spot inside its world, or the point along the home edge it strolls to. A hang from a bubble is a short
// one.
export function nextStay(now, figure, hands, random, tally, free = false) {
    const {where, stay: seconds} = roamNext(random, tally, free);
    const until = now + seconds;
    if (where === "ledge") return {where, until, along: draw({moment: "ledge_at"}, random).along};
    if (where === "bubble") {
        const perch = perchOn(readFloors(), figure, hands, random);
        return {where, until: perch?.kind === HANGS ? now + between(HANG_STAY, random) : until, perch};
    }
    if (where === "tab") {
        const tabs = Object.keys(openTabs()).filter((view) => spotOf(view, figure));
        return {where, until, view: tabs[Math.floor(random() * tabs.length)]};
    }
    if (where === "edge") return {where, until, along: {x: random() * window.innerWidth, y: 0}};
    return {where, until};
}

// The spot of a stay now for a figure at `near`, or null when its bubble or tab is gone or its perch is no longer free; a tab it only
// visits is not one it points at
export function stayingAt(stay, figure, near) {
    if (stay.where === "bubble") {
        const spot = stay.perch && perchSpot(stay.perch, readFloors(), figure);
        return spot ? {...spot, view: null} : null;
    }
    if (stay.where === "tab") {
        const spot = stay.view && spotOf(stay.view, figure, near);
        return spot ? {...spot, view: null} : null;
    }
    if (stay.where === "edge") return spotOf(null, figure, stay.along);
    if (stay.where === "mark") return markSpot(stay.card, figure);
    if (stay.where === "ledge") return ledgeSpot(stay.along, figure, near);
    if (stay.where === "seat") return seatOf(figure, near) ?? restOf(figure, near);
    return restOf(figure, near);
}

// Where the figure goes now and the stay it keeps: onto the compose box's top to push a parcel it built onto the pile, where `work.x`
// says, or to build while its agent runs a command, beside the parcel it builds there or else clear of the pile (places.js buildSpot);
// resting at home while its agent cannot act; to the tab of what waits on the user when something does and that tab has a spot inside
// the figure's world; otherwise where its stay is, drawing the next stay when this one is over or its place is gone. `near` is where it
// is, `counts` the views' badge counts and `state` what the agent does. The spot is kept clear of the box the figure stepped aside from
// while that box is `cleared` (keptClear), except where it builds; resting by the parcel `pile`, it stands beside it (places.js besidePile).
export function targetFor({state, counts, stay, now, near, figure, hands, work = {}, pile = null, cleared = {until: 0}, random = Math.random, tally = null}) {
    const building = (work.x != null || builds(state)) && buildSpot(figure, near, work);
    if (building) return {spot: building, stay};
    const target = targetOf({state, counts, stay, now, near, figure, hands, random, tally});
    return {...target, spot: unlessClosing(besidePile(keptClear(target.spot, {state, now, near, figure, cleared}), pile, figure), near)};
}

// the spot, or null when it is on a docked card about to close by itself and the figure at `near` is not on it already: it never sets out
// for one, and one already on it may stay
const unlessClosing = (spot, near) => (spot?.on && spot.on !== near.on && spot.on === groundEdge().element && homeCloses() ? null : spot);

// whether the figure builds in `state`: its clip there is the hammering
export const builds = (state) => clipOf(state) === "work";

// The spot, or, while the box the figure stepped aside from is `cleared` and the spot's picture would cover it, one at home clear of it
export function keptClear(spot, {state, now, near, figure, cleared}) {
    if (now >= cleared.until || !overlaps(boxAt(spot, figure), cleared.box)) return spot;
    return clearOf(cleared.box, figure, near, RESTS.has(state)) ?? spot;
}

function targetOf({state, counts, stay, now, near, figure, hands, random, tally}) {
    if (RESTS.has(state)) return {spot: restOf(figure, near), stay};
    // at its laptop, while its agent edits, it sits on a corner where there is one
    const seat = clipOf(state) === "type" && seatOf(figure, near);
    if (seat) return {spot: seat, stay};
    const pressing = pointedView(counts, openTabs());
    const pointing = pressing && climbable(spotOf(pressing, figure, near), figure, near);
    if (pointing) return {spot: pointing, stay};
    const kept = now < stay.until && climbable(stayingAt(stay, figure, near), figure, near);
    if (kept) return {spot: kept, stay};
    const next = nextStay(now, figure, hands, random, tally, FREE.has(state));
    return {spot: climbable(stayingAt(next, figure, near), figure, near) || restOf(figure, near), stay: next};
}

// how long the box a figure stepped aside from stays clear of it, in seconds
export const CLEARED_SECONDS = 30;

// The stay and the cleared box once the figure steps out of the way, as when the user clicks it or a message appears under it: the stay is
// over, and `box`, the picture it was drawn in then, is kept clear of it for CLEARED_SECONDS
export const stepAside = (stay, box, now) => ({stay: {...stay, until: 0}, cleared: {box, until: now + CLEARED_SECONDS}});

// The stay once the ground went from under the figure: a stroll along the home edge or a rest there is kept, any stay away from home is
// given up for a rest
export const stayAtHome = (stay) => (stay.where === "edge" ? stay : {where: "rest", until: stay.where === "rest" ? stay.until : 0});

// The stay once a look comes: over at once when the figure hangs there with its back to the viewer, so it lets go and turns round to
// show it, else kept
export const stayForLook = (stay, place) => (letsGoFor(place) ? {...stay, until: 0} : stay);
