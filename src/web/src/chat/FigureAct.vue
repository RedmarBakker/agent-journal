<script setup>
import {computed} from "vue";
import {ACTS, heldPhases, partOf, standingAt} from "../figure/acts.js";

// What the figure holds and what grows beside it while it acts out a journal moment or a search (figure/acts.js), drawn over its picture:
// the act `name`, `u` of the way through it, 0 to 1; the free hand's grip, the eyes and the feet as shares of the picture (`hand.out` the
// way across the picture the free hand's side is, 1 to the right); the picture `size` pixels square; and `room`, the pixels from its left
// and right sides to the screen's edges, which a runner runs off past.
const props = defineProps({
    name: {type: String, required: true},
    u: {type: Number, required: true},
    hand: {type: Object, required: true},
    head: {type: Object, required: true},
    feet: {type: Number, required: true},
    size: {type: Number, required: true},
    room: {type: Object, required: true},
});

// Where what stands beside the figure stands, as shares of the picture: across from its middle, toward the free hand, and the height of
// its top above the feet; and the drawings' sizes and colours, in pixels
const STANDS = {post_mailbox: {across: 0.25, top: 0.4}, stamp: {across: 0.25, top: 0.32}, pin_note: {across: 0.31, top: 0.56}, file_card: {across: 0.24, top: 0.3}};
const COLOURS = {ink: "#272936", paper: "#f6f1e3", red: "#d9413b", green: "#2f9e44", wood: "#8a5a2b", cork: "#c99a5b", note: "#f5d547", gold: "#e8b84a", dove: "#fbfbf7", light: "#fff3a8"};
const CONFETTI = ["#6366f1", "#e8b84a", "#ef476f", "#06d6a0", "#118ab2"];

const act = computed(() => ACTS[props.name]);
const px = (share) => share * props.size;
const hand = computed(() => ({x: px(props.hand.x), y: px(props.hand.y), out: props.hand.out}));
const head = computed(() => ({x: px(props.head.x), y: px(props.head.y)}));
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

// the dove: flying in to the envelope held up beside the head, and off with it, its wings beating
const dove = computed(() => {
    const {comes, taken, goes} = act.value;
    if (props.u < comes[0] || props.u > goes[1]) return null;
    const held = {x: head.value.x + out.value * 21, y: head.value.y - 16};
    const from = {x: held.x + out.value * 80, y: held.y - 70};
    const away = {x: held.x + out.value * (props.room[out.value > 0 ? "right" : "left"] + 60), y: held.y - 150};
    const k = props.u < taken ? partOf(props.u, comes) : partOf(props.u, goes) ** 2;
    const [a, b] = props.u < taken ? [from, held] : [held, away];
    return {x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, way: props.u < taken ? -out.value : out.value, wings: Math.sin(props.u * 60), carrying: props.u >= taken};
});

// the mailbox's flag goes up once the letter is in; the letter goes in behind the box's front
const flagUp = computed(() => props.u >= act.value.flag);
const posted = computed(() => props.u >= act.value.posted[1]);

// the stamp's mark on the sheet, popping in as it lands
const stamped = computed(() => (props.u >= act.value.stamped ? Math.min((props.u - act.value.stamped) / 0.05, 1) : 0));

// the note pinned to the board where the hand left it
const pinned = computed(() => props.u >= act.value.pinned);

// the sign over its head on a stick, tipping as it waggles
const waggle = computed(() => {
    const [from, to] = act.value.waggle;
    const k = Math.min(Math.max((props.u - from) / (to - from), 0), 1);
    return 14 * Math.sin(2 * Math.PI * act.value.waggles * k) * Math.sin(Math.PI * k);
});

// the runner: from beside the figure's feet off past the screen's edge, its legs going
const runner = computed(() => {
    const k = partOf(props.u, act.value.runs);
    if (k <= 0 || k >= 1) return null;
    const far = props.room[out.value > 0 ? "right" : "left"] + props.size / 2 + 20;
    return {x: middle.value + out.value * (14 + far * k ** 1.4), stride: Math.sin(2 * Math.PI * act.value.strides * k)};
});

