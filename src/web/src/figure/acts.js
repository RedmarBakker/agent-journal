// The journal moments and the searches the figure acts out with things the page draws beside it (chat/FigureAct.vue): for each act its
// length, unless it plays a clip of figure.js's own, and the shares of its clip over which each of its parts plays, read alike by the clip
// that moves the body (figure.js) and by the page that draws what it holds, so the hand and the thing in it never part.
export const ACTS = {
    // a celebration: it jumps for joy `jumps` times with its arms flung up, each jump a little lower than the last
    joy: {frames: 50, fps: 14, jumps: 5},
    // a worker sent off or another session messaged: a call on an old desk telephone (figure.js TELEPHONE). The telephone appears on the
    // floor before it, whole, in a poof of smoke over `poof`, `above` its units over the floor, drops onto it over `drop` and settles with
    // a jiggle over `settle`, squashing `squash` flat as it lands and wobbling `wobbles` times to still (figure.js phoneArrival), its handset
    // resting on the cradle a moment; it bends to the handset over `reach` and lifts it to its ear over `lift`; it bends to the dial and
    // puts a finger in it over `finger`, turns it `turn` degrees round to the stop over `dial`, and the dial springs back over `back`; it
    // talks over `talk`, nodding `nods` times; it bends to put the handset back on the cradle over `hang`, stands back from it a moment, and the telephone goes in a poof over `goes`
    // While it talks and until the handset is down it says whom it calls in a speech bubble beside its head (figure/places.js callSays)
    phone_call: {frames: 108, fps: 12, poof: [0, 0.06], above: 0.7, drop: [0.015, 0.055], settle: [0.055, 0.12], squash: 0.24, wobbles: 3, reach: [0.13, 0.2], lift: [0.2, 0.28], finger: [0.28, 0.33], dial: [0.33, 0.42], turn: 250, back: [0.42, 0.5], talk: [0.5, 0.72], nods: 3, hang: [0.72, 0.84], goes: [0.92, 1]},
    // a question asked: it raises a sign with a question mark on a stick over its head and waggles it
    ask_sign: {frames: 42, fps: 12, raise: [0, 0.22], waggle: [0.22, 0.78], waggles: 3, lower: [0.78, 1]},
    // a report: it brings the rolled scroll up before its chest over `raise`, a roller in each hand, the free hand's on top; pulls the
    // rollers apart over `unrolls`, the written side toward itself and the parchment's plain back to the viewer (figure.js SCROLL); reads
    // it `lines` lines down, its head going slowly along each; rolls it closed between its hands over `rolls` and lowers it over `lower`
    scroll: {frames: 96, fps: 12, raise: [0, 0.09], unrolls: [0.09, 0.22], rolls: [0.85, 0.93], lower: [0.93, 1], lines: 3},
    // a task finished, a job well done: it brings its hands together before its chest over `together`, rubs them round each other
    // `rubs` times, nodding a little with each, and lowers them over `apart`; a small puff with a few sparkles rises from the hands over
    // `puff` (chat/FigureAct.vue)
    hand_rub: {frames: 26, fps: 12, together: [0, 0.18], rubs: 3, apart: [0.84, 1], puff: [0.2, 0.92]},
    // stopping to think at the laptop (figure.js type_ponder), under the thought cloud, its dots pulsing three times a loop
    type_ponder: {frames: 24, fps: 6, pulse: 4 / 3},
    // The thinking act, now and then while the agent thinks (figure.js thinkingClip, reactions.js thinkingAct), in its three plays. With
    // the cloud: it raises its finger to its cheek over `into`, tilting its head up, swaying `sways` times; three puffs rise from its head
    // over `puffs` into a small thought cloud over it, held over `cloud`, its three dots pulsing one after another, `pulse` seconds round
    // (chat/FigureAct.vue), and over `rise` its hand comes away. With the bulb: over `rise` the finger comes up, "got it", the light bulb
    // over the head (figure.js LIGHT_BULB) appears over `appears`, switches on over `lights`, glows, goes out over `fades` and is gone over
    // `goes`. "ponder" has both, the bulb at its end; "think_cloud" the cloud alone, its hand going down; "got_it" the bulb alone.
    ponder: {frames: 84, fps: 12, into: [0, 0.1], puffs: [0.06, 0.24], cloud: [0.06, 0.72], pulse: 1.2, sways: 2, rise: [0.72, 0.8], appears: [0.75, 0.78], lights: [0.79, 0.82], fades: [0.9, 0.96], goes: [0.95, 1]},
    think_cloud: {frames: 66, fps: 12, into: [0, 0.12], puffs: [0.07, 0.29], cloud: [0.07, 0.86], pulse: 1.2, sways: 2, rise: [0.86, 1]},
    got_it: {frames: 30, fps: 12, rise: [0, 0.25], appears: [0.05, 0.15], lights: [0.18, 0.26], fades: [0.72, 0.88], goes: [0.86, 1]},
    // a fact or a reminder: a small cabinet grows beside it, its drawer slides out, it files a card in it and the drawer shuts
    file_card: {frames: 42, fps: 12, grows: [0, 0.15], opens: [0.12, 0.28], reach: [0.2, 0.44], filed: [0.44, 0.56], back: [0.56, 0.72], shuts: [0.58, 0.72], sinks: [0.86, 1]},
    // searching: binoculars at its eyes, sweeping slowly left and right
    binoculars: {frames: 80, fps: 10, sweep: 1},
    // searching with a torch (figure.js flashlight, torchOf): held up and forward, its beam aimed at `aim` (across to the free hand's side,
    // forward and up from the feet, in the figure's units), at about the height of its head, where a chat bubble beside it is, never at its
    // own feet, and swept slowly about there, `sweep` across and up and down (torchAim); its lens `lens` from where the hand grips it, which
    // the beam spreads from (chat/FigureAct.vue)
    flashlight: {frames: 80, fps: 10, aim: [2.4, -0.9, 3.5], sweep: [0.5, 0.35], lens: 0.72},
    // searching: it crouches, lifts a corner of the floor it stands on and peeks under it, then lets it down
    peek_under: {frames: 80, fps: 10, lift: [0.08, 0.3], peek: [0.3, 0.75], down: [0.75, 0.92], open: 42},
    // searching, now and then: like a cartoon character hunting through a closet, it rummages in an opening at the edge beside it. The
    // opening comes over `opens`, from `lip` of the picture out from the figure's middle to the picture's edge and `height` of it up from
    // the floor; the figure turns side-on to it and leans in, head and shoulders buried in it, over `leans`, digging about `digs` times;
    // it flings what it pulls out over its shoulder, one thing over each of `throws` (rummage_things), each from `from` up over `over` and
    // down behind it at `to` (the figure's units, across, forward and up, before it turns side-on), tumbling `spins` turns, and shrinking
    // away to nothing over `shrinks` once it lands; it pops out over `pops`, stepping `back` of the picture away from the opening, which
    // shuts behind it over `closes`, and holds up the key it found until it lowers it over `lowers`
    rummage: {
        frames: 132, fps: 12, opens: [0, 0.07], leans: [0.05, 0.14], digs: 7, pops: [0.74, 0.8], closes: [0.78, 0.86], lowers: [0.92, 1], back: 0.06, lip: 0.2, height: 0.72,
        throws: [[0.16, 0.32], [0.28, 0.44], [0.4, 0.56], [0.52, 0.68]], from: [0, -1.5, 1.5], over: 3.9, to: [0, 1.9, 0.2], spins: [1.5, -2, 1.25, -1.75], shrinks: 0.05,
    },
    // a bar it was eager for failed: crushed at first, then plainly mad about it, stamping and fuming, steam rising off its head
    fume: {frames: 54, fps: 12, crushed: [0, 0.36], mad: [0.36, 0.96], stamps: 6, steam: [0.42, 0.96]},
    // a rope swing tied under a bubble: its two ropes `rope` of the figure's height long from the middle of the bubble's bottom edge, `ties`
    // of it apart, down to a seat `seat` of it wide. Its frames are an intro, the knots tied and the ropes let down; a held stretch looped
    // while it swings, `swings` swings each way of `sway` degrees, the legs pumping with them; and an outro, the ropes pulled up. The knots
    // stand at least `room` of the figure's height in from either side of the chat, so it swings clear of them.
    rope_swing: {intro: 12, hold: 60, outro: 12, fps: 12, swings: 2, rope: 0.62, ties: 0.42, seat: 0.5, sway: 9, room: 0.85},
    // a pogo stick up onto a bubble's top: it reaches behind its back and pulls the stick out over `draw`, bounces `count` times on the spot
    // over `bounces`, each higher than the last up to `bounce` of its height, and springs up over `spring` to the top of its throw, `over`
    // of its height past the bubble's edge; there it lets the stick go over `release`, the stick falling away over `drop`, and it falls
    // onto the bubble on its own feet; every hop and the fall are timed by one gravity (pogoHop); the stick `stick` of its height long,
    // its handles where the hands hold it
    pogo: {frames: 54, fps: 12, draw: [0, 0.18], bounces: [0.18, 0.62], count: 3, bounce: 0.45, spring: [0.62, 0.82], over: 0.3, release: [0.82, 0.86], drop: [0.82, 1], stick: 0.62},
    // a passing test run's bug: a small bug crawls in along the floor over `crawl` to `away` of the figure's height out on its free hand's
    // side; it pulls a rifle from behind its back over `draw`, shoots `count` times over `shots`, each shot kicking the rifle back `kick`
    // degrees, the bug splatters at `splat`, and a few drops of the splatter land on the screen, as on a camera's lens, and run down and
    // fade over `drops`
    bug_shot: {frames: 72, fps: 12, crawl: [0, 0.3], draw: [0.2, 0.38], shots: [0.4, 0.56], count: 3, kick: 8, splat: 0.56, drops: [0.58, 1], away: 0.85},
    // a disco dance under a disco ball: the classic move, one arm pointing up and the other down, switching sides `beats` times, the hips
    // swaying and the knees bouncing, the visor flashing through the colours; the ball `ball` of the picture across, turning, hung `clear`
    // of it over the hat, on a string at least `tie` of it long from the bottom of a bubble no further than `far` of the figure's height
    // above the hat
    disco: {frames: 96, fps: 12, beats: 8, ball: 0.24, clear: 0.08, tie: 0.1, far: 2.2},
    // coming down on a parachute, swaying a little under it
    chute: {frames: 24, fps: 8, sway: 8},
    // compacting: a box appears, it hops into it and the box shrinks with it inside; once the compaction is over the box grows back and
    // pops in a puff, and it jumps out. Its frames are an intro, a held stretch looped while the compaction lasts, and an outro
    pack_box: {intro: 36, hold: 24, outro: 26, fps: 12, appears: [0, 0.3], hop: [0.3, 0.62], into: [0.55, 0.88], shrinks: [0.86, 1], grows: [0, 0.3], pops: 0.38, leap: [0.38, 0.88], small: 0.5},
    // compacting: a press comes down onto its head, it holds it up with both hands and is squashed under it, and springs back once it lifts
    press: {intro: 24, hold: 24, outro: 24, fps: 12, lowers: [0, 0.55], squashes: [0.5, 1], frees: [0, 0.3], springs: [0.25, 0.7], lifts: [0.3, 1], flat: 0.42},
    // compacting: it vacuums up the words flying in from beside it, the canister on the floor and the nozzle in its hand
    vacuum: {intro: 10, hold: 40, outro: 10, fps: 10, words: 5},
};

