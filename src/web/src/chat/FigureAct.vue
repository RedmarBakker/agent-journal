<script setup>
import {computed} from "vue";
import {ACTS, heldPhases, partOf, ropeDown, standingAt} from "../figure/acts.js";
import {POSTURES} from "../figure/places.js";

// What the figure holds and what grows beside it while it acts out a journal moment or a search (figure/acts.js), drawn over its picture:
// the act `name`, `u` of the way through it, 0 to 1; the free hand's grip, the eyes and the feet as shares of the picture (`hand.out` the
// way across the picture the free hand's side is, 1 to the right, and `hand.other` the other hand's grip); the picture `size` pixels square; and `room`, the pixels from its left
// and right sides to the screen's edges, which a runner runs off past; and `ball`, where the disco ball hangs over the feet while it
// dances (perches.js discoBall).
const props = defineProps({
    name: {type: String, required: true},
    u: {type: Number, required: true},
    hand: {type: Object, required: true},
    head: {type: Object, required: true},
    feet: {type: Number, required: true},
    size: {type: Number, required: true},
    room: {type: Object, required: true},
    ball: {type: Object, default: null},
});

// Where what stands beside the figure stands, as shares of the picture: across from its middle, toward the free hand, and the height of
// its top above the feet; and the drawings' sizes and colours, in pixels
const STANDS = {file_card: {across: 0.24, top: 0.3}};
const COLOURS = {ink: "#272936", paper: "#f6f1e3", red: "#d9413b", wood: "#8a5a2b", gold: "#e8b84a", light: "#fff3a8", rope: "#c9a56a", silver: "#c3c7d1", smoke: "#e9e7e1"};

const act = computed(() => ACTS[props.name]);
const px = (share) => share * props.size;
const hand = computed(() => ({x: px(props.hand.x), y: px(props.hand.y), out: props.hand.out}));
const head = computed(() => ({x: px(props.head.x), y: px(props.head.y)}));
// The bug shot: the bug crawling in along the floor to its place out on the free hand's side, its legs going, until it splatters; the rifle
// in the free hand pointed at it, kicked back by each shot, with its flash; and the drops of the splatter on the screen, as on a camera's
// lens, each `at` its place from the figure's middle in shares of the picture, as big as `size`, landing at the splatter and running
// down as they fade
const LENS_DROPS = [{at: [-1.3, -1.6], size: 0.2}, {at: [0.9, -0.9], size: 0.14}, {at: [-0.4, 0.2], size: 0.16}, {at: [1.6, -2.1], size: 0.1}];
const bug = computed(() => {
    const {crawl, draw, shots, count, kick, splat, drops, away} = ACTS.bug_shot;
    const out = props.hand.out;
    const crawled = partOf(props.u, crawl);
    const x = middle.value + out * props.size * (away + 1.1 * (1 - crawled));
    const y = floor.value - 3;
    const aimed = partOf(props.u, [(draw[0] + draw[1]) / 2, draw[1]]) * (props.u < drops[0] + 0.15 ? 1 : 0);
    const shot = ((props.u - shots[0]) / (shots[1] - shots[0])) * count;
    const firing = props.u > shots[0] && props.u < shots[1] && shot % 1 < 0.35;
    const angle = (Math.atan2(y - hand.value.y, x - hand.value.x) * 180) / Math.PI - (firing ? out * kick : 0);
    const dripped = partOf(props.u, drops);
    return {
        x,
        y,
        alive: props.u < splat,
        legs: Math.sin(props.u * 90) * 1.2,
        splat: props.u >= splat ? 1 - partOf(props.u, [0.85, 1]) : 0,
        aimed,
        angle,
        firing,
        drops: props.u >= splat ? LENS_DROPS.map((drop) => ({x: middle.value + drop.at[0] * props.size, y: px(0.5) + drop.at[1] * props.size, r: drop.size * props.size, run: dripped * dripped * props.size * 1.2, fade: 1 - dripped})) : [],
    };
});

