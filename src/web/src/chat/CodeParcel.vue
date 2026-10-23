<script setup>
import {computed, ref, watch} from "vue";

// A parcel of code the figure built, standing on the page with its base's middle at `x`, `y`, in pixels, `up` pixels higher on the pile
// it sits on, `scale` times its size and as opaque as `opacity`; it pops in as it appears, and hops up when it is pushed onto the pile.
// Each time `blows` goes up, a blow has landed on it: a cartoon cloud of dust puffs around it, and now and then a few bits fly out.
const props = defineProps({
    x: {type: Number, required: true},
    y: {type: Number, required: true},
    up: {type: Number, default: 0},
    scale: {type: Number, default: 1},
    opacity: {type: Number, default: 1},
    blows: {type: Number, default: 0},
});

// The dust of a blow: puffs of cloud around the parcel, each its place from the parcel's base's middle and its size, in pixels; the share
// of blows that throw bits out, how many at most, what they are, how far they fly and how fast they spin
const DUST = {
    clouds: [
        {x: -17, y: -5, size: 15},
        {x: -7, y: -2, size: 13},
        {x: 6, y: -3, size: 14},
        {x: 17, y: -6, size: 13},
        {x: -11, y: -15, size: 12},
        {x: 12, y: -17, size: 11},
        {x: 0, y: -22, size: 12},
    ],
    throws: 0.45,
    most: 3,
    bits: ["{", "}", ";", "</>", "=", "a", "x", "λ", "nail"],
    reach: [14, 30],
    spin: 540,
};

// the puffs in the air, each {id, bits}, every bit {id, text, dx, dy, spin}
const puffs = ref([]);
let puffed = 0;
const still = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function bitOf(id) {
    const angle = -Math.PI / 2 + (Math.random() - 0.5) * 2.2;
    const reach = DUST.reach[0] + Math.random() * (DUST.reach[1] - DUST.reach[0]);
    const text = DUST.bits[Math.floor(Math.random() * DUST.bits.length)];
    return {id, text, dx: Math.cos(angle) * reach, dy: Math.sin(angle) * reach, spin: (Math.random() - 0.5) * DUST.spin};
}

function puff() {
    const id = ++puffed;
    const thrown = Math.random() < DUST.throws ? 1 + Math.floor(Math.random() * DUST.most) : 0;
    puffs.value = [...puffs.value, {id, bits: Array.from({length: thrown}, (_, index) => bitOf(`${id}-${index}`))}];
}

// a puff is gone once its first cloud has faded, as they all fade together
const settled = (id) => (puffs.value = puffs.value.filter((each) => each.id !== id));

watch(
    () => props.blows,
    (now, before) => now > before && !still() && puff()
);

const cloudStyle = (cloud) => ({
    left: `${cloud.x - cloud.size / 2}px`,
    top: `${cloud.y - cloud.size / 2}px`,
    width: `${cloud.size}px`,
    height: `${cloud.size}px`,
});
const bitStyle = (bit) => ({"--dx": `${bit.dx}px`, "--dy": `${bit.dy}px`, "--spin": `${bit.spin}deg`});

// the lines of code on the parcel's front, each its row from the top and its indent and length in the drawing's units
const LINES = [
    {row: 0, indent: 0, length: 9},
    {row: 1, indent: 3, length: 8},
    {row: 2, indent: 3, length: 6},
    {row: 3, indent: 0, length: 5},
];

const style = computed(() => ({left: `${props.x}px`, top: `${props.y}px`}));
const placed = computed(() => ({transform: `translateY(${-props.up}px)`}));
const sized = computed(() => ({transform: `scale(${props.scale})`, opacity: props.opacity}));
</script>