const span = (u, from, to) => Math.min(Math.max((u - from) / (to - from), 0), 1);
const ease = (k) => k * k * (3 - 2 * k);

// how far `u` is through the part `[from, to]` of an act, eased, 0 before it and 1 after
export const partOf = (u, [from, to]) => ease(span(u, from, to));

// the things the figure flings over its shoulder rummaging (rummage), in the order it pulls them out
export const RUMMAGED = ["rummage_papers", "rummage_boot", "rummage_bone", "rummage_book"];

// Where thing `index` of RUMMAGED is `u` of the way through the rummage, as {at, turn, landed}: in flight along its arc from the
// opening up over the figure's shoulder and down behind it, `at` in the figure's units before it turns side-on, `turn` how far it has
// tumbled in degrees, and `landed` how far it has shrunk away once down, 0 to 1; null before it is pulled out and once it is gone
export function flungAt(index, u) {
    const act = ACTS.rummage;
    const [out, down] = act.throws[index];
    if (u < out || u >= down + act.shrinks) return null;
    const s = span(u, out, down);
    const at = act.from.map((from, axis) => from + (act.to[axis] - from) * s);
    at[2] += 4 * (act.over - (act.from[2] + act.to[2]) / 2) * s * (1 - s);
    return {at, turn: 360 * act.spins[index] * s, landed: span(u, down, down + act.shrinks)};
}

