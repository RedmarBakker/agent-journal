import {BODY} from "./places.js";

// The highest the figure jumps, in its own heights from its hat to its feet, for every avatar; only the pogo stick goes higher
export const JUMP = {most: 2.5};

// how far up one jump of a figure ({size, below}) goes at most, in pixels
export const jumpMost = ({size, below}) => JUMP.most * (1 - below - BODY.top) * size;

// The footholds a climb from the feet at `from` up to feet at height `y` hops onto, of those in `holds` (feet {x, y}), each hop no higher
// than `most`: as many hops as the height needs, each onto the highest foothold in reach, until `y` itself is in reach; null when a gap on
// the way is too high to hop
export function climbStops(from, y, holds, most) {
    const stops = [];
    let at = from;
    while (at.y - y > most) {
        const reach = holds.filter((hold) => hold.y < at.y && hold.y > y && at.y - hold.y <= most);
        if (!reach.length) return null;
        at = reach.reduce((best, hold) => (hold.y < best.y ? hold : best));
        stops.push(at);
    }
    return stops;
}
