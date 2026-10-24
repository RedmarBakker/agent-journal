import {fallStep} from "../domain/falls.js";
import {stretchedFrame} from "./timeline.js";

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
    // Seated it makes the call sitting with the one hand on the telephone's side (figure.js seatedCall), dialling first, its finger in over
    // `seated.finger`, the dial turned over `seated.dial` and springing back over `seated.back`, then reaching the handset over `seated.reach`
    // and lifting it to its ear over `seated.lift`; it talks and hangs up as standing. The telephone stands on the seat `seated.beside` of the
    // figure's units across from its middle on the page, on the side the seat leaves free (perches.js phoneSide), `seated.behind` back from
    // it, taking `seated.wide` either side of its middle (half the telephone's width and a little more), and the figure leans
    // `seated.lean` degrees over to it as it dials
    phone_call: {frames: 108, fps: 12, poof: [0, 0.06], above: 0.7, drop: [0.015, 0.055], settle: [0.055, 0.12], squash: 0.24, wobbles: 3, reach: [0.13, 0.2], lift: [0.2, 0.28], finger: [0.28, 0.33], dial: [0.33, 0.42], turn: 250, back: [0.42, 0.5], talk: [0.5, 0.72], nods: 3, hang: [0.72, 0.84], goes: [0.92, 1], seated: {finger: [0.13, 0.18], dial: [0.18, 0.28], back: [0.28, 0.33], reach: [0.33, 0.4], lift: [0.4, 0.5], beside: 1.3, behind: 0.15, wide: 0.7, lean: 14}},
    // a question asked: it raises a sign with a question mark on a stick over its head and waggles it
    ask_sign: {frames: 42, fps: 12, raise: [0, 0.22], waggle: [0.22, 0.78], waggles: 3, lower: [0.78, 1]},
    // a report: it brings the rolled scroll up before its chest over `raise`, a roller in each hand, the free hand's on top; pulls the
    // rollers apart over `unrolls`, the written side toward itself and the parchment's plain back to the viewer (figure.js SCROLL); reads
    // it `lines` lines down, its head going slowly along each; rolls it closed between its hands over `rolls` and lowers it over `lower`
    scroll: {frames: 96, fps: 12, raise: [0, 0.09], unrolls: [0.09, 0.22], rolls: [0.85, 0.93], lower: [0.93, 1], lines: 3},
    // a task finished, a job well done: standing, it brings its hands together before its chest over `together`, rubs them round each
    // other `rubs` times, slowly, a stroke and a half a second at most, nodding a little with each, and lowers them over `apart`; `puffs`
    // small puffs rise from the hands once each over `puff`, with `sparkles` sparkles among them (chat/act/HandRub.vue)
    hand_rub: {frames: 48, fps: 12, together: [0, 0.12], rubs: 2, apart: [0.88, 1], puff: [0.2, 0.9], puffs: 2, sparkles: 1},
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
    // searching from the compose box: binoculars at its eyes, tipped `up` degrees up the chat and scanning slowly up and down it `scan`
    // degrees either way, twice, with a little turn left and right
    binoculars: {frames: 100, fps: 10, sweep: 1, up: 9, scan: 6},
    // searching, now and then: at the edge of the chat window the figure reaches past it into the space beyond, where nothing is seen, and
    // rummages there like a cartoon character hunting through a closet: it turns side-on to the edge and leans in, head and shoulders past
    // it, over `leans`, digging about `digs` times, and flings what it pulls out back over its shoulder, one thing at each of `throws`, each
    // from `from` (the figure's units, across, forward and up, before it turns side-on) on the arc its throw gives it (throwsFor), shrinking
    // away to nothing over `shrinks` once it lands; over `pops` it pulls back out, having found nothing
    rummage: {
        frames: 120, fps: 12, leans: [0.05, 0.14], digs: 7, pops: [0.8, 0.9], throws: [0.18, 0.28, 0.38, 0.48], from: [0, -1.5, 1.5], shrinks: 0.05,
    },
    // a bar it was eager for failed: crushed at first, then plainly mad about it, stamping and fuming, steam rising off its head
    fume: {frames: 54, fps: 12, crushed: [0, 0.36], mad: [0.36, 0.96], stamps: 6, steam: [0.42, 0.96]},
    // a rope swing tied under a bubble, drawn whole from the act's first frame: its two ropes `rope` of the figure's height long from the
    // middle of the bubble's bottom edge, `ties` of it apart, just outside the figure's arms, down to a seat `seat` of it wide, a little wider
    // than its body, whose top is `under` of it below the line the figure sits on, where its thighs' underside rests. Its frames are an
    // intro, the figure sitting down onto the seat; a held stretch looped while it swings, `swings` swings each way of `sway` degrees, the
    // legs pumping with them; and an outro, the figure rising off it. The knots stand at least `room` of the figure's height in from either
    // side of the chat, so it swings clear of them.
    rope_swing: {intro: 12, hold: 60, outro: 12, fps: 12, swings: 2, rope: 0.62, ties: 0.53, seat: 0.59, under: 0.025, sway: 9, room: 0.85},
    // a pogo stick up onto a bubble's top: it reaches behind its back and pulls the stick out over `draw`, bounces `count` times on the spot
    // over `bounces`, each higher than the last up to `bounce` of its height, and springs up over `spring` to the top of its throw, `over`
    // of its height past the bubble's edge; there it lets the stick go over `release`, the stick falling away over `drop`, and it falls
    // onto the bubble on its own feet; every hop and the fall are timed by one gravity (pogoHop); the stick `stick` of its height long,
    // its handles where the hands hold it
    pogo: {frames: 54, fps: 12, draw: [0, 0.18], bounces: [0.18, 0.62], count: 3, bounce: 0.45, spring: [0.62, 0.82], over: 0.3, release: [0.82, 0.86], drop: [0.82, 1], stick: 0.62},
    // a fixed run's bugs: two to five of them crawl along the chat window's walls (WALL_BUGS); the figure pulls a rifle from behind its back
    // over `draw` and shoulders it, then shoots them one by one, each in its own `turn` of the act played over again for every bug
    // (bugShotFrame): it swings its aim onto the bug over `aim`, shoots `count` bursts over `shots`, each kicking the rifle and the shoulder
    // back, and the bug splatters on its wall at `splat`; after the last, drops of its splatter fly out at the screen over `fly`, growing
    // as they come, land on it as on a camera's lens at their `lens` places (from the figure's middle, in shares of the picture, as big as
    // `size`), and run down and fade over `drops`, as the rifle is lowered
    bug_shot: {
        frames: 80, fps: 12, draw: [0, 0.22], turn: [0.25, 0.55], aim: [0.25, 0.32], shots: [0.33, 0.48], count: 2, splat: 0.48, fly: [0.56, 0.64], drops: [0.64, 1],
        lens: [{at: [-1.3, -1.6], size: 0.2}, {at: [0.9, -0.9], size: 0.14}, {at: [-0.4, 0.2], size: 0.16}, {at: [1.6, -2.1], size: 0.1}],
    },
    // a fixed run's bug smashed with a big wooden mallet on the floor the figure stands on (smashPlan): the bug climbs up the back of the
    // floor's box, out of sight behind it, over `emerge`, comes over its top edge onto it over `climb`, and it and the figure walk to meet
    // each other over `walk`, until it is `away` of the picture out on the figure's left (`side`); the figure raises the mallet high before
    // its head over `raise` and holds it there for the wind-up until `swing`, swings it down over `swing` and flattens the bug at `blow`,
    // which lies flat and fades over `gone`, and lowers the mallet over `lower`
    bug_smash: {
        frames: 96, fps: 12, side: 1, emerge: [0, 0.09], climb: [0.09, 0.16], walk: [0.16, 0.38], raise: [0.46, 0.58], swing: [0.66, 0.72], blow: 0.72, gone: [0.84, 0.95],
        lower: [0.88, 0.99], away: 0.42,
    },
    // a sin repented: a halo grows over the head over `grows` and fades over `fades`, the figure floating up `float` of its units and down
    // with its hands folded and a serene, holy look
    halo: {frames: 48, fps: 12, grows: [0, 0.15], fades: [0.85, 1], float: 0.06},
    // a sin found: the figure drops to its knees over `kneel`, brings out a small crucifix over `out`, holds it up over `up` and keeps it
    // up, trembling a little, until `hold` ends, puts it away over `down` and gets up over `rise`
    repent: {frames: 72, fps: 12, kneel: [0, 0.18], out: [0.16, 0.28], up: [0.26, 0.36], hold: [0.36, 0.78], down: [0.78, 0.86], rise: [0.84, 1]},
    // a disco dance under a disco ball: the classic move, one arm pointing up and the other down, switching sides `beats` times, the hips
    // swaying and the knees bouncing, the visor flashing through the colours; the ball `ball` of the picture across, turning, hung `clear`
    // of it over the hat, on a string at least `tie` of it long from the bottom of a bubble no further than `far` of the figure's height
    // above the hat
    disco: {frames: 96, fps: 12, beats: 8, ball: 0.24, clear: 0.08, tie: 0.1, far: 2.2},
    // leaning against a wall to rest (perches.js leanSpot): the wall `wall` of the picture out from its middle, the hand flat against it
    // `contact` of the figure's units above its feet; the whole body tilted `tilt` degrees toward it from the feet, its weight on that hand;
    // the other hand on its hip at `hip` (across, forward, up); the ankles crossed, the inner leg turned in `inner` degrees and the outer
    // `outer`, swung `over` degrees before the inner so its foot crosses over in front
    lean: {wall: 0.33, contact: 1.95, tilt: 16, hip: [0.62, 0.05, 1.5], inner: 20, outer: 42, over: 12},
    // coming down on a parachute, swaying `sway` degrees under it, its canopy (figure.js canopyOf) `width` of the picture across with its
    // rim `above` of the picture over the eyes, the lines running from the rim down to the hands
    chute: {frames: 24, fps: 8, sway: 8, width: 0.66, above: 0.5},
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

