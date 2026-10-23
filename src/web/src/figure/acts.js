// The journal moments and the searches the figure acts out with things the page draws beside it (chat/FigureAct.vue): for each act its
// length, unless it plays a clip of figure.js's own, and the shares of its clip over which each of its parts plays, read alike by the clip that moves the body (figure.js) and by
// the page that draws what it holds, so the hand and the thing in it never part.
export const ACTS = {
    // a reply: it holds an envelope up high, a dove flies in, takes it and flies off with it
    post_dove: {frames: 48, fps: 12, raise: [0, 0.18], comes: [0.2, 0.5], taken: 0.5, goes: [0.5, 0.95], lower: [0.58, 0.8]},
    // a reply: a red mailbox on a plank grows out of the floor beside it, it posts the letter, the flag goes up and the box sinks again
    post_mailbox: {frames: 48, fps: 12, grows: [0, 0.18], reach: [0.2, 0.42], posted: [0.42, 0.55], back: [0.6, 0.76], flag: 0.55, sinks: [0.84, 1]},
    // a finished task: a sheet on a stand grows beside it, it lifts a big stamp, brings it down on the sheet, which is stamped green
    stamp: {frames: 42, fps: 12, grows: [0, 0.15], lift: [0.12, 0.36], down: [0.36, 0.46], stamped: 0.45, up: [0.52, 0.7], sinks: [0.86, 1]},
    // a new task: a small board on a post grows beside it and it pins a note to it, then taps it
    pin_note: {frames: 42, fps: 12, grows: [0, 0.15], reach: [0.15, 0.4], pinned: 0.42, tap: [0.5, 0.64], back: [0.64, 0.8], sinks: [0.86, 1]},
    // a question asked: it raises a sign with a question mark on a stick over its head and waggles it
    ask_sign: {frames: 42, fps: 12, raise: [0, 0.22], waggle: [0.22, 0.78], waggles: 3, lower: [0.78, 1]},
    // a worker sent out: it blows a whistle and a small runner sets off from beside it and runs off the screen
    whistle_runner: {runs: [0.3, 0.98], strides: 9},
    // a report: it holds a scroll up before it in both hands, which unrolls down, is read, and rolls up again
    scroll: {frames: 48, fps: 12, raise: [0, 0.16], unrolls: [0.16, 0.4], rolls: [0.8, 0.94], lower: [0.9, 1]},
    // a fact or a reminder: a small cabinet grows beside it, its drawer slides out, it files a card in it and the drawer shuts
    file_card: {frames: 42, fps: 12, grows: [0, 0.15], opens: [0.12, 0.28], reach: [0.2, 0.44], filed: [0.44, 0.56], back: [0.56, 0.72], shuts: [0.58, 0.72], sinks: [0.86, 1]},
    // a check that passed: a thumbs up, and a little confetti bursts over its head
    cheer: {burst: [0.35, 0.95]},
    // a celebration: it aims a confetti cannon up and fires it, kicked back a little as the confetti bursts out
    confetti_cannon: {frames: 40, fps: 12, aim: [0, 0.25], fire: 0.4, kick: [0.4, 0.55], burst: [0.4, 0.95], lower: [0.8, 1]},
    // a celebration: it blows a party horn at its mouth, which unrolls and rolls back up with each blow
    party_horn: {frames: 44, fps: 12, raise: [0, 0.18], blows: [[0.22, 0.48], [0.52, 0.8]], lower: [0.84, 1]},
    // searching: binoculars at its eyes, sweeping slowly left and right
    binoculars: {frames: 80, fps: 10, sweep: 1},
    // searching: a flashlight shone into a dark corner beside it, the beam moving about in it
    flashlight: {frames: 80, fps: 10},
    // searching: it crouches, lifts a corner of the floor it stands on and peeks under it, then lets it down
    peek_under: {frames: 80, fps: 10, lift: [0.08, 0.3], peek: [0.3, 0.75], down: [0.75, 0.92], open: 42},
    // a bar it was eager for failed: crushed at first, then plainly mad about it, stamping and fuming, steam rising off its head
    fume: {frames: 54, fps: 12, crushed: [0, 0.36], mad: [0.36, 0.96], stamps: 6, steam: [0.42, 0.96]},
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
