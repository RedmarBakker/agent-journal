// The mouse pointer tickling the figure: moved back and forth over it or within `reach` pixels round its body, so a move may overshoot it,
// turning `turns` times within `within` milliseconds, each move at least `least` pixels across to count, and kept up while the next move
// comes within `lingers` milliseconds of the last, wherever the pointer went meanwhile; it sets the figure off only once it has gone on
// `prolonged` milliseconds from its first turn back
export const TICKLE = {turns: 3, within: 1500, least: 6, lingers: 500, reach: 40, prolonged: 2000};

// whether the pointer at `x`, `y` on the page is over the figure's body `box` or within TICKLE.reach of it
export const nearBody = (box, x, y) =>
    x >= box.left - TICKLE.reach && x <= box.right + TICKLE.reach && y >= box.top - TICKLE.reach && y <= box.bottom + TICKLE.reach;

// the pointer as it was before any move over the figure: where across it last was, the way it went, 1 right or -1 left, the times it
// turned back, when it last moved, and when the stretch of tickling going on now first turned back, null with none
export const UNTICKLED = Object.freeze({x: 0, way: 0, turns: [], at: -Infinity, firstTurnAt: null});

// The pointer after a move to `x` across the page at `at` milliseconds, from how it was, `pointer`: a move too short to count keeps it as
// it was but for the time, and one the other way from the last counts a turn
export function movedTo(pointer, x, at) {
    if (pointer.at === -Infinity) return {x, way: 0, turns: [], at, firstTurnAt: null};
    const stretch = at - pointer.at <= TICKLE.lingers ? pointer.firstTurnAt : null;
    if (Math.abs(x - pointer.x) < TICKLE.least) return {...pointer, at, firstTurnAt: stretch};
    const way = Math.sign(x - pointer.x);
    const turned = pointer.way !== 0 && way !== pointer.way;
    const turns = [...pointer.turns.filter((time) => at - time <= TICKLE.within), ...(turned ? [at] : [])];
    return {x, way, turns, at, firstTurnAt: turned ? (stretch ?? at) : stretch};
}

// whether the pointer tickles the figure at `at`: turned back often enough of late, moving still, and kept up long enough
export const tickling = (pointer, at) =>
    pointer.turns.filter((time) => at - time <= TICKLE.within).length >= TICKLE.turns &&
    at - pointer.at <= TICKLE.lingers &&
    pointer.firstTurnAt !== null &&
    at - pointer.firstTurnAt >= TICKLE.prolonged;