// How each thing flung out rummaging flies, worked out afresh for each rummage (throwsFor): thrown from the opening at `speed` units a
// second, `angle` degrees above level back over the shoulder, drifting `spread` units a second to either side, spinning `spin` degrees a
// second either way, and falling at `gravity` units a second squared until it reaches the floor at `floor`, where it lies and shrinks away
export const THROW = {speed: [8, 10], angle: [66, 80], spread: [-0.8, 0.8], spin: [400, 900], gravity: 14, floor: 0.2};

const within = ([least, most], random) => least + random() * (most - least);

// The throws of one rummage, one for each thing of RUMMAGED, each {velocity, spin}: its velocity across, back and up in units a second,
// and its spin in degrees a second, drawn from THROW's ranges
export function throwsFor(random) {
    return RUMMAGED.map(() => {
        const speed = within(THROW.speed, random);
        const angle = (within(THROW.angle, random) * Math.PI) / 180;
        const spin = within(THROW.spin, random) * (random() < 0.5 ? -1 : 1);
        return {velocity: [within(THROW.spread, random), speed * Math.cos(angle), speed * Math.sin(angle)], spin};
    });
}

// the throws of a rummage the page drew none for: the middle of each range, the spins turning either way in turn
export const MIDDLE_THROWS = throwsFor(() => 0.5).map((thrown, index) => ({...thrown, spin: Math.abs(thrown.spin) * (index % 2 ? -1 : 1)}));

