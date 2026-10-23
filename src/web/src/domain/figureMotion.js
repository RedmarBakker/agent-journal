import {ACTS, pogoBounces, pogoHop} from "../figure/acts.js";
import {draw} from "../figure/pile.js";
import {fallStep} from "./falls.js";

// How far, in pixels, a figure's feet may be from a floor's top and still stand on it: a floor that moves away under the figure must move
// further than this before it falls, so a pixel or two of the page shifting never drops it
export const ON_FLOOR = 5;

const holds = (floor, x) => x >= floor.left && x <= floor.right;

// How far a walker's feet may be from a floor's top and still keep to it, as when the floor moved while the figure got up to go: it is
// carried onto that floor's top, or falls to it
export const KEPT_WITHIN = 8;

// The floor nearest a figure's feet at `x`, `y` within `within` pixels of them, or null when the snapshot holds none so near
export const floorAt = (floors, x, y, within = ON_FLOOR) =>
    floors
        .filter((floor) => holds(floor, x) && Math.abs(floor.top - y) <= within)
        .sort((a, b) => Math.abs(a.top - y) - Math.abs(b.top - y))[0] ?? null;

// The highest floor under a figure's feet at `x`, `y`: never one the feet were already below
export const floorBelow = (floors, x, y, reach = ON_FLOOR) =>
    floors.filter((floor) => holds(floor, x) && floor.top >= y - reach).sort((a, b) => a.top - b.top)[0] ?? null;

// At the top of a jump, the one frame the figure stops rising and would fall, a floor whose top is this many pixels above its feet at
// most is close enough to land on, so a jump that misses an edge by a hair lands instead of falling back to try again; the figure hangs
// there this many frames and lands only if the floor is still that close then, so a page still settling is never landed on.
export const SNAP_WITHIN = 5;
export const SNAP_WAIT_FRAMES = 3;

// The floors at home, the only ones that throw a figure up or let it drop: anywhere else a floor that moves, as a bubble the chat scrolls,
// carries the figure with it
export const HOME_FLOORS = ["dock", "compose", "foot"];

// What became of the floor a walker set off on: gone, or a home floor dropped away under its feet, so it falls; or still there, `dy`
// pixels above or below the line it walks and `dx` pixels to bring it back inside a floor that narrowed past its feet, which carry it
export function underWalker(floors, id, x, y) {
    const floor = floors.find((each) => each.id === id);
    if (!floor || (HOME_FLOORS.includes(floor.kind) && floor.top > y + ON_FLOOR)) return {falls: true, dx: 0, dy: 0};
    return {falls: false, dx: Math.min(Math.max(x, floor.left), floor.right) - x, dy: floor.top - y};
}

// The floors a fall can end on: every floor when the figure lets a bubble catch it, else only the floors at home (the user's ruling: it is
// up to the avatar, fall by fall)
export const catching = (floors, bubblesCatch) => (bubblesCatch ? floors : floors.filter((floor) => HOME_FLOORS.includes(floor.kind)));

// The share of the way a leg with `easing` has gone at `share` of its time: as the browser eases a transition, so a CSS cubic-bezier
// steps the same in code; "linear" or any other easing goes at an even pace
export function eased(easing, share) {
    const curve = /^cubic-bezier\(([^)]*)\)$/.exec(easing ?? "");
    if (!curve || share <= 0 || share >= 1) return Math.min(1, Math.max(0, share));
    const [x1, y1, x2, y2] = curve[1].split(",").map(Number);
    const along = (t, a, b) => 3 * (1 - t) * (1 - t) * t * a + 3 * (1 - t) * t * t * b + t * t * t;
    let [low, high] = [0, 1];
    for (let step = 0; step < 30; step++) {
        const t = (low + high) / 2;
        if (along(t, x1, x2) < share) low = t;
        else high = t;
    }
    return along((low + high) / 2, y1, y2);
}

// Whether a leg that set off at `began` has run its lead and its course by `now`
export const legEnded = (leg, began, now) => now - began >= leg.lead + leg.ms;