// The disco ball over the dancing figure: its string from where it is tied down to the ball, the ball's mirror tiles turning as it
// spins, and flecks of its light going round the figure in the colours
const disco = computed(() => {
    if (!props.ball) return null;
    const r = (ACTS.disco.ball * props.size) / 2;
    const y = floor.value - props.ball.hangs;
    const turn = props.u * 40;
    const tiles = [];
    for (let row = -2; row <= 2; row++) for (let column = -3; column <= 3; column++) tiles.push({x: middle.value + column * r * 0.42 + ((turn * r * 0.42) % (r * 0.42)) - r * 0.21, y: y + row * r * 0.42, light: (row + column + Math.floor(turn)) % 3 === 0});
    const flecks = Array.from({length: 9}, (_, index) => {
        const way = index * 0.7 + props.u * 9;
        return {x: middle.value + Math.cos(way) * props.size * (0.55 + 0.1 * (index % 3)), y: y + 10 + Math.abs(Math.sin(way * 1.3)) * props.size * 0.75, colour: `hsl(${(index * 40 + props.u * 1400) % 360} 95% 65%)`};
    });
    return {x: middle.value, y, r, top: floor.value - props.ball.above, tiles, flecks};
});

// the pogo stick, upright under the hands with its foot below the figure's feet: drawn out from behind the back, held, and let go to fall
// away out of sight, turning as it goes; its handlebar, foot pegs and spring
const stick = computed(() => {
    const {draw, drop, stick: long} = ACTS.pogo;
    const height = long * props.size;
    const falling = partOf(props.u, drop);
    const coil = Array.from({length: 7}, (_, index) => `${index % 2 ? 3 : -3} ${2 + index * 1.6}`).join(" L");
    return {
        shown: partOf(props.u, [draw[1] * 0.6, draw[1]]),
        foot: floor.value,
        top: -height * 0.82,
        bottom: height * 0.18,
        bar: props.size * 0.16,
        peg: props.size * 0.13,
        spring: `M0 1 L${coil} L0 ${2 + 7 * 1.6}`,
        fall: falling * falling * props.size * 9,
        turn: 70 * falling,
    };
});

// the rope swing: where its seat runs, under the hips of the figure sitting on it, the knots it hangs from on the bubble's bottom edge above,
// and how far its ropes are let down from them
const swing = computed(() => {
    const {rope, ties, seat} = ACTS.rope_swing;
    const line = px(props.feet - POSTURES.sit.drop);
    const top = line - rope * props.size;
    const down = ropeDown(props.u);
    return {line, top, reach: top + (line - top) * down, down, ropes: [-1, 1].map((side) => middle.value + (side * ties * props.size) / 2), seat: seat * props.size};
});
const floor = computed(() => px(props.feet));
const middle = computed(() => px(0.5));
const out = computed(() => props.hand.out);

// a thing beside the figure that grows up out of the floor and sinks back: its middle across, its top, and how far it stands up, 0 to 1
const stand = computed(() => {
    const at = STANDS[props.name];
    if (!at) return null;
    return {x: middle.value + out.value * px(at.across), top: floor.value - px(at.top), up: standingAt(act.value, props.u)};
});
const growing = computed(() => stand.value && `translate(0 ${floor.value}) scale(1 ${stand.value.up}) translate(0 ${-floor.value})`);


// the sign over its head on a stick, tipping as it waggles
const waggle = computed(() => {
    const [from, to] = act.value.waggle;
    const k = Math.min(Math.max((props.u - from) / (to - from), 0), 1);
    return 14 * Math.sin(2 * Math.PI * act.value.waggles * k) * Math.sin(Math.PI * k);
});

// The scroll between the hands, `half` its width either side of a roller's middle: rolled in the free hand while the hands come up and go
// down, and once both hold it, its top roller in the free hand and its bottom roller in the other, the parchment between them turned
// with its written side to the figure, so the viewer sees only its plain back, aged darker than fresh paper
const SCROLL_HALF = 0.09;
const ROLLER = 3.4;
const PARCHMENT_BACK = "#dcc79c";
const scrollHeld = computed(() => {
    const top = hand.value;
    const held = partOf(props.u, act.value.raise) * (1 - partOf(props.u, act.value.lower)) === 1;
    const bottom = held ? {x: px(props.hand.other.x), y: px(props.hand.other.y)} : {x: top.x, y: top.y + ROLLER};
    const half = px(SCROLL_HALF);
    const parchment = `M${top.x - half + 1} ${top.y}L${top.x + half - 1} ${top.y}L${bottom.x + half - 1} ${bottom.y}L${bottom.x - half + 1} ${bottom.y}Z`;
    return {top, bottom, half, parchment};
});