// the seconds a throw is in the air, from the opening at `from` up and down onto the floor
export function flightSeconds(thrown, from) {
    const up = thrown.velocity[2];
    return (up + Math.sqrt(up * up + 2 * THROW.gravity * (from[2] - THROW.floor))) / THROW.gravity;
}

// Where thing `index` of RUMMAGED is `u` of the way through the rummage, thrown as `throws` says, as {at, turn, landed}: in flight from
// the opening along the arc gravity gives it, `at` in the figure's units before it turns side-on, `turn` how far it has spun in degrees,
// and `landed` how far it has shrunk away lying on the floor, 0 to 1; null before it is pulled out and once it is gone
export function flungAt(index, u, throws = MIDDLE_THROWS) {
    const act = ACTS.rummage;
    const seconds = ((u - act.throws[index]) * act.frames) / act.fps;
    const thrown = throws[index];
    const flight = flightSeconds(thrown, act.from);
    const lies = (act.shrinks * act.frames) / act.fps;
    if (seconds < 0 || seconds >= flight + lies) return null;
    const time = Math.min(seconds, flight);
    const at = act.from.map((from, axis) => from + thrown.velocity[axis] * time);
    at[2] -= (THROW.gravity * time * time) / 2;
    return {at, turn: thrown.spin * time, landed: Math.max(0, seconds - flight) / lies};
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

// The meeting of the mallet act on the floor the figure stands on, in shares of the figure's picture: the bug comes up behind the floor's
// box `reach` further out than the blow lands, never nearer an end of the floor than `margin`, starting `tall` below its top edge, out of
// sight; the figure walks in steps `stride` long; and the bug keeps to its floor while the floor moves no more than `carried` pixels in a
// frame, as the figure does (floors.js CARRIED_WITHIN)
export const SMASH = {reach: 1.2, margin: 0.25, tall: 0.14, stride: 0.5, carried: 5};

// The mallet act of a figure with its middle at `x` on the floor `floor` (its left, right and top on the page), its picture `size` pixels
// across: where the figure and the bug start and end, each [from, to] in pixels from the floor's left, so a floor that moves carries them;
// both walk to meet halfway, the bug ending `away` of the picture out on the figure's left, where the blow lands, and a figure with too
// little room for that walks back to it on its own
export function smashPlan(x, floor, size) {
    const {away, side} = ACTS.bug_smash;
    const out = side * away * size;
    const [low, high] = [floor.left + SMASH.margin * size, floor.right - SMASH.margin * size];
    const from = Math.min(Math.max(x + out + side * SMASH.reach * size, low), high);
    const gap = from - out - x;
    const to = from - (side * gap > 0 ? gap / 2 : 0);
    return {figure: [x - floor.left, to - out - floor.left], bug: [from - floor.left, to - floor.left]};
}

// The mallet act by the plan `plan` (smashPlan) `u` of the way through, the figure's picture `size` pixels across: the figure's middle in
// pixels from the floor's left, the steps it has walked and the way it walks (1 the viewer's right); and the bug: in pixels from the floor's
// left, how far below the floor's top edge it is, behind the box, the degrees it is turned from walking, 90 head up as it climbs, whether
// it is still whole, how flat the blow has left it, 0 whole to 1 flat, and how much of it still shows as it fades
export function smashAt(plan, u, size) {
    const act = ACTS.bug_smash;
    const walked = partOf(u, act.walk);
    const along = ([from, to]) => from + (to - from) * walked;
    return {
        figure: along(plan.figure),
        steps: Math.abs(along(plan.figure) - plan.figure[0]) / (SMASH.stride * size),
        way: Math.sign(plan.figure[1] - plan.figure[0]),
        bug: {
            dx: along(plan.bug),
            below: SMASH.tall * size * (1 - partOf(u, act.emerge)),
            turn: 90 * (1 - partOf(u, act.climb)),
            whole: u < act.blow,
            flat: u >= act.blow ? 1 : 0,
            shows: 1 - partOf(u, act.gone),
        },
    };
}

// One frame of the mallet act's bug, `bug` ({x, y, speed, falling}), `on` where the act puts it on its floor now ({x, y}), or null once the
// floor is gone or no longer reaches under it: on its floor while that holds it, carried with it, up too; once it went, or dropped further
// in a frame than SMASH carried, as a bar docked over the compose box closes, it falls at GRAVITY from where it was onto `ground`, the top of what is
// under it, and stays there
export function bugStep(bug, on, ground, seconds) {
    if (!bug.falling && on && (bug.y === undefined || on.y - bug.y <= SMASH.carried)) return {x: on.x, y: on.y, speed: 0, falling: false};
    const fell = fallStep({y: bug.y, speed: bug.speed}, ground, seconds);
    return {x: bug.x, y: fell.y, speed: fell.speed, falling: true};
}

// The bugs of a bug shot on the chat window's walls: at least `least` and at most `most` of them, each on the left, the right or the top wall,
// `inset` pixels in from it, crawling along it `speed` pixels a second, turning back `margin` of the wall's length from its ends
export const WALL_BUGS = {least: 2, most: 5, walls: ["left", "right", "top"], inset: 8, speed: 14, margin: 0.1};

// the bugs of a bug shot drawn with `random`, each {wall, along, way}: its wall, where along it it starts, 0 to 1, and the way it crawls
export function wallBugs(random) {
    const count = WALL_BUGS.least + Math.floor(random() * (WALL_BUGS.most - WALL_BUGS.least + 1));
    return Array.from({length: count}, () => ({
        wall: WALL_BUGS.walls[Math.floor(random() * WALL_BUGS.walls.length)],
        along: WALL_BUGS.margin + random() * (1 - 2 * WALL_BUGS.margin),
        way: random() < 0.5 ? -1 : 1,
    }));
}

// Where the wall bug `bug` is `seconds` after it came, in the chat window `world` (its left, top, right and bottom on the page): the page
// point it stands at on its wall, crawling back and forth along it, and the way its back faces, in degrees, 0 its feet down
export function wallBugAt(bug, world, seconds) {
    const tall = bug.wall === "top" ? world.right - world.left : world.bottom - world.top;
    const span = 1 - 2 * WALL_BUGS.margin;
    const run = (bug.along - WALL_BUGS.margin + (bug.way * WALL_BUGS.speed * seconds) / tall) / span;
    const phase = ((run % 2) + 2) % 2;
    const along = WALL_BUGS.margin + span * (phase <= 1 ? phase : 2 - phase);
    if (bug.wall === "top") return {x: world.left + along * tall, y: world.top + WALL_BUGS.inset, turn: 180};
    const x = bug.wall === "left" ? world.left + WALL_BUGS.inset : world.right - WALL_BUGS.inset;
    return {x, y: world.top + along * tall, turn: bug.wall === "left" ? 90 : -90};
}

// The bug shot `raw` frames in when it shoots `count` bugs: the frame of its clip, its turn played over once for each bug (timeline.js
// stretchedFrame, `stretch`); the bug it aims at, by its turn; and how many it has shot, a bug splattering at its turn's `splat`
export function bugShotFrame(raw, count) {
    const act = ACTS.bug_shot;
    const [from, to] = act.turn.map((share) => share * act.frames);
    const stretch = {from, to, extra: (count - 1) * (to - from)};
    const frame = stretchedFrame(raw, stretch);
    const turn = raw < from ? 0 : Math.min(Math.floor((raw - from) / (to - from)), count - 1);
    const done = raw >= from + count * (to - from);
    const shot = done ? count : turn + (frame / act.frames >= act.splat ? 1 : 0);
    return {frame, stretch, bug: turn, shot};
}

// The bug shot `raw` frames in, its bugs `bugs` (wallBugs) in the chat window `world`: each bug where it is on its wall (wallBugAt), still
// where it was shot once it is, and whether it is; the frame of the clip (bugShotFrame); and the page point the rifle aims at, swung from
// the bug before onto the bug of this turn over the turn's `aim`
export function bugShotScene(bugs, world, raw) {
    const act = ACTS.bug_shot;
    const {frame, bug, shot} = bugShotFrame(raw, bugs.length);
    const turnFrames = (act.turn[1] - act.turn[0]) * act.frames;
    const shotAt = (index) => (act.turn[0] * act.frames + index * turnFrames + (act.splat - act.turn[0]) * act.frames) / act.fps;
    const placed = bugs.map((each, index) => ({...wallBugAt(each, world, Math.min(raw / act.fps, shotAt(index))), shot: index < shot}));
    const swing = partOf(frame / act.frames, act.aim);
    const [from, to] = [placed[Math.max(bug - 1, 0)], placed[bug]];
    return {bugs: placed, frame, target: {x: from.x + (to.x - from.x) * swing, y: from.y + (to.y - from.y) * swing}};
}

// The drops of a shot bug's splatter `u` of the way through the bug shot (ACTS bug_shot), in a picture `size` pixels across, the bug at
// `from` (x, y) and the picture's middle at `middle`: each flying out at the screen from the bug over `fly`, growing from a speck to its
// size as it comes, then on the glass at its lens place, running down and fading; none before they fly, after the last bug is shot
export function splatDrops(u, size, from, middle) {
    const {fly, drops, lens} = ACTS.bug_shot;
    if (u < fly[0]) return [];
    const flown = partOf(u, fly);
    const dripped = partOf(u, drops);
    return lens.map((drop) => {
        const landed = {x: middle.x + drop.at[0] * size, y: middle.y + drop.at[1] * size};
        return {
            x: from.x + (landed.x - from.x) * flown,
            y: from.y + (landed.y - from.y) * flown,
            r: drop.size * size * (0.15 + 0.85 * flown * flown),
            run: dripped * dripped * size * 1.2,
            fade: 1 - dripped,
            landed: flown >= 1,
        };
    });
}

// The parachute over the figure `u` of the way through its sway, in the picture's pixels: the canopy's picture `canopy` (figure.js
// Stage.drawCanopy, its rim's middle `at` and its lines' ends `ends`, the left pair first) placed with its rim's middle ACTS.chute above of
// the picture `size` over the eyes at `head`, turned `turn` degrees about that middle as it sways; and its lines, each from where it leaves
// the rim, turned with it, down to the hand on its side, `hands` the two hands' grips in either order
export function chuteOver(canopy, head, hands, size, u) {
    const {sway, above} = ACTS.chute;
    const middle = {x: head.x, y: head.y - above * size};
    const turn = (sway / 2) * Math.sin(2 * Math.PI * u);
    const [cos, sin] = [Math.cos((turn * Math.PI) / 180), Math.sin((turn * Math.PI) / 180)];
    const turned = (end) => {
        const [dx, dy] = [end.x - canopy.at.x, end.y - canopy.at.y];
        return {x: middle.x + dx * cos - dy * sin, y: middle.y + dx * sin + dy * cos};
    };
    const [left, right] = [...hands].sort((one, other) => one.x - other.x);
    const ends = canopy.ends.map(turned);
    return {left: middle.x - canopy.at.x, top: middle.y - canopy.at.y, middle, turn, lines: ends.map((from, index) => ({from, to: index < ends.length / 2 ? left : right}))};
}

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

// how far above the rope swing's seat the figure is at `u` of its frames, 0 sat on it to 1: sitting down onto it through the intro, rising off
// it through the outro
export function offSwing(u) {
    const {into, out} = heldPhases(ACTS.rope_swing, u);
    return 1 - partOf(into, [0, 1]) * (1 - partOf(out, [0, 1]));
}

// how far the rope swing has swung at `u` of its frames, in degrees, clockwise on the screen: still while the ropes go down or up
export function swingAngle(u) {
    const {held} = heldPhases(ACTS.rope_swing, u);
    return held === null ? 0 : ACTS.rope_swing.sway * Math.sin(2 * Math.PI * ACTS.rope_swing.swings * held);
}