// Where a run of hops on the pogo stick is `share` of the way through its time, as {index, s, height}: hop `index` of `heights`, `s` of
// the way through it, and how high above its foot it is then. One gravity times them all: a hop lasts as the square root of its height,
// so a higher one takes longer, and its height goes as 4s(1 - s), rising fast off the ground, slowing to the top and falling faster
export function pogoHop(heights, share) {
    const lengths = heights.map((height) => Math.sqrt(height));
    const whole = lengths.reduce((sum, each) => sum + each, 0);
    let left = Math.min(Math.max(share, 0), 1) * whole;
    for (const [index, length] of lengths.entries()) {
        if (left <= length || index === lengths.length - 1) {
            const s = length > 0 ? Math.min(left / length, 1) : 1;
            return {index, s, height: heights[index] * 4 * s * (1 - s)};
        }
        left -= length;
    }
    return {index: 0, s: 1, height: 0};
}

// the pogo stick's bounces on the spot, in the figure's heights, each higher than the last
export const pogoBounces = () => Array.from({length: ACTS.pogo.count}, (_, hop) => (ACTS.pogo.bounce * (hop + 1)) / ACTS.pogo.count);

// how far a thing that grows out of the floor at the start of an act and sinks at its end stands up at `u`, 0 to 1
export const standingAt = (act, u) => partOf(u, act.grows) * (1 - partOf(u, act.sinks));

