import {GRAVITY} from "../domain/falls.js";
import {SKYWARD} from "./skyward.js";

// The figure handled with the pointer. Its head, pressed and dragged across, tilts with the pointer `pull` degrees a pixel up to `tilt`
// degrees either way, the head being the picture above `neck` of it under the eyes. Its body, pressed `hold` seconds, is lifted and
// dangles under the pointer; let go, it flies off at the pointer's speed over its last `sampled` seconds, never faster than `fastest`
// pixels a second, tumbling `spin` degrees a second and off the walls keeping `bounce` of its speed, until its parachute opens, `tumble`
// seconds after the throw or once it falls to within `open` of its heights above its perch; under the canopy it sinks at the parachute's
// speed (skyward.js SKYWARD chute) and is steered no faster than `steer` of its heights a second across onto its perch, the tumble
// righting itself `righting` times a second.
export const GRAB = {tilt: 30, pull: 0.6, neck: 0.06, hold: 0.25, sampled: 0.1, fastest: 3000, spin: 900, bounce: 0.5, tumble: 0.9, open: 1.5, steer: 4, righting: 10};

// the longest step the flight takes at once, in seconds, so a frame missed while the tab was away does not carry it through a wall
const LONGEST_STEP = 0.05;

const clamp = (value, least, most) => Math.min(Math.max(value, least), most);

// whether a press at `point`, as shares of the picture, is on the head, whose eyes are at `head`: anything above the neck
export const onHead = (point, head) => point.y <= head.y + GRAB.neck;

// how far the head tilts, in degrees, for a drag `across` pixels to the right of where it was pressed: with the pointer, never past GRAB.tilt
export const headTiltFor = (across) => clamp(across * GRAB.pull, -GRAB.tilt, GRAB.tilt);

// The clock of the act on screen, which `started` at, once the head held from `began` is let go at `released`, in milliseconds: it goes on
// from the frame it stood still on, the time held never counted
export const resumedClock = (started, began, released) => started + (released - began);

// The pointer's speed at `now` from its `moves` ({x, y, at} in pixels and seconds, oldest first), in pixels a second: over its moves of the
// last GRAB.sampled seconds, none when it has not moved in that time, never faster than GRAB.fastest
export function pointerSpeed(moves, now) {
    const recent = moves.filter((move) => now - move.at <= GRAB.sampled);
    if (recent.length < 2) return {x: 0, y: 0};
    const [first, last] = [recent[0], recent.at(-1)];
    const seconds = Math.max(last.at - first.at, 1e-3);
    const [x, y] = [(last.x - first.x) / seconds, (last.y - first.y) / seconds];
    const scale = Math.min(1, GRAB.fastest / Math.max(Math.hypot(x, y), 1e-9));
    return {x: x * scale, y: y * scale};
}

// The figure let go with its feet at `feet` at `speed` ({x, y} pixels a second, down is more), at `now` in milliseconds: in the air,
// tumbling, its parachute still shut
export const thrownFrom = (feet, speed, now) => ({x: feet.x, y: feet.y, posture: "stand", face: 0, vx: speed.x, speed: speed.y, at: now, began: now, spin: 0, chute: false, thrown: true});

// One frame of a throw at `now` toward `perch`, its spot, for a figure `size` pixels high whose feet keep inside `room` ({left, right,
// top, bottom}): the throw stepped on, tumbling and then under its canopy; or, once it lands, null with the perch it landed on; or, when
// the parachute opens below the perch, `lost`, to come down on it to whatever is under it
export function thrownFrame(thrown, perch, room, size, now) {
    const seconds = Math.min((now - thrown.at) / 1000, LONGEST_STEP);
    const opens = !thrown.chute && ((now - thrown.began) / 1000 >= GRAB.tumble || (thrown.speed > 0 && thrown.y >= perch.y - GRAB.open * size));
    if (opens && thrown.y > perch.y) return {airborne: {...thrown, at: now}, landed: null, lost: true};
    const next = thrown.chute || opens ? floated(thrown, perch, size, seconds) : tumbled(thrown, room, seconds);
    const landed = next.chute && next.y >= perch.y && Math.abs(next.x - perch.x) <= 0.5;
    if (landed) return {airborne: null, landed: perch, lost: false};
    return {airborne: {...next, at: now}, landed: null, lost: false};
}

// the throw `seconds` on while it tumbles: under gravity, turning the way it flies across, off the walls, the top and the bottom of `room`
function tumbled(thrown, room, seconds) {
    const vy = thrown.speed + GRAVITY * seconds;
    const [x, y] = [thrown.x + thrown.vx * seconds, thrown.y + vy * seconds];
    const across = x < room.left || x > room.right ? -thrown.vx * GRAB.bounce : thrown.vx;
    const down = y < room.top || y > room.bottom ? -vy * GRAB.bounce : vy;
    const spin = thrown.spin + (Math.sign(thrown.vx) || 1) * GRAB.spin * seconds;
    return {...thrown, x: clamp(x, room.left, room.right), y: clamp(y, room.top, room.bottom), vx: across, speed: down, spin};
}

// a turn of `spin` degrees as the least turn from upright, either way
const upright = (spin) => ((((spin + 180) % 360) + 360) % 360) - 180;

// the throw `seconds` on under its canopy: sinking no faster than the parachute lets it, steered across to arrive over `perch` as it
// reaches the perch's line, and held on that line until it is over it, the tumble righting itself
function floated(thrown, perch, size, seconds) {
    const sink = SKYWARD.chute * size;
    const vy = Math.min(thrown.speed + GRAVITY * seconds, sink);
    const left = Math.max((perch.y - thrown.y) / sink, seconds);
    const steer = GRAB.steer * size;
    const vx = clamp((perch.x - thrown.x) / left, -steer, steer);
    const x = Math.abs(perch.x - thrown.x) <= Math.abs(vx * seconds) ? perch.x : thrown.x + vx * seconds;
    const y = Math.min(thrown.y + vy * seconds, perch.y);
    return {...thrown, x, y, vx, speed: vy, chute: true, spin: upright(thrown.spin) * Math.max(1 - GRAB.righting * seconds, 0)};
}