// Where a leg under way has carried the picture `elapsed` milliseconds after it set off from `from`: still at the start through the
// leg's lead, then along it by the leg's easing to its end; with motion kept `still`, a hop is at its end at once
export function legAt(leg, from, elapsed, still = false) {
    if (leg.pogo && !still) return pogoAt(leg, from, elapsed);
    const share = still && leg.hopping ? 1 : eased(leg.easing, leg.ms > 0 ? (elapsed - leg.lead) / leg.ms : 1);
    return {x: from.x + (leg.x - from.x) * share, y: from.y + (leg.y - from.y) * share};
}

// Where a leg up on the pogo stick (acts.js pogo) has carried the picture `elapsed` milliseconds after it set off from `from`, its picture
// `leg.size` pixels tall: still while the stick is drawn, bouncing on the spot higher each time, then springing up in one throw to its top
// past the leg's end by `over` of its height, where it lets the stick go, and falling from there onto the leg's end on its own feet, staying
// there; one gravity times every hop, the rise and the fall (acts.js pogoHop), so it slows to each top and falls faster each time
export function pogoAt(leg, from, elapsed) {
    const {bounces, spring, over} = ACTS.pogo;
    const u = Math.min(Math.max(elapsed / leg.ms, 0), 1);
    const span = (range) => Math.min(Math.max((u - range[0]) / (range[1] - range[0]), 0), 1);
    if (u < spring[0]) return {x: from.x, y: from.y - pogoHop(pogoBounces(), span(bounces)).height * leg.size};
    const past = over * leg.size;
    const rise = Math.max(from.y - leg.y, 0) + past;
    const peak = leg.y - past;
    const falls = pogoFall(leg, from);
    const across = from.x + (leg.x - from.x) * span([spring[0], falls[1]]);
    if (u < spring[1]) return {x: across, y: peak + rise * (1 - span(spring)) ** 2};
    return {x: across, y: peak + past * span(falls) ** 2};
}

// the share of a pogo leg's act (acts.js pogo) its fall from the throw's top onto the leg's end takes, from where it lets the stick go
// until it lands: as long against the rise as the square root of its height against the rise's, as under one gravity
export function pogoFall(leg, from) {
    const {spring, over} = ACTS.pogo;
    const past = over * leg.size;
    const rise = Math.max(from.y - leg.y, 0) + past;
    return [spring[1], spring[1] + (spring[1] - spring[0]) * Math.sqrt(past / rise)];
}

// One frame of a figure falling from `body` (its feet line and speed) to the floor under it, `seconds` after the last: it lands on that
// floor the moment it touches, with the floor it landed on, and falls to the window's foot when nothing else is under it; with motion
// kept `still`, it is on that floor at once
export function fallFrame(body, floors, seconds, still = false) {
    const peak = peakFrame(body, floors);
    if (peak) return peak;
    const floor = floorBelow(floors, body.x, body.y, 0);
    if (!floor) return {...body, landed: null};
    if (floor.top < body.y) return {x: body.x, y: floor.top, speed: 0, landed: floor};
    if (still) return {x: body.x, y: floor.top, speed: 0, landed: floor};
    const step = fallStep({y: body.y, speed: body.speed}, floor.top, seconds, body.most);
    return {x: body.x, y: step.y, speed: step.speed, landed: step.landed ? floor : null};
}

// The floor just above a figure's feet at the top of its jump: one whose top is SNAP_WITHIN pixels above them at most
const shelfAbove = (floors, x, y) => floors.filter((floor) => holds(floor, x) && floor.top < y && y - floor.top <= SNAP_WITHIN).sort((a, b) => b.top - a.top)[0] ?? null;

// The top of a jump, a fall's first frame (no speed yet, `peak` not set): with a shelf just above the feet the figure hangs for
// SNAP_WAIT_FRAMES frames, then lands on the shelf if it is still that close, else falls on; with none, or once the wait is over, null,
// and the fall goes on as any other
function peakFrame(body, floors) {
    if (body.peak === 0 || (body.peak === undefined && body.speed)) return null;
    const shelf = shelfAbove(floors, body.x, body.y);
    if (body.peak === undefined) return shelf ? {...body, peak: SNAP_WAIT_FRAMES, landed: null} : null;
    if (body.peak > 1) return {...body, peak: body.peak - 1, landed: null};
    return shelf ? {x: body.x, y: shelf.top, speed: 0, peak: 0, landed: shelf} : {...body, peak: 0, landed: null};
}