// how far the scroll has unrolled, 0 to 1
const unrolled = computed(() => partOf(props.u, act.value.unrolls) * (1 - partOf(props.u, act.value.rolls)));

// the drawer slid out, 0 to 1, and the card dropped into it
const drawer = computed(() => partOf(props.u, act.value.opens) * (1 - partOf(props.u, act.value.shuts)));
const filed = computed(() => partOf(props.u, act.value.filed));

// confetti bursting from `from` over `burst`: each piece out along its own way, falling as it goes
function confettiFrom(from, burst, reach, count) {
    const k = partOf(props.u, burst);
    if (k <= 0 || k >= 1) return [];
    return Array.from({length: count}, (_, index) => {
        const way = -Math.PI / 2 + (index / (count - 1) - 0.5) * 2.4;
        const far = reach * Math.sqrt(k) * (0.6 + 0.4 * ((index * 7) % count) / count);
        return {x: from.x + Math.cos(way) * far, y: from.y + Math.sin(way) * far + 50 * k * k, spin: 720 * k + index * 40, colour: CONFETTI[index % CONFETTI.length], fade: 1 - k ** 3};
    });
}
const cheered = computed(() => (props.name === "cheer" ? confettiFrom({x: head.value.x, y: head.value.y - 30}, act.value.burst, 44, 18) : []));

// the cannon held up and out in the free hand, its mouth where the confetti comes out of
const cannon = computed(() => {
    const tip = {x: hand.value.x + out.value * 9, y: hand.value.y - 14};
    return {tip, confetti: confettiFrom(tip, act.value.burst, 60, 24)};
});