// The thought cloud over the thinking figure's head, out toward its free hand: three puffs rising from beside the head one after another
// into a small cloud, `across` and `above` the eyes as shares of the picture, `wide` across, holding three dots that pulse one after
// another, each its turn of the act's pulse; all of it fading as the bulb lights
const CLOUD = {across: 0.24, above: 0.36, wide: 0.3, puffs: [[0.08, 0.12, 0.022], [0.13, 0.2, 0.03], [0.18, 0.27, 0.04]]};
const cloud = computed(() => {
    const {puffs, cloud: held, rise, pulse, frames, fps} = act.value;
    const shown = partOf(props.u, [held[0], puffs[1]]) * (1 - partOf(props.u, [held[1], rise[1]]));
    if (!shown) return null;
    const out = props.hand.out;
    const seconds = (props.u * frames) / fps;
    const rising = CLOUD.puffs.map(([across, above, r], index) => ({
        x: head.value.x + out * px(across),
        y: head.value.y - px(above),
        r: px(r) * partOf(props.u, [puffs[0] + (index * (puffs[1] - puffs[0])) / 3, puffs[0] + ((index + 1) * (puffs[1] - puffs[0])) / 3]),
    }));
    const x = head.value.x + out * px(CLOUD.across);
    const y = head.value.y - px(CLOUD.above);
    const w = px(CLOUD.wide);
    const bumps = [[-0.32, 0.05, 0.2], [-0.12, -0.12, 0.24], [0.14, -0.1, 0.22], [0.32, 0.06, 0.18], [0, 0.12, 0.22]].map(([dx, dy, r]) => ({x: x + dx * w, y: y + dy * w, r: r * w}));
    const dots = [-1, 0, 1].map((place, index) => ({x: x + place * w * 0.22, y, r: w * 0.05 * (1 + 0.5 * Math.max(Math.sin(2 * Math.PI * (seconds / pulse - index / 3)), 0)), lit: 0.35 + 0.65 * Math.max(Math.sin(2 * Math.PI * (seconds / pulse - index / 3)), 0)}));
    return {shown, rising, bumps, dots, grown: partOf(props.u, [puffs[0] + (2 * (puffs[1] - puffs[0])) / 3, puffs[1]])};
});

// the drawer slid out, 0 to 1, and the card dropped into it
const drawer = computed(() => partOf(props.u, act.value.opens) * (1 - partOf(props.u, act.value.shuts)));
const filed = computed(() => partOf(props.u, act.value.filed));

// the flashlight's beam into the dark corner beside the figure, its lit end moving as the hand does
const corner = computed(() => ({x: middle.value + out.value * px(0.5), y: floor.value - 10}));
const beam = computed(() => {
    const lit = {x: corner.value.x - out.value * 4, y: corner.value.y + (hand.value.y - px(0.66)) * 1.6};
    const tip = {x: hand.value.x + out.value * 6, y: hand.value.y + 2};
    return {tip, lit, path: `M${tip.x} ${tip.y - 1.5}L${lit.x} ${lit.y - 9}L${lit.x} ${lit.y + 9}L${tip.x} ${tip.y + 1.5}Z`};
});

// where an act of an intro, a held stretch and an outro is
const phases = computed(() => (act.value.intro ? heldPhases(act.value, props.u) : null));

// the box: popping up around the feet, its flaps open, until it pops in a puff of smoke with its bits flying off
const box = computed(() => {
    const {appears, pops} = act.value;
    const {into, out} = phases.value;
    const popped = out >= pops;
    const puff = popped ? Math.min((out - pops) / 0.4, 1) : 0;
    return {grown: partOf(into, appears), popped, puff, x: middle.value, width: 50, height: 36};
});

// the press: its plate lowered onto the head on its screw from above the picture, and lifted off it again
const plate = computed(() => {
    const {lowers, lifts} = act.value;
    const {into, out} = phases.value;
    const top = px(0.27) - 6;
    return {y: top - 70 * (1 - partOf(into, lowers)) - 90 * partOf(out, lifts)};
});