// A trip re-aimed at where its destination is now, `landed`: the legs that end on the destination's line, and the leg under way among
// them, `leg`, carried with it, and `from`, where that leg set off, moved along with it, so a hop stays upright and lands on the ground
// where it is rather than where it was
export function aimedAt(trip, leg, from, landed) {
    const dx = landed.x - trip.to.x;
    const dy = landed.y - trip.to.y;
    if (Math.hypot(dx, dy) <= 0.3) return {trip, leg, from};
    const end = (trip.legs.at(-1) ?? leg).y;
    const carried = (each) => (each.y === end ? {...each, x: each.x + dx, y: each.y + dy} : each);
    const under = leg.y === end;
    return {
        trip: {...trip, to: landed, legs: trip.legs.map(carried)},
        leg: under ? carried(leg) : leg,
        from: under ? {...from, x: from.x + dx} : from,
    };
}

// How far the squire's chase may run, out to its right and back: as far as `most` pixels along the floor under its feet, never past that
// floor's right end or the right of its world, so it never runs into the air; nothing when it stands on no floor
export function chaseRoom(floors, world, feet, picture, most) {
    const floor = floorAt(floors, feet.x, feet.y, KEPT_WITHIN);
    if (!floor) return 0;
    return Math.max(0, Math.min(most, floor.right - feet.x, world.right - picture.right));
}

// whether a bubble a figure falls past catches it, rather than its dropping straight home, as the pile draws it (pile.js fall): never
// for a fall that comes soon after another, `settled` false, so a fall onto a bubble that then goes from under it never chains on
export const catches = (settled, random) => draw({moment: "fall", settled}, random).name === "caught";

// A fall from the line a figure rests on at `spot`, in its posture there and turned the way it faces there, starting at `now`: never from
// below the floor at home, going on to `to` once it lands, and caught by a bubble it falls past when the pile draws so
export function fallingFrom(spot, to, floors, now, random, settled) {
    const home = floors.find((floor) => floor.id === "home");
    const y = home ? Math.min(spot.y, home.top) : spot.y;
    return {x: spot.x, y, posture: spot.posture, face: spot.face, speed: 0, at: now, to, catches: catches(settled, random)};
}

// A parachute's descent from `top`, above the screen, at `x`, starting at `now`: a fall no faster than `most` pixels a second, caught by a
// bubble it comes down past when `random()` says so
export const chuteFrom = (x, top, most, now, random) => ({x, y: top, posture: "stand", speed: 0, at: now, to: null, catches: catches(true, random), most, chute: true});

// One frame of a fall at `now` (fallFrame): the fall stepped on, or, once it lands, null with the spot it settles on in the posture it
// fell in and turned as it was, where it goes on to and whether it landed on its feet
export function airborneFrame(airborne, floors, now, still = false) {
    const fell = fallFrame(airborne, catching(floors, airborne.catches), (now - airborne.at) / 1000, still);
    if (!fell.landed) return {airborne: {...airborne, ...fell, at: now}, landed: null};
    const spot = {x: fell.x, y: fell.landed.top, posture: airborne.posture, face: airborne.face, view: null, on: fell.landed.element ?? null};
    return {airborne: null, landed: {spot, to: airborne.to, standing: airborne.posture === "stand"}};
}

// the ease a change of posture slides the picture by, as CSS's ease-in-out
const SLIDE_EASING = "cubic-bezier(0.42, 0, 0.58, 1)";

// Where a picture sliding from `slide.from` to `slide.to` since `slide.began` is at `now`, over `ms`, and whether it has got there
export function slideAt(slide, now, ms) {
    const share = Math.min(1, Math.max(0, (now - slide.began) / ms));
    const along = eased(SLIDE_EASING, share);
    return {
        at: {x: slide.from.x + (slide.to.x - slide.from.x) * along, y: slide.from.y + (slide.to.y - slide.from.y) * along},
        done: share >= 1,
    };
}

// The legs of a trip, or any points of one, moved by dx and dy, as the floor the figure waits on to set off moves under it
export const liftedLegs = (legs, dx, dy) => legs.map((each) => ({...each, x: each.x + dx, y: each.y + dy}));
