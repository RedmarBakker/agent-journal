// The mouse pointer tickling the figure: moved back and forth over it, turning `turns` times within `within` milliseconds, each move at
// least `least` pixels across to count, and kept up while the next move comes within `lingers` milliseconds of the last
export const TICKLE = {turns: 3, within: 1500, least: 6, lingers: 500};

// the pointer as it was before any move over the figure: where across it last was, the way it went, 1 right or -1 left, the times it
// turned back and when it last moved
export const UNTICKLED = Object.freeze({x: 0, way: 0, turns: [], at: -Infinity});

// The pointer after a move to `x` across the page at `at` milliseconds, from how it was, `pointer`: a move too short to count keeps it as
// it was but for the time, and one the other way from the last counts a turn
export function movedTo(pointer, x, at) {
    if (pointer.at === -Infinity) return {x, way: 0, turns: [], at};
    if (Math.abs(x - pointer.x) < TICKLE.least) return {...pointer, at};
    const way = Math.sign(x - pointer.x);
    const turned = pointer.way !== 0 && way !== pointer.way;
    return {x, way, turns: [...pointer.turns.filter((time) => at - time <= TICKLE.within), ...(turned ? [at] : [])], at};
}

// whether the pointer tickles the figure at `at`: turned back often enough of late, and moving still
export const tickling = (pointer, at) =>
    pointer.turns.filter((time) => at - time <= TICKLE.within).length >= TICKLE.turns && at - pointer.at <= TICKLE.lingers;