// the vacuum: the canister on the floor beside it, its hose up to the nozzle in the hand, and the words flying in to the nozzle
const vacuumed = computed(() => {
    const {held, into, out: off} = phases.value;
    const on = into * (1 - off);
    const canister = {x: middle.value + out.value * px(0.44), y: floor.value};
    const nozzle = {x: hand.value.x + out.value * 7, y: hand.value.y + 4};
    const words = Array.from({length: act.value.words}, (_, index) => {
        const k = ((held ?? 0) * 2 + index / act.value.words) % 1;
        const from = {x: nozzle.x + out.value * (70 + 12 * (index % 3)), y: nozzle.y - 30 + 13 * index};
        return {x: from.x + (nozzle.x - from.x) * k ** 1.6, y: from.y + (nozzle.y - from.y) * k ** 1.6, size: 1 - 0.7 * k, word: ["abc", "the", "ok", "do", "fix"][index]};
    });
    return {on, canister, nozzle, words: held === null ? [] : words, hose: `M${canister.x} ${canister.y - 12}Q${canister.x} ${nozzle.y + 30} ${nozzle.x - out.value * 6} ${nozzle.y}`};
});

// the steam rising off the head of a figure fuming, puff after puff from either side
// the little cloud rising from the rubbing hands: puffs drifting up and fading, one after another, and a few sparkles twinkling among
// them, each at its place from the hands in pixels; empty outside the act's puff
const SPARKLES = [[-9, -12], [8, -18], [1, -26]];
const rub = computed(() => {
    const k = (props.u - act.value.puff[0]) / (act.value.puff[1] - act.value.puff[0]);
    if (k <= 0 || k >= 1) return null;
    const fade = Math.min(k * 6, 1, (1 - k) * 6);
    const puffs = Array.from({length: 5}, (_, index) => {
        const rise = (k * 3 + index / 5) % 1;
        return {x: (index - 2) * 3 + 3 * Math.sin(rise * 6 + index), y: -4 - 16 * rise, r: 2 + 3.5 * rise, fade: fade * (1 - rise) * 0.85};
    });
    const sparkles = SPARKLES.map(([x, y], index) => ({x, y, size: 2.6 * Math.max(Math.sin(Math.PI * ((k * 4 + index / 3) % 1)), 0), fade}));
    return {x: hand.value.x, y: hand.value.y, puffs, sparkles};
});

const steam = computed(() => {
    const k = (props.u - act.value.steam[0]) / (act.value.steam[1] - act.value.steam[0]);
    if (k <= 0 || k >= 1) return [];
    return Array.from({length: 6}, (_, index) => {
        const rise = (k * 3 + index / 6) % 1;
        const side = index % 2 ? 1 : -1;
        return {x: head.value.x + side * (12 + 10 * rise), y: head.value.y - 14 - 26 * rise, r: 2.5 + 4 * rise, fade: 1 - rise};
    });
});

// the corner of the floor lifted beside the figure, hinged at its far end
const flap = computed(() => {
    const {lift, down, open} = act.value;
    const lifted = partOf(props.u, lift) * (1 - partOf(props.u, down));
    const hinge = middle.value + out.value * px(0.56);
    const length = px(0.32);
    const turn = (open * lifted * Math.PI) / 180;
    return {hinge, length, lifted, end: {x: hinge - out.value * length * Math.cos(turn), y: floor.value - length * Math.sin(turn)}};
});
</script>

