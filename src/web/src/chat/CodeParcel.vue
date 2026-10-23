<script setup>
import {computed, onMounted, watch} from "vue";

// The parcel of code the figure builds, standing on the page where its blows land, `x` along and `y` the top of the floor it stands on,
// in pixels; it pops in as it appears. Once `taken`, a small UFO flies in, lifts it up its beam and flies off with it, and the parcel is
// `gone`; with motion kept still it goes at once.
const props = defineProps({x: {type: Number, required: true}, y: {type: Number, required: true}, taken: {type: Boolean, default: false}});
const emit = defineEmits(["gone"]);

// the lines of code on the parcel's front, each its indent and length in the drawing's units, from the top down
const LINES = [
    [0, 9],
    [3, 8],
    [3, 6],
    [0, 5],
];

const still = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const goneNow = (taken) => taken && still() && emit("gone");
watch(() => props.taken, goneNow);
onMounted(() => goneNow(props.taken));

const style = computed(() => ({left: `${props.x}px`, top: `${props.y}px`}));
const flown = (event) => event.target === event.currentTarget && emit("gone");
</script>

<template>
    <div :class="['code-parcel', {taken}]" :style="style" aria-hidden="true">
        <svg class="code-parcel-box" viewBox="0 0 24 19" width="24" height="19">
            <path class="code-parcel-top" d="M1 5 5 1h18l-4 4Z" />
            <path class="code-parcel-side" d="M19 5l4-4v13l-4 4Z" />
            <rect class="code-parcel-front" x="1" y="5" width="18" height="13" />
            <path class="code-parcel-tape" d="M8 5 12 1h3l-4 4Z" />
            <template v-for="([indent, length], index) in LINES" :key="index">
                <rect :class="index % 2 ? 'code-parcel-accent' : 'code-parcel-ink'" :x="4 + indent" :y="7.5 + index * 2.4" :width="length" height="1.2" rx="0.6" />
            </template>
        </svg>
        <template v-if="taken">
            <div class="code-parcel-ufo" @animationend="flown">
                <svg class="code-parcel-beam" viewBox="0 0 40 60" width="40" height="118" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="code-parcel-beam" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0" stop-color="#fff3a8" stop-opacity="0.85" />
                            <stop offset="1" stop-color="#fff3a8" stop-opacity="0.2" />
                        </linearGradient>
                    </defs>
                    <path d="M14 0h12l14 60H0Z" fill="url(#code-parcel-beam)" />
                </svg>
                <svg class="code-parcel-saucer" viewBox="0 0 36 18" width="36" height="18">
                    <path class="code-parcel-dome" d="M11 9a7 7 0 0 1 14 0Z" />
                    <ellipse class="code-parcel-hull" cx="18" cy="11" rx="17" ry="5" />
                    <circle class="code-parcel-light" cx="8" cy="12" r="1.4" />
                    <circle class="code-parcel-light" cx="18" cy="13.5" r="1.4" />
                    <circle class="code-parcel-light" cx="28" cy="12" r="1.4" />
                </svg>
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

/* the parcel fades in out of thin air, grows past its size and quickly settles back to it, as a cartoon's prop pops in */
.code-parcel-box {
    position: absolute;
    left: -12px;
    bottom: 0;
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

/* taken: the parcel rises up the beam into the saucer, shrinking as it goes */
.code-parcel.taken .code-parcel-box {
    animation: code-parcel-lifted 4200ms ease-in-out both;
}

@keyframes code-parcel-lifted {
    0%,
    38% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }

    74% {
        opacity: 1;
        transform: translateY(-116px) scale(0.55);
    }

    78%,
    100% {
        opacity: 0;
        transform: translateY(-122px) scale(0.4);
    }
}

/* the saucer flies in from above to the right, hovers over the parcel above the figure's head with its beam on the parcel, and flies off
   up to the left */
.code-parcel-ufo {
    position: absolute;
    left: -18px;
    bottom: 118px;
    width: 36px;
    animation: code-parcel-flight 4200ms ease-in-out both;
}

@keyframes code-parcel-flight {
    0% {
        opacity: 0;
        transform: translate(180px, -160px) rotate(-12deg);
    }

    8% {
        opacity: 1;
    }

    30%,
    80% {
        transform: translate(0, 0) rotate(0);
    }

    92% {
        opacity: 1;
    }

    100% {
        opacity: 0;
        transform: translate(-220px, -200px) rotate(-14deg);
    }
}

.code-parcel-saucer {
    position: relative;
    display: block;
    overflow: visible;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
}

.code-parcel-hull {
    fill: #a9adb8;
    stroke: #272936;
    stroke-width: 0.8;
}

.code-parcel-dome {
    fill: #cfe6ff;
    stroke: #272936;
    stroke-width: 0.8;
}

.code-parcel-light {
    fill: #e8b84a;
    animation: code-parcel-blink 600ms steps(2) infinite;
}

.code-parcel-light:nth-of-type(2) {
    animation-delay: 200ms;
}

.code-parcel-light:nth-of-type(3) {
    animation-delay: 400ms;
}

@keyframes code-parcel-blink {
    50% {
        fill: #6366f1;
    }
}

/* the beam shines down from under the saucer onto the parcel while it hovers there */
.code-parcel-beam {
    position: absolute;
    left: -2px;
    top: 14px;
    opacity: 0;
    transform-origin: 50% 0;
    animation: code-parcel-beam 4200ms ease-in-out both;
}

@keyframes code-parcel-beam {
    0%,
    32% {
        opacity: 0;
        transform: scaleY(0.2);
    }

    40%,
    76% {
        opacity: 1;
        transform: scaleY(1);
    }

    82%,
    100% {
        opacity: 0;
        transform: scaleY(0.2);
    }
}

@media (prefers-reduced-motion: reduce) {
    .code-parcel-box,
    .code-parcel-light {
        animation: none;
    }
}
</style>
