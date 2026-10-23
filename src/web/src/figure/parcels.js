import {draw} from "./pile.js";
import {VISOR} from "./visor.js";

// The parcels of code the figure builds on the compose box's top and the UFO that takes them once the work is committed, drawn by the page
// beside the figure (chat/CodeParcel.vue, chat/FlyingSaucer.vue). Every number that decides where they go and when is here, in pixels and
// milliseconds on the page.

// A parcel's drawing, a square block of `units` 1U server units stacked, drawn in 3D by the figure's own renderer and camera
// (figure.js serverBlockOf): `width` pixels wide and as deep, `height` pixels high with the strip of its top that shows, `top`; and how
// far inside either end of the floor one stands at least
export const PARCEL = {width: 24, height: 27, top: 3, units: 2, inside: 14};

// The colours the status lights shine in: amber while the run goes, and the visor's green and red once it has ended
export const LIGHT_COLOURS = {amber: [1, 0.69, 0.125], good: VISOR.colours.good, bad: VISOR.colours.bad};

// Amber lights blink, each out of step with the next: the blink is `phases` steps of `ms` each, a light on for half of them and dimmed to
// `dim` for the rest; green and red stay on
export const BLINK = {phases: 4, ms: 230, dim: 0.25};

// how bright the light numbered `index` on a unit's front is at step `phase` of the blink, with its lights `lit`
export const brightness = (lit, phase, index) => (lit !== "amber" || (phase + index) % BLINK.phases < BLINK.phases / 2 ? 1 : BLINK.dim);

// the steps of the blink a unit's lights `lit` show, one for lights that stay on
export const phasesOf = (lit) => (lit === "amber" ? BLINK.phases : 1);

// The status lights on a unit's front after a look: amber, blinking, from the moment a run `started`, and all green or red with the visor
// once a run has `ended` good or bad, kept so until the next run starts; `lit` is how they were
export const lightsAfter = (lit, started, ended) => ended || (started ? "amber" : lit);

// The 0 and 1 digits a blow's dust lets out, which drift in toward the unit as if bits were built into it: how many at least and at most,
// and how far from the unit's middle they start, in pixels, all above the floor
export const DIGITS = {least: 2, most: 4, from: [16, 28]};

// the digits of one blow at the roll `random()` gives, each its text and where it starts against the unit's base's middle; each drifts
// to the unit's front
export function digitsOf(random) {
    const count = DIGITS.least + Math.floor(random() * (DIGITS.most - DIGITS.least + 1));
    return Array.from({length: Math.min(count, DIGITS.most)}, () => {
        const way = -Math.PI / 2 + (random() - 0.5) * 2.4;
        const far = DIGITS.from[0] + random() * (DIGITS.from[1] - DIGITS.from[0]);
        return {text: draw({moment: "digit"}, random).name, x: Math.cos(way) * far, y: Math.min(Math.sin(way) * far, -4)};
    });
}

// The pile at the right end of the floor: blocks stacked `high` to a column, each on the top of the one under it, the columns going leftward from the end
export const PILE = {high: 3, gap: 1};

// where the parcel numbered `index` on the pile sits: `left` pixels from the floor's right end, its middle, and `up` above the floor
export function pileSlot(index) {
    const column = Math.floor(index / PILE.high);
    return {left: -(PARCEL.inside + PARCEL.width / 2 + column * (PARCEL.width + PILE.gap)), up: (index % PILE.high) * (PARCEL.height - PARCEL.top)};
}

// whether a run going on now builds a server unit, as the pile draws it (pile.js UNIT): nearly always, but one at most every few minutes,
// `memory` holding when the last was granted, at `now` in seconds
export const unitGranted = (memory, now, random) => draw({moment: "unit", memory, now}, random) !== null;

// how long the figure hammers each parcel, a random number of milliseconds between the two
export const HAMMER = {least: 3000, most: 8000};
export const hammerMs = (random) => HAMMER.least + random() * (HAMMER.most - HAMMER.least);

// how many blows have landed `frames` frames into a hammering whose blows are `blowFrames` frames long and land `lands` of the way through
export const blowsLanded = (frames, blowFrames, lands) => Math.max(Math.floor(frames / blowFrames - lands) + 1, 0);

