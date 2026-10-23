import {BODY} from "./places.js";

// The highest the figure jumps, in its own heights from its hat to its feet, for every avatar; only the pogo stick goes higher
export const JUMP = {most: 2.5};

// how tall a figure ({size, below}) stands, from its hat to its feet, in pixels
export const heightOf = ({size, below}) => (1 - below - BODY.top) * size;

// how far up one jump of a figure goes at most, in pixels
export const jumpMost = (figure) => JUMP.most * heightOf(figure);

// The pogo stick takes the figure up a climb past `over` of its heights, now and then, as high as `most` of them in one go
export const POGO = {over: 3, most: 6};

// whether a climb of `height` pixels is one for the pogo stick: past its `over` and within its `most`
export const pogoClimb = (figure, height) => height > POGO.over * heightOf(figure) && height <= POGO.most * heightOf(figure);

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
