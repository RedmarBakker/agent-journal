<script setup>
import {computed, ref, watch} from "vue";
import {PARCEL, digitsOf} from "../figure/parcels.js";
import {VISOR} from "../figure/visor.js";

// A parcel the figure built, drawn as a flat near-black 1U server unit, standing on the page with its base's middle at `x`, `y`, in pixels,
// `up` pixels higher on the pile it sits on, `scale` times its size and as opaque as `opacity`; it pops in as it appears, and hops up when
// it is pushed onto the pile. Its status lights are `lights` (parcels.js lightsAfter): amber and blinking while the run goes, or green or
// red, the visor's own, once it has ended. Each time `blows` goes up, a blow has landed on it: a cartoon cloud of dust puffs around it,
// and a few 0 and 1 digits come out of it and drift in to the unit.
const props = defineProps({
    x: {type: Number, required: true},
    y: {type: Number, required: true},
    up: {type: Number, default: 0},
    scale: {type: Number, default: 1},
    opacity: {type: Number, default: 1},
    blows: {type: Number, default: 0},
    lights: {type: String, default: "amber"},
});

// The dust of a blow: puffs of cloud around the unit, each its place from the unit's base's middle and its size, in pixels
const CLOUDS = [
    {x: -17, y: -4, size: 14},
    {x: -7, y: -2, size: 12},
    {x: 6, y: -3, size: 13},
    {x: 17, y: -5, size: 12},
    {x: -11, y: -12, size: 11},
    {x: 12, y: -13, size: 10},
    {x: 0, y: -17, size: 11},
];

// the status lights along the front's left, each its middle across, and the vent slits along its right, each its left
const LIGHTS = [3.6, 5.8, 8, 10.2];
const VENTS = [12.4, 13.8, 15.2, 16.6];
// the lights' colours: amber while the run goes, and the visor's green and red once it has ended
const rgb = (colour) => `rgb(${colour.map((part) => Math.round(part * 255)).join(" ")})`;
const LIT = {amber: "#ffb020", good: rgb(VISOR.colours.good), bad: rgb(VISOR.colours.bad)};

// the puffs in the air, each {id, digits}, every digit {id, text, x, y}
const puffs = ref([]);
let puffed = 0;
const still = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function puff() {
    const id = ++puffed;
    puffs.value = [...puffs.value, {id, digits: digitsOf(Math.random).map((digit, index) => ({...digit, id: `${id}-${index}`}))}];
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
const digitStyle = (digit) => ({"--from-x": `${digit.x}px`, "--from-y": `${digit.y}px`, "--to-y": `${-PARCEL.height / 2}px`});

const style = computed(() => ({left: `${props.x}px`, top: `${props.y}px`}));
const placed = computed(() => ({transform: `translateY(${-props.up}px)`}));
const sized = computed(() => ({transform: `scale(${props.scale})`, opacity: props.opacity}));
const lit = computed(() => ({"--light": LIT[props.lights]}));
</script>

<template>
    <div class="code-parcel" :style="style" aria-hidden="true">
        <div class="code-parcel-placed" :style="placed">
            <div class="code-parcel-sized" :style="sized">
                <svg :class="['code-parcel-box', `lights-${lights}`]" :style="lit" :viewBox="`0 0 ${PARCEL.width} ${PARCEL.height}`" :width="PARCEL.width" :height="PARCEL.height">
                    <path class="code-parcel-top" d="M1 5 5 1h18l-4 4Z" />
                    <path class="code-parcel-side" d="M19 5l4-4v7l-4 4Z" />
                    <rect class="code-parcel-front" x="1" y="5" width="18" height="7" />
                    <template v-for="(at, index) in LIGHTS" :key="at">
                        <circle class="code-parcel-light" :cx="at" cy="8.5" r="0.85" :style="{animationDelay: `${index * -230}ms`}" />
                    </template>
                    <template v-for="at in VENTS" :key="at">
                        <rect class="code-parcel-vent" :x="at" y="6.8" width="0.6" height="3.4" />
                    </template>
                </svg>
            </div>
        </div>
        <template v-for="each in puffs" :key="each.id">
            <div class="code-parcel-dust" @animationend.once="settled(each.id)">
                <template v-for="cloud in CLOUDS" :key="`${cloud.x}/${cloud.y}`">
                    <span class="code-parcel-cloud" :style="cloudStyle(cloud)" />
                </template>
                <template v-for="digit in each.digits" :key="digit.id">
                    <span class="code-parcel-digit" :style="digitStyle(digit)">{{ digit.text }}</span>
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
    height: 13px;
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

/* edged a little lighter than the unit, so a near-black unit keeps its shape on a dark page */
.code-parcel-box path,
.code-parcel-box rect.code-parcel-front {
    stroke: #4a4e5c;
    stroke-width: 0.8;
    stroke-linejoin: round;
}

/* a near-black unit, its top a shade lighter and its side darker */
.code-parcel-front {
    fill: #1c1e25;
}

.code-parcel-top {
    fill: #2c2f39;
}

.code-parcel-side {
    fill: #121318;
}

.code-parcel-vent {
    fill: #050608;
}

/* the status lights glow in their colour; amber blinks while the run goes, each light out of step with the next */
.code-parcel-light {
    fill: var(--light);
    filter: drop-shadow(0 0 0.8px var(--light));
}

.lights-amber .code-parcel-light {
    animation: code-parcel-blink 920ms steps(1, end) infinite;
}

@keyframes code-parcel-blink {
    0% {
        opacity: 1;
    }

    50% {
        opacity: 0.25;
    }
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

/* the digits come out of the dust where they start and drift in to the unit's front, shrinking into it */
.code-parcel-digit {
    position: absolute;
    left: -2.5px;
    top: -4px;
    font: 800 8px/1 var(--mono, monospace);
    color: #8eeaff;
    text-shadow: 0 0 2px #1c1e25;
    animation: code-parcel-drift 620ms cubic-bezier(0.4, 0, 0.7, 1) both;
}

@keyframes code-parcel-drift {
    0% {
        opacity: 0;
        transform: translate(var(--from-x), var(--from-y)) scale(1);
    }

    25% {
        opacity: 1;
    }

    100% {
        opacity: 0.2;
        transform: translate(0, var(--to-y)) scale(0.4);
    }
}

@media (prefers-reduced-motion: reduce) {
    .code-parcel-box {
        animation: none;
    }

    .code-parcel-placed {
        transition: none;
    }

    .lights-amber .code-parcel-light {
        animation: none;
    }
}
</style>