<template>
    <svg class="figure-act" :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" aria-hidden="true" :data-act="name">
        <g :stroke="COLOURS.ink" stroke-width="1" stroke-linejoin="round">
            <template v-if="name === 'ask_sign' && u > act.raise[0] && u < act.lower[1]">
                <g :transform="`translate(${hand.x} ${hand.y}) rotate(${waggle})`">
                    <rect x="-1.2" y="-22" width="2.4" height="26" :fill="COLOURS.wood" />
                    <rect x="-12" y="-40" width="24" height="20" rx="2" :fill="COLOURS.paper" stroke-width="1.4" />
                    <text x="0" y="-24.5" text-anchor="middle" class="figure-act-mark" :fill="COLOURS.ink" stroke="none">?</text>
                </g>
            </template>

            <template v-if="name === 'scroll' && u > act.raise[0] && u < act.lower[1]">
                <path :d="scrollHeld.parchment" :fill="PARCHMENT_BACK" stroke-width="0.8" data-scroll-parchment />
                <rect v-for="(roller, index) in [scrollHeld.top, scrollHeld.bottom]" :key="`roller${index}`" :x="roller.x - scrollHeld.half - 1" :y="roller.y - ROLLER / 2" :width="2 * scrollHeld.half + 2" :height="ROLLER" :rx="ROLLER / 2" :fill="COLOURS.wood" :data-scroll-roller="index ? 'bottom' : 'top'" />
            </template>

            <template v-if="name === 'ponder' && cloud">
                <g :opacity="cloud.shown" data-thought-cloud>
                    <circle v-for="(puff, index) in cloud.rising" :key="`puff${index}`" :cx="puff.x" :cy="puff.y" :r="puff.r" :fill="COLOURS.paper" stroke-width="0.8" />
                    <g v-if="cloud.grown" :opacity="cloud.grown">
                        <circle v-for="(bump, index) in cloud.bumps" :key="`bump${index}`" :cx="bump.x" :cy="bump.y" :r="bump.r" :fill="COLOURS.paper" stroke-width="0.9" />
                        <circle v-for="(bump, index) in cloud.bumps" :key="`fill${index}`" :cx="bump.x" :cy="bump.y" :r="bump.r - 0.8" :fill="COLOURS.paper" stroke="none" />
                        <circle v-for="(dot, index) in cloud.dots" :key="`dot${index}`" :cx="dot.x" :cy="dot.y" :r="dot.r" :fill="COLOURS.ink" stroke="none" :opacity="dot.lit" data-thought-dot />
                    </g>
                </g>
            </template>

            <template v-if="name === 'file_card' && stand">
                <g v-if="filed < 1 && u > act.reach[0]" :transform="`translate(${hand.x} ${hand.y + 3 + 6 * filed})`">
                    <rect x="-6" y="-4" width="12" height="8" :fill="COLOURS.paper" stroke-width="0.7" />
                    <path d="M-4 -1.5h8M-4 1h6" stroke-width="0.5" />
                </g>
                <g :transform="growing">
                    <rect :x="stand.x - 12" :y="stand.top" :width="24" :height="floor - stand.top" rx="1" :fill="COLOURS.wood" />
                    <rect :x="stand.x - 10" :y="stand.top + 2 - 5 * drawer" width="20" :height="5 * drawer" fill="#5b3a1c" stroke-width="0.6" />
                    <rect :x="stand.x - 10 - 1.5 * drawer" :y="stand.top + 2" :width="20 + 3 * drawer" height="10" rx="1" :fill="COLOURS.wood" />
                    <rect :x="stand.x - 10" :y="stand.top + 14" width="20" height="10" rx="1" :fill="COLOURS.wood" />
                    <path :d="`M${stand.x - 3} ${stand.top + 7}h6M${stand.x - 3} ${stand.top + 19}h6`" stroke-width="1.4" />
                </g>
            </template>

            <template v-if="name === 'binoculars'">
                <g :transform="`translate(${head.x} ${head.y + 1})`">
                    <rect x="-1.5" y="-1.6" width="3" height="3.2" :fill="COLOURS.ink" />
                    <circle cx="-4.6" cy="0" r="3.8" :fill="COLOURS.ink" stroke="#a9adb8" stroke-width="0.8" />
                    <circle cx="4.6" cy="0" r="3.8" :fill="COLOURS.ink" stroke="#a9adb8" stroke-width="0.8" />
                </g>
            </template>

            <template v-if="name === 'flashlight'">
                <ellipse :cx="corner.x" :cy="corner.y" rx="30" ry="20" fill="url(#figure-act-dark)" stroke="none" />
                <path :d="beam.path" :fill="COLOURS.light" stroke="none" opacity="0.5" />
                <ellipse :cx="beam.lit.x" :cy="beam.lit.y" rx="3" ry="8" :fill="COLOURS.light" stroke="none" opacity="0.7" />
                <g :transform="`translate(${hand.x} ${hand.y}) rotate(${Math.atan2(beam.lit.y - beam.tip.y, beam.lit.x - beam.tip.x) * 57.3})`">
                    <rect x="-4" y="-1.6" width="9" height="3.2" rx="1" fill="#35374b" />
                    <rect x="5" y="-2.4" width="2.4" height="4.8" :fill="COLOURS.gold" />
                </g>
            </template>

            <template v-if="name === 'hand_rub' && rub">
                <g class="figure-act-rub" :transform="`translate(${rub.x} ${rub.y})`">
                    <template v-for="(puff, index) in rub.puffs" :key="`puff${index}`">
                        <circle :cx="puff.x" :cy="puff.y" :r="puff.r" :fill="COLOURS.smoke" stroke="#a9adb8" stroke-width="0.5" :opacity="puff.fade" />
                    </template>
                    <template v-for="(sparkle, index) in rub.sparkles" :key="`sparkle${index}`">
                        <path :d="`M${sparkle.x} ${sparkle.y - sparkle.size * 2}L${sparkle.x + sparkle.size * 0.5} ${sparkle.y - sparkle.size * 0.5}L${sparkle.x + sparkle.size * 2} ${sparkle.y}L${sparkle.x + sparkle.size * 0.5} ${sparkle.y + sparkle.size * 0.5}L${sparkle.x} ${sparkle.y + sparkle.size * 2}L${sparkle.x - sparkle.size * 0.5} ${sparkle.y + sparkle.size * 0.5}L${sparkle.x - sparkle.size * 2} ${sparkle.y}L${sparkle.x - sparkle.size * 0.5} ${sparkle.y - sparkle.size * 0.5}Z`" :fill="COLOURS.light" stroke="none" :opacity="sparkle.fade" />
                    </template>
                </g>
            </template>

            <template v-if="name === 'fume'">
                <circle v-for="(puff, index) in steam" :key="index" :cx="puff.x" :cy="puff.y" :r="puff.r" fill="#e9e7e1" stroke="#a9adb8" stroke-width="0.6" :opacity="puff.fade" />
            </template>

            <template v-if="name === 'bug_shot'">
                <g v-if="bug.alive" :transform="`translate(${bug.x} ${bug.y - 2}) scale(${-hand.out * 1.5} 1.5)`">
                    <path :d="`M-3 -3l-3 ${-2 + bug.legs}M-3 0h-4M-3 3l-3 ${2 - bug.legs}M3 -3l3 ${-2 - bug.legs}M3 0h4M3 3l3 ${2 + bug.legs}`" :stroke="COLOURS.ink" stroke-width="1.1" />
                    <ellipse cx="0" cy="0" rx="5" ry="3.6" fill="#7a5232" />
                    <circle cx="5" cy="0" r="2" fill="#7a5232" />
                </g>
                <path v-if="bug.splat" :transform="`translate(${bug.x} ${bug.y}) scale(${1.3 - 0.3 * bug.splat})`" :opacity="bug.splat" d="M-9 0q2-6 6-3 1-6 5-2 5-3 5 2 5 1 2 4 3 4-3 3-4 4-7 1-3 0-6-1-6-4-4-3 0-3Z" fill="#9bd34a" stroke="#5f8f24" stroke-width="0.8" />
                <g v-if="bug.aimed" :transform="`translate(${hand.x} ${hand.y}) rotate(${bug.angle})`" :opacity="bug.aimed">
                    <rect x="-16" y="-2.5" width="13" height="5" rx="1.5" :fill="COLOURS.wood" />
                    <rect x="-4" y="-3" width="20" height="5" rx="1" :fill="COLOURS.ink" />
                    <path d="M4 2q1 6 5 8l3-1q-3-3-3-7Z" :fill="COLOURS.ink" />
                    <rect x="16" y="-1.8" width="14" height="2.2" :fill="COLOURS.ink" />
                    <path v-if="bug.firing" d="M30 -0.7l9 -5 -3 5 5 2 -6 1 3 5Z" :fill="COLOURS.gold" />
                </g>
                <template v-for="(drop, index) in bug.drops" :key="index">
                    <g class="figure-act-lens" :opacity="drop.fade">
                        <rect :x="drop.x - drop.r * 0.25" :y="drop.y" :width="drop.r * 0.5" :height="drop.run" rx="2" fill="#9bd34a" opacity="0.8" />
                        <circle :cx="drop.x" :cy="drop.y + drop.run" :r="drop.r * 0.4" fill="#9bd34a" />
                        <circle :cx="drop.x" :cy="drop.y" :r="drop.r" fill="#9bd34a" opacity="0.85" />
                        <circle :cx="drop.x - drop.r * 0.3" :cy="drop.y - drop.r * 0.3" :r="drop.r * 0.25" fill="#e8ffd0" opacity="0.8" />
                    </g>
                </template>
            </template>

            <template v-if="name === 'disco' && disco">
                <line :x1="disco.x" :y1="disco.top" :x2="disco.x" :y2="disco.y - disco.r" :stroke="COLOURS.silver" stroke-width="1" />
                <clipPath id="figure-act-ball">
                    <circle :cx="disco.x" :cy="disco.y" :r="disco.r" />
                </clipPath>
                <circle :cx="disco.x" :cy="disco.y" :r="disco.r" fill="#8d93a3" />
                <g clip-path="url(#figure-act-ball)">
                    <template v-for="(tile, index) in disco.tiles" :key="index">
                        <rect :x="tile.x - disco.r * 0.18" :y="tile.y - disco.r * 0.18" :width="disco.r * 0.36" :height="disco.r * 0.36" :fill="tile.light ? '#f4f6fb' : '#b9bfcc'" />
                    </template>
                </g>
                <circle :cx="disco.x" :cy="disco.y" :r="disco.r" fill="none" :stroke="COLOURS.ink" stroke-width="0.8" />
                <template v-for="(fleck, index) in disco.flecks" :key="`fleck${index}`">
                    <circle :cx="fleck.x" :cy="fleck.y" r="2.2" :fill="fleck.colour" opacity="0.85" />
                </template>
            </template>

            <template v-if="name === 'pogo' && stick.shown">
                <g :transform="`translate(${middle} ${stick.foot + stick.fall}) rotate(${stick.turn}) scale(${stick.shown})`">
                    <line x1="0" :y1="stick.top" x2="0" :y2="stick.bottom" :stroke="COLOURS.silver" stroke-width="2.6" stroke-linecap="round" />
                    <line :x1="-stick.bar" :y1="stick.top" :x2="stick.bar" :y2="stick.top" :stroke="COLOURS.silver" stroke-width="3" stroke-linecap="round" />
                    <line :x1="-stick.peg" y1="-1" :x2="stick.peg" y2="-1" :stroke="COLOURS.red" stroke-width="2.4" stroke-linecap="round" />
                    <path :d="stick.spring" :stroke="COLOURS.gold" stroke-width="1.2" fill="none" />
                </g>
            </template>

            <template v-if="name === 'rope_swing'">
                <template v-for="x in swing.ropes" :key="x">
                    <line :x1="x" :y1="swing.top" :x2="x" :y2="swing.reach" :stroke="COLOURS.rope" stroke-width="1.4" stroke-linecap="round" />
                    <circle :cx="x" :cy="swing.top" r="1.8" :fill="COLOURS.rope" />
                </template>
                <rect v-if="swing.down > 0.95" :x="middle - swing.seat / 2" :y="swing.line - 1" :width="swing.seat" height="3" rx="1" :fill="COLOURS.wood" stroke-width="0.6" />
            </template>

            <template v-if="name === 'chute'">
                <g :transform="`rotate(${act.sway * Math.sin(2 * Math.PI * u)} ${head.x} ${head.y})`">
                    <path :d="`M${head.x - 30} ${head.y - 44}L${head.x - 9} ${head.y - 14}M${head.x + 30} ${head.y - 44}L${head.x + 9} ${head.y - 14}M${head.x - 12} ${head.y - 46}L${head.x - 4} ${head.y - 14}M${head.x + 12} ${head.y - 46}L${head.x + 4} ${head.y - 14}`" stroke-width="0.6" fill="none" />
                    <path :d="`M${head.x - 32} ${head.y - 44}Q${head.x} ${head.y - 92} ${head.x + 32} ${head.y - 44}Q${head.x + 16} ${head.y - 50} ${head.x} ${head.y - 46}Q${head.x - 16} ${head.y - 50} ${head.x - 32} ${head.y - 44}Z`" :fill="COLOURS.red" />
                    <path :d="`M${head.x} ${head.y - 46}Q${head.x - 2} ${head.y - 70} ${head.x} ${head.y - 69}`" stroke-width="0.6" fill="none" />
                    <path :d="`M${head.x - 16} ${head.y - 48}Q${head.x - 13} ${head.y - 68} ${head.x - 6} ${head.y - 67}L${head.x} ${head.y - 46}`" :fill="COLOURS.paper" stroke-width="0.6" />
                    <path :d="`M${head.x + 16} ${head.y - 48}Q${head.x + 13} ${head.y - 68} ${head.x + 6} ${head.y - 67}L${head.x} ${head.y - 46}`" :fill="COLOURS.paper" stroke-width="0.6" />
                </g>
            </template>

            <template v-if="name === 'pack_box'">
                <g v-if="!box.popped && box.grown > 0" :transform="`translate(${box.x} ${floor}) scale(${box.grown})`">
                    <path :d="`M${-box.width / 2} ${-box.height}l-12 -9 4 -4 8 13Z`" fill="#b88a55" />
                    <path :d="`M${box.width / 2} ${-box.height}l12 -9 -4 -4 -8 13Z`" fill="#b88a55" />
                    <rect :x="-box.width / 2" :y="-box.height" :width="box.width" :height="box.height" fill="#c89b63" />
                    <path :d="`M${-box.width / 2} ${-box.height + 5}H${box.width / 2}`" stroke-width="0.6" />
                    <rect x="-7" :y="-box.height + 8" width="14" height="6" fill="#e8d4b0" stroke-width="0.6" />
                </g>
                <g v-if="box.popped && box.puff < 1" :transform="`translate(${box.x} ${floor - 18})`" :opacity="1 - box.puff">
                    <circle v-for="(way, index) in [-2.4, -1.6, -0.8, 0, 0.8, 1.6, 2.4]" :key="index" :cx="Math.sin(way) * 30 * box.puff" :cy="-Math.cos(way) * 16 * box.puff" :r="8 + 8 * box.puff" fill="#e9e7e1" stroke="#a9adb8" stroke-width="0.8" />
                    <rect v-for="index in 4" :key="`bit${index}`" :x="(index - 2.5) * 22 * box.puff" :y="-20 * box.puff + 30 * box.puff * box.puff" width="7" height="4" fill="#c89b63" :transform="`rotate(${index * 70 * box.puff})`" />
                </g>
            </template>

            <template v-if="name === 'press'">
                <rect :x="middle - 2" :y="plate.y - 200" width="4" height="200" fill="#a9adb8" />
                <rect :x="middle - 22" :y="plate.y" width="44" height="6" rx="1" fill="#6b6f7c" />
            </template>

            <template v-if="name === 'vacuum' && vacuumed.on > 0">
                <path :d="vacuumed.hose" fill="none" stroke-width="2.6" :stroke="COLOURS.ink" />
                <path :d="vacuumed.hose" fill="none" stroke-width="1.4" stroke="#6366f1" />
                <rect :x="vacuumed.canister.x - 9" :y="vacuumed.canister.y - 16" width="18" height="14" rx="4" fill="#ef476f" />
                <circle :cx="vacuumed.canister.x - 5" :cy="vacuumed.canister.y - 2" r="2.5" :fill="COLOURS.ink" />
                <circle :cx="vacuumed.canister.x + 5" :cy="vacuumed.canister.y - 2" r="2.5" :fill="COLOURS.ink" />
                <g :transform="`translate(${vacuumed.nozzle.x} ${vacuumed.nozzle.y}) scale(${out} 1)`">
                    <path d="M-6 -1.6H2L6 -4.5V4.5L2 1.6H-6Z" fill="#35374b" />
                </g>
                <text v-for="(word, index) in vacuumed.words" :key="index" :x="word.x" :y="word.y" :font-size="7 * word.size" text-anchor="middle" class="figure-act-word" stroke="none" :fill="COLOURS.paper">{{ word.word }}</text>
            </template>

            <template v-if="name === 'peek_under' && flap.lifted > 0">
                <rect :x="Math.min(flap.hinge, flap.hinge - out * flap.length)" :y="floor" :width="flap.length" height="7" fill="#0b0c10" stroke="none" />
                <path :d="`M${flap.hinge} ${floor}L${flap.end.x} ${flap.end.y}`" class="figure-act-floor" stroke-width="3.4" stroke-linecap="round" />
                <path :d="`M${flap.hinge} ${floor}L${flap.end.x} ${flap.end.y}`" fill="none" stroke-width="0.8" />
            </template>
        </g>
        <defs>
            <radialGradient id="figure-act-dark">
                <stop offset="0" stop-color="#0b0c10" stop-opacity="0.85" />
                <stop offset="0.7" stop-color="#0b0c10" stop-opacity="0.55" />
                <stop offset="1" stop-color="#0b0c10" stop-opacity="0" />
            </radialGradient>
        </defs>
    </svg>
</template>

<style scoped>
.figure-act {
    position: absolute;
    left: 0;
    top: 0;
    overflow: visible;
    pointer-events: none;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
}

/* a drop of the bug's splatter on the screen, soft as a drop on a camera's lens is */
.figure-act-lens {
    filter: blur(0.7px);
}

.figure-act-mark {
    font: 800 15px/1 var(--mono, monospace);
}

.figure-act-word {
    font-family: var(--mono, monospace);
    font-weight: 700;
    paint-order: stroke;
}

.figure-act-floor {
    stroke: color-mix(in srgb, var(--text) 25%, var(--bg));
}
</style>