// how far in front of its feet a pushing figure's hands meet the parcel's middle, and the room it leaves behind a parcel before pushing
export const PUSH = {reach: 22, room: 6};

// whether a figure with its feet at `feet` stands behind a parcel at `parcel`, on its left, so walking right pushes it
export const behind = (parcel, feet) => feet <= parcel - PUSH.reach + 2;

// Where the figure goes next to push a parcel at `parcel` onto the pile at `to`, its feet at `feet`, all page x: round behind the parcel
// first, then along to where the parcel meets the pile
export const pushStand = (parcel, to, feet) => (behind(parcel, feet) ? to - PUSH.reach : parcel - PUSH.reach - PUSH.room);

// Where a parcel at `parcel` is once a figure with its feet at `feet`, walking `way` (1 to the right, -1 to the left), has pushed it toward
// `to`: carried in front of the figure's hands while it walks right from behind it, never past `to`, and left where it is otherwise, as
// when the figure walks round it
export const pushedTo = (parcel, feet, to, way) =>
    way > 0 && feet < parcel && feet + PUSH.reach >= parcel - 2 ? Math.min(to, Math.max(parcel, feet + PUSH.reach)) : parcel;

// The UFO: the most its beam spans, so parcels further apart than that are taken one stop at a time; how far above the floor it hovers;
// and how long each part of its flight takes: flying in from far off, moving between stops, at each stop the beam coming on, the parcels
// rising up it and the beam going off, and flying away
export const UFO = {beamMost: 90, beamLeast: 34, hover: 150, enter: 1800, move: 900, beamOn: 300, lift: 1500, beamOff: 300, leave: 1800};

// The stops of a UFO taking `parcels` (each {id, x}): the parcels within one beam of each other taken together, left to right, each stop
// at their middle with a beam as wide as they lie
export function stopsOf(parcels) {
    const stops = [];
    for (const parcel of [...parcels].sort((a, b) => a.x - b.x)) {
        const last = stops.at(-1);
        if (last && parcel.x - last.left + PARCEL.width <= UFO.beamMost) {
            last.ids.push(parcel.id);
            last.right = parcel.x;
        } else stops.push({ids: [parcel.id], left: parcel.x, right: parcel.x});
    }
    return stops.map((stop) => ({...stop, x: (stop.left + stop.right) / 2, beam: Math.max(UFO.beamLeast, stop.right - stop.left + PARCEL.width + 8)}));
}

const STOP_MS = UFO.beamOn + UFO.lift + UFO.beamOff;

// how long a flight with `stops` stops lasts
export const flightMs = (stops) => UFO.enter + (stops - 1) * UFO.move + stops * STOP_MS + UFO.leave;

const ease = (k) => k * k * (3 - 2 * k);
const clamp = (k) => Math.min(Math.max(k, 0), 1);
const toward = (a, b, k) => ({x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k});

// Where the UFO is `ms` into its flight over `stops` (stopsOf), hovering UFO.hover pixels above the floor's top at `floor`, coming in
// `from` far off and going `away`: its middle; how strong its beam is, 0 to 1, and how wide; the stop it is at and how far up the beam
// that stop's parcels have risen, 0 to 1; how many stops it has taken; whether it is still coming in, before its first beam; and whether
// it is gone
export function ufoAt(stops, ms, floor, from, away) {
    const over = (stop) => ({x: stop.x, y: floor - UFO.hover});
    const still = {beam: 0, width: stops[0].beam, stop: 0, risen: 0, taken: 0, coming: false, gone: false};
    if (ms < UFO.enter) return {...still, ...toward(from, over(stops[0]), ease(ms / UFO.enter)), coming: true};
    let at = ms - UFO.enter;
    for (const [index, stop] of stops.entries()) {
        if (index > 0) {
            if (at < UFO.move) return {...still, ...toward(over(stops[index - 1]), over(stop), ease(at / UFO.move)), width: stop.beam, stop: index, taken: index};
            at -= UFO.move;
        }
        if (at < STOP_MS) {
            const beam = clamp(at / UFO.beamOn) * (1 - clamp((at - UFO.beamOn - UFO.lift) / UFO.beamOff));
            return {...still, ...over(stop), beam, width: stop.beam, stop: index, risen: ease(clamp((at - UFO.beamOn) / UFO.lift)), taken: index};
        }
        at -= STOP_MS;
    }
    const k = clamp(at / UFO.leave);
    return {...still, ...toward(over(stops.at(-1)), away, k * k), stop: stops.length - 1, risen: 1, taken: stops.length, gone: k >= 1};
}