// where an act whose frames are an intro, a held stretch and an outro is at `u` of its frames: how far through the intro, the share of the
// held stretch, null outside it, and how far through the outro
export function heldPhases(act, u) {
    const frame = u * (act.intro + act.hold + act.outro);
    const held = frame >= act.intro && frame < act.intro + act.hold;
    return {into: span(frame, 0, act.intro), held: held ? (frame - act.intro) / act.hold : null, out: span(frame, act.intro + act.hold, act.intro + act.hold + act.outro)};
}

// how the picture is squeezed at `u` of the act, as {x, y} scales from the feet, or null: shrunk with the box it is packed in, or
// squashed flat under the press and springing back
export function squeezeOf(name, u) {
    const act = ACTS[name];
    if (name === "pack_box") {
        const {into, held, out} = heldPhases(act, u);
        const size = 1 - (1 - act.small) * partOf(into, act.shrinks) * (1 - partOf(out, act.grows)) + 0.02 * Math.sin(2 * Math.PI * 2 * (held ?? 0));
        return {x: size, y: size};
    }
    if (name === "press") {
        const {into, out} = heldPhases(act, u);
        const flat = act.flat * partOf(into, act.squashes) * (1 - partOf(out, act.frees));
        const spring = 0.14 * Math.sin(2 * Math.PI * span(out, ...act.springs)) * (1 - span(out, ...act.springs));
        return {x: 1 + 0.5 * flat - spring / 2, y: 1 - flat + spring};
    }
    return null;
}

// whether the picture is hidden below the floor through the act, as the figure in the box sinks past it
export const hidesBelowFloor = (name) => name === "pack_box";

// how far the rope swing's ropes are let down at `u` of its frames, 0 to 1: let down through the intro, pulled up through the outro
export function ropeDown(u) {
    const {into, out} = heldPhases(ACTS.rope_swing, u);
    return partOf(into, [0, 1]) * (1 - partOf(out, [0, 1]));
}

// how far the rope swing has swung at `u` of its frames, in degrees, clockwise on the screen: still while the ropes go down or up
export function swingAngle(u) {
    const {held} = heldPhases(ACTS.rope_swing, u);
    return held === null ? 0 : ACTS.rope_swing.sway * Math.sin(2 * Math.PI * ACTS.rope_swing.swings * held);
}

// Where the torch's beam lands `u` of the way through the search, across to the free hand's side, forward and up from the feet, in the
// figure's units (ACTS flashlight): swept once across and back, and twice up and down, as one looks about in the dark
export function torchAim(u) {
    const {aim: [across, forward, up], sweep: [wide, high]} = ACTS.flashlight;
    return [across + wide * Math.sin(2 * Math.PI * u), forward, up + high * Math.sin(4 * Math.PI * u)];
}
