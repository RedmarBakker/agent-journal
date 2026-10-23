// The parcels of code the figure builds on the compose box's top and the UFO that takes them once the work is committed, drawn by the page
// beside the figure (chat/CodeParcel.vue, chat/FlyingSaucer.vue). Every number that decides where they go and when is here, in pixels and
// milliseconds on the page.

// a parcel's drawing, and how far inside either end of the floor one stands at least
export const PARCEL = {width: 24, height: 19, inside: 14};

// The pile at the right end of the floor: parcels stacked `high` to a column, the columns going leftward from the end
export const PILE = {high: 3, gap: 1};

// where the parcel numbered `index` on the pile sits: `left` pixels from the floor's right end, its middle, and `up` above the floor
export function pileSlot(index) {
    const column = Math.floor(index / PILE.high);
    return {left: -(PARCEL.inside + PARCEL.width / 2 + column * (PARCEL.width + PILE.gap)), up: (index % PILE.high) * (PARCEL.height - 2)};
}

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