// the party horn at the mouth: unrolled with each blow, coiled up between them
const horn = computed(() => {
    const blown = Math.max(...act.value.blows.map((blow) => Math.sin(Math.PI * Math.min(Math.max((props.u - blow[0]) / (blow[1] - blow[0]), 0), 1))));
    const up = partOf(props.u, act.value.raise) * (1 - partOf(props.u, act.value.lower));
    return {x: head.value.x + out.value * 4, y: head.value.y + 9, length: 4 + 24 * blown, coil: 5 * (1 - blown) + 1, up};
});

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
            <template v-if="name === 'post_dove'">
                <g v-if="!dove?.carrying && u > act.raise[0]" :transform="`translate(${hand.x} ${hand.y - 10})`">
                    <rect x="-7" y="-5" width="14" height="10" rx="1" :fill="COLOURS.paper" />
                    <path d="M-7 -5 0 1 7 -5" fill="none" />
                </g>
                <g v-if="dove" :transform="`translate(${dove.x} ${dove.y}) scale(${1.5 * dove.way} 1.5)`">
                    <g v-if="dove.carrying" transform="translate(0 8)">
                        <rect x="-6" y="-4" width="12" height="8" rx="1" :fill="COLOURS.paper" />
                        <path d="M-6 -4 0 0.8 6 -4" fill="none" />
                    </g>
                    <ellipse cx="0" cy="0" rx="8" ry="4.5" :fill="COLOURS.dove" />
                    <circle cx="7" cy="-3" r="3" :fill="COLOURS.dove" />
                    <path d="M10 -3.4 13 -2.6 10 -1.8Z" :fill="COLOURS.gold" />
                    <path d="M-8 0 -13 -2.5 -12 2Z" :fill="COLOURS.dove" />
                    <path :d="`M-2 -2 Q-4 ${-12 * dove.wings} 6 ${-14 * dove.wings} Q3 ${-5 * dove.wings} 3 -2Z`" :fill="COLOURS.dove" />
                </g>
            </template>

            <template v-if="name === 'post_mailbox' && stand">
                <g v-if="!posted && u > act.reach[0]" :transform="`translate(${hand.x} ${hand.y})`">
                    <rect x="-6" y="-4" width="12" height="8" rx="1" :fill="COLOURS.paper" />
                    <path d="M-6 -4 0 0.8 6 -4" fill="none" />
                </g>
                <g :transform="growing">
                    <rect :x="stand.x - 2" :y="stand.top + 12" width="4" :height="floor - stand.top - 12" :fill="COLOURS.wood" />
                    <rect :x="stand.x - 9" :y="stand.top + 11" width="18" height="3" :fill="COLOURS.wood" />
                    <path :d="`M${stand.x - 8} ${stand.top + 11}V${stand.top + 5}a8 5 0 0 1 16 0V${stand.top + 11}Z`" :fill="COLOURS.red" />
                    <path :d="`M${stand.x - 5} ${stand.top + 5}h10`" stroke-width="1.6" />
                    <g :transform="`rotate(${flagUp ? 0 : 90 * -out} ${stand.x + out * 8} ${stand.top + 9})`">
                        <path :d="`M${stand.x + out * 8} ${stand.top + 9}V${stand.top - 2}h${out * 5}v4h${-out * 5}`" :fill="COLOURS.gold" />
                    </g>
                </g>
            </template>

            <template v-if="name === 'stamp' && stand">
                <g :transform="growing">
                    <rect :x="stand.x - 2" :y="stand.top + 3" width="4" :height="floor - stand.top - 3" :fill="COLOURS.wood" />
                    <path :d="`M${stand.x - 14} ${stand.top + 4}L${stand.x - 10} ${stand.top - 2}H${stand.x + 14}L${stand.x + 10} ${stand.top + 4}Z`" :fill="COLOURS.wood" />
                    <path :d="`M${stand.x - 10} ${stand.top + 2.5}L${stand.x - 7} ${stand.top - 1}H${stand.x + 11}L${stand.x + 8} ${stand.top + 2.5}Z`" :fill="COLOURS.paper" stroke-width="0.6" />
                    <g v-if="stamped" :transform="`translate(${stand.x + 1} ${stand.top + 0.8}) scale(${1.4 - 0.4 * stamped} ${(1.4 - 0.4 * stamped) * 0.42}) rotate(-8)`">
                        <rect x="-8" y="-6" width="16" height="12" rx="2" fill="none" :stroke="COLOURS.green" stroke-width="2" />
                        <path d="M-4.5 0 -1 3.5 5 -3.5" fill="none" :stroke="COLOURS.green" stroke-width="2.2" />
                    </g>
                </g>
                <g v-if="u > act.lift[0] && u < act.sinks[0]" :transform="`translate(${hand.x} ${hand.y})`">
                    <rect x="-3" y="-7" width="6" height="6" rx="3" :fill="COLOURS.wood" />
                    <rect x="-1.5" y="-1" width="3" height="5" :fill="COLOURS.wood" />
                    <rect x="-7" y="4" width="14" height="4" rx="1" :fill="COLOURS.wood" />
                    <rect x="-7" y="8" width="14" height="2" :fill="COLOURS.green" />
                </g>
            </template>

            <template v-if="name === 'pin_note' && stand">
                <g :transform="growing">
                    <rect :x="stand.x - 2" :y="stand.top + 20" width="4" :height="floor - stand.top - 20" :fill="COLOURS.wood" />
                    <rect :x="stand.x - 15" :y="stand.top" width="30" height="22" rx="1.5" :fill="COLOURS.cork" stroke-width="2.4" />
                    <g v-if="pinned">
                        <rect :x="stand.x - 5" :y="stand.top + 5" width="11" height="11" :fill="COLOURS.note" stroke-width="0.7" transform-origin="center" />
                        <path :d="`M${stand.x - 3} ${stand.top + 10}h7M${stand.x - 3} ${stand.top + 12.5}h5`" stroke-width="0.6" />
                        <circle :cx="stand.x + 0.5" :cy="stand.top + 6" r="1.6" :fill="COLOURS.red" stroke-width="0.6" />
                    </g>
                </g>
                <g v-if="!pinned && u > act.reach[0]" :transform="`translate(${hand.x} ${hand.y - 4})`">
                    <rect x="-5.5" y="-5.5" width="11" height="11" :fill="COLOURS.note" stroke-width="0.7" />
                    <path d="M-3.5 -0.5h7M-3.5 2h5" stroke-width="0.6" />
                </g>
            </template>

            <template v-if="name === 'ask_sign' && u > act.raise[0] && u < act.lower[1]">
                <g :transform="`translate(${hand.x} ${hand.y}) rotate(${waggle})`">
                    <rect x="-1.2" y="-22" width="2.4" height="26" :fill="COLOURS.wood" />
                    <rect x="-12" y="-40" width="24" height="20" rx="2" :fill="COLOURS.paper" stroke-width="1.4" />
                    <text x="0" y="-24.5" text-anchor="middle" class="figure-act-mark" :fill="COLOURS.ink" stroke="none">?</text>
                </g>
            </template>

            <template v-if="name === 'whistle_runner' && runner">
                <g :transform="`translate(${runner.x} ${floor}) scale(${out} 1)`" class="figure-act-runner" stroke-width="1.8" stroke-linecap="round" fill="none">
                    <circle cx="1.5" cy="-14.5" r="2.4" fill="currentColor" />
                    <path d="M1 -11.5 -1 -5.5" />
                    <path :d="`M-1 -5.5 ${-1 + 4 * runner.stride} 0M-1 -5.5 ${-1 - 4 * runner.stride} 0`" />
                    <path :d="`M0.6 -10 ${0.6 - 3.5 * runner.stride} -7M0.6 -10 ${0.6 + 3.5 * runner.stride} -8`" />
                </g>
            </template>

            <template v-if="name === 'scroll' && u > act.raise[0] && u < act.lower[1]">
                <g :transform="`translate(${hand.x} ${hand.y})`">
                    <rect x="-9" :y="0" width="18" :height="2 + 30 * unrolled" :fill="COLOURS.paper" stroke-width="0.8" />
                    <path v-for="line in Math.floor(6 * unrolled)" :key="line" :d="`M-6 ${2 + line * 4.4}h${line % 3 ? 12 : 8}`" stroke-width="0.6" />
                    <rect x="-11" y="-2" width="22" height="3.4" rx="1.7" :fill="COLOURS.wood" />
                    <rect x="-10" :y="30 * unrolled" width="20" height="3.4" rx="1.7" :fill="COLOURS.wood" />
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

            <template v-for="(piece, index) in [...cheered, ...(name === 'confetti_cannon' ? cannon.confetti : [])]" :key="index">
                <rect :x="piece.x - 2.5" :y="piece.y - 1.5" width="5" height="3" :fill="piece.colour" stroke="none" :opacity="piece.fade" :transform="`rotate(${piece.spin} ${piece.x} ${piece.y})`" />
            </template>

            <template v-if="name === 'confetti_cannon' && u > act.aim[0] && u < act.lower[1]">
                <g :transform="`translate(${hand.x} ${hand.y}) rotate(${-out * 28})`">
                    <path d="M-3 2 -4.5 -16H4.5L3 2Z" fill="#6366f1" />
                    <rect x="-5" y="-17" width="10" height="2.6" :fill="COLOURS.gold" />
                </g>
            </template>

            <template v-if="name === 'party_horn' && horn.up > 0">
                <g :transform="`translate(${horn.x} ${horn.y}) scale(${out} 1)`" :opacity="Math.min(horn.up * 3, 1)">
                    <path d="M0 -1.6 4 -1 4 1 0 1.6Z" :fill="COLOURS.gold" />
                    <rect x="4" y="-1.4" :width="horn.length" height="2.8" :fill="COLOURS.red" stroke-width="0.6" />
                    <circle :cx="4 + horn.length" :cy="-horn.coil + 1.4" :r="horn.coil" fill="none" :stroke="COLOURS.red" stroke-width="2.6" />
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

.figure-act-mark {
    font: 800 15px/1 var(--mono, monospace);
}

.figure-act-runner {
    color: var(--text);
    stroke: var(--text);
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
