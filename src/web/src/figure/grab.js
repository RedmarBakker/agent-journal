import {fallFrame} from "../domain/figureMotion.js";

// The figure handled with the pointer. Its head, pressed and dragged across, tilts with the pointer `pull` degrees a pixel up to `tilt`
// degrees either way, the head being the picture above `neck` of it under the eyes. Its body, pressed `hold` seconds, is lifted and
// dangles under the pointer; let go, it flies off at the pointer's speed over its last `sampled` seconds, never faster than `fastest`
// pixels a second, tumbling `spin` degrees a second and off the chat's sides keeping `bounce` of its speed across, and falls from where it
// is let go to the nearest floor below; thrown up past the chat's top it flies on freely, out of sight, and is gone off the screen once
// its feet are `away` pixels above that top, to come back from above.
export const GRAB = {tilt: 30, pull: 0.6, neck: 0.06, hold: 0.25, sampled: 0.1, fastest: 3000, spin: 900, bounce: 0.5, away: 500};

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
// tumbling as it flies, falling from there
export const thrownFrom = (feet, speed, now) => ({x: feet.x, y: feet.y, posture: "stand", face: 0, vx: speed.x, speed: speed.y, at: now, spin: 0, peak: 0, thrown: true});

// One frame of a throw at `now` over the `floors`, its feet kept between the chat's sides `room.left` and `room.right`: the throw flown on
// across and falling as any fall does (figureMotion.js fallFrame), off the sides; once it lands on the nearest floor below where it comes
// down, a bubble's top or the chat's floor, null with the spot it landed on, standing; and `gone` once it rises GRAB.away pixels past
// `room.top`, the chat's top, nothing stopping it on the way, out of sight above the chat
export function thrownFrame(thrown, floors, room, now) {
    const seconds = Math.min((now - thrown.at) / 1000, LONGEST_STEP);
    const across = thrown.x + thrown.vx * seconds;
    const off = across < room.left || across > room.right;
    const x = clamp(across, room.left, room.right);
    const {landed, ...fell} = fallFrame({...thrown, x}, floors, seconds);
    if (landed) return {airborne: null, landed: {x, y: landed.top, posture: "stand", face: 0, view: null, on: landed.element ?? null}, gone: false};
    const spin = thrown.spin + (Math.sign(thrown.vx) || 1) * GRAB.spin * seconds;
    const airborne = {...thrown, ...fell, x, vx: off ? -thrown.vx * GRAB.bounce : thrown.vx, spin, at: now};
    return {airborne, landed: null, gone: airborne.speed < 0 && airborne.y <= room.top - GRAB.away};
}