<template>
    <div class="code-parcel" :style="style" aria-hidden="true">
        <div class="code-parcel-placed" :style="placed">
            <div class="code-parcel-sized" :style="sized">
                <svg class="code-parcel-box" viewBox="0 0 24 19" width="24" height="19">
                    <path class="code-parcel-top" d="M1 5 5 1h18l-4 4Z" />
                    <path class="code-parcel-side" d="M19 5l4-4v13l-4 4Z" />
                    <rect class="code-parcel-front" x="1" y="5" width="18" height="13" />
                    <path class="code-parcel-tape" d="M8 5 12 1h3l-4 4Z" />
                    <template v-for="line in LINES" :key="line.row">
                        <rect
                            :class="line.row % 2 ? 'code-parcel-accent' : 'code-parcel-ink'"
                            :x="4 + line.indent"
                            :y="7.5 + line.row * 2.4"
                            :width="line.length"
                            height="1.2"
                            rx="0.6"
                        />
                    </template>
                </svg>
            </div>
        </div>
        <template v-for="each in puffs" :key="each.id">
            <div class="code-parcel-dust" @animationend.once="settled(each.id)">
                <template v-for="cloud in DUST.clouds" :key="`${cloud.x}/${cloud.y}`">
                    <span class="code-parcel-cloud" :style="cloudStyle(cloud)" />
                </template>
                <template v-for="bit in each.bits" :key="bit.id">
                    <span class="code-parcel-bit" :style="bitStyle(bit)">
                        <template v-if="bit.text === 'nail'">
                            <svg viewBox="0 0 4 10" width="4" height="10"><path d="M0 0h4v1.5H2.6L2 10 1.4 1.5H0Z" /></svg>
                        </template>
                        <template v-else>{{ bit.text }}</template>
                    </span>
                </template>
            </div>
        </template>
    </div>
</template>

<style scoped>
.code-parcel {
    position: fixed;
    z-index: 39;
    width: 0;
    height: 0;
    pointer-events: none;
}

/* pushed onto the pile, the parcel hops up onto the parcels under it */
.code-parcel-placed {
    position: absolute;
    left: -12px;
    bottom: 0;
    width: 24px;
    height: 19px;
    transform-origin: 50% 100%;
    transition: transform 240ms cubic-bezier(0.3, 1.6, 0.5, 1);
}

.code-parcel-sized {
    transform-origin: 50% 100%;
}

/* the parcel fades in out of thin air, grows past its size and quickly settles back to it, as a cartoon's prop pops in */
.code-parcel-box {
    display: block;
    overflow: visible;
    transform-origin: 50% 100%;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
    animation: code-parcel-pop 520ms cubic-bezier(0.3, 0.7, 0.4, 1) both;
}

.code-parcel-box path,
.code-parcel-box rect.code-parcel-front {
    stroke: #272936;
    stroke-width: 0.8;
    stroke-linejoin: round;
}

.code-parcel-front {
    fill: #c99a5f;
}

.code-parcel-top {
    fill: #dcb27a;
}

.code-parcel-side {
    fill: #a87a45;
}

.code-parcel-tape {
    fill: #e3c58e;
}

.code-parcel-ink {
    fill: #272936;
}

.code-parcel-accent {
    fill: #6366f1;
}

@keyframes code-parcel-pop {
    0% {
        opacity: 0;
        transform: scale(0.2);
    }

    55% {
        opacity: 1;
        transform: scale(1.4);
    }

    78% {
        transform: scale(0.9);
    }

    100% {
        opacity: 1;
        transform: scale(1);
    }
}

/* a blow's dust puffs out around the parcel and fades, and its bits fly up and out in an arc, turning */
.code-parcel-dust {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 0;
    height: 0;
}

.code-parcel-cloud {
    position: absolute;
    border-radius: 50%;
    background: #ece6d8;
    box-shadow: 0 0 0 0.7px color-mix(in srgb, #272936 70%, transparent);
    animation: code-parcel-puff 560ms ease-out both;
}

@keyframes code-parcel-puff {
    0% {
        opacity: 0;
        transform: scale(0.3);
    }

    25% {
        opacity: 0.95;
    }

    100% {
        opacity: 0;
        transform: scale(1.35) translateY(-4px);
    }
}

.code-parcel-bit {
    position: absolute;
    left: -3px;
    top: -12px;
    font: 700 9px/1 var(--mono, monospace);
    color: #272936;
    text-shadow: 0 0 2px #f3eedf;
    animation: code-parcel-fly 560ms cubic-bezier(0.2, 0.6, 0.4, 1) both;
}

.code-parcel-bit svg {
    display: block;
    fill: #a9adb8;
    stroke: #272936;
    stroke-width: 0.5;
}

@keyframes code-parcel-fly {
    0% {
        opacity: 1;
        transform: translate(0, 0) rotate(0);
    }

    70% {
        opacity: 1;
    }

    100% {
        opacity: 0;
        transform: translate(var(--dx), calc(var(--dy) + 8px)) rotate(var(--spin));
    }
}

@media (prefers-reduced-motion: reduce) {
    .code-parcel-box {
        animation: none;
    }

    .code-parcel-placed {
        transition: none;
    }
}
</style>