// The claw crane, as an arcade's claw machine: it rolls in along the chat window's top edge, stops over each stack, lowers its claw on a
// chain, closes it on the stack and lifts it up out of the window, then rolls out at the far side. How long each part takes, in
// milliseconds; how short the chain is when it is wound up, in pixels; and how far past the window's top a stack is lifted
export const CRANE = {enter: 1700, move: 900, lower: 1000, grab: 400, lift: 1400, leave: 1500, wound: 10, clear: 30};

const CRANE_STOP_MS = CRANE.lower + CRANE.grab + CRANE.lift;

// how long a crane's visit to `stops` stops lasts
export const craneMs = (stops) => CRANE.enter + (stops - 1) * CRANE.move + stops * CRANE_STOP_MS + CRANE.leave;

// the chain a claw at the window's `top` needs to reach down onto `stop`'s stack, standing on the floor at `floor`, in pixels
const reachOf = (stop, floor, top) => floor - top - stop.high;

// Where the crane is `ms` into its visit to `stops` (stopsOf, each with `high`, its stack's height), its rail along the window's top at
// `top` over a floor at `floor`, rolling in at `from` and out at `away`, all page x: its trolley's x; its chain's length down from the rail,
// below the window's top when it is less than nothing; how open its claw is, 1 wide open and 0 shut on a stack; the stop it is at and how
// far its stack has been lifted from the floor, in pixels; how many stops it has taken; and whether it is still coming in, or gone
export function craneAt(stops, ms, floor, top, from, away) {
    const still = {chain: CRANE.wound, open: 1, stop: 0, lifted: 0, taken: 0, coming: false, gone: false};
    if (ms < CRANE.enter) return {...still, x: from + (stops[0].x - from) * ease(ms / CRANE.enter), coming: true};
    let at = ms - CRANE.enter;
    for (const [index, stop] of stops.entries()) {
        if (index > 0) {
            if (at < CRANE.move) {
                const k = ease(at / CRANE.move);
                return {...still, x: stops[index - 1].x + (stop.x - stops[index - 1].x) * k, chain: windingIn(stops[index - 1], k), stop: index, taken: index};
            }
            at -= CRANE.move;
        }
        if (at < CRANE_STOP_MS) {
            const reach = reachOf(stop, floor, top);
            const lowered = ease(clamp(at / CRANE.lower));
            const shut = clamp((at - CRANE.lower) / CRANE.grab);
            const lift = ease(clamp((at - CRANE.lower - CRANE.grab) / CRANE.lift));
            const out = -(stop.high + CRANE.clear);
            const chain = lift > 0 ? reach + (out - reach) * lift : CRANE.wound + (reach - CRANE.wound) * lowered;
            return {...still, x: stop.x, chain, open: 1 - shut, stop: index, lifted: reach - chain > 0 && lift > 0 ? reach - chain : 0, taken: index};
        }
        at -= CRANE_STOP_MS;
    }
    const k = clamp(at / CRANE.leave);
    return {...still, x: stops.at(-1).x + (away - stops.at(-1).x) * k * k, chain: windingIn(stops.at(-1), ease(k)), stop: stops.length - 1, taken: stops.length, gone: k >= 1};
}

// the chain wound back in, `k` of the way, from up past the window's top where it lifted `stop`'s stack out to its wound length
const windingIn = (stop, k) => -(stop.high + CRANE.clear) + (CRANE.wound + stop.high + CRANE.clear) * k;

// The stacks the crane takes from `parcels` (each {id, x, up}): the stops of stopsOf, each with `high`, its stack's height in pixels
export const stacksOf = (parcels) =>
    stopsOf(parcels).map((stop) => ({...stop, high: Math.max(...parcels.filter((each) => stop.ids.includes(each.id)).map((each) => each.up)) + PARCEL.height}));
