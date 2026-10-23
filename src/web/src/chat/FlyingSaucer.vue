<script setup>
import {computed} from "vue";

// The small UFO that comes for the parcels once the work is committed: its middle at `x`, `y` on the page, in pixels, and under it a beam
// of light as strong as `beam`, 0 to 1, reaching `reach` pixels down and `width` pixels wide at its foot, as wide as what it lifts.
const props = defineProps({
    x: {type: Number, required: true},
    y: {type: Number, required: true},
    beam: {type: Number, default: 0},
    reach: {type: Number, default: 0},
    width: {type: Number, default: 34},
});

// the saucer's drawing, in pixels, and how wide the beam is where it leaves the saucer's belly
const SAUCER = {width: 36, height: 18, belly: 12};

const style = computed(() => ({left: `${props.x}px`, top: `${props.y}px`}));
// the beam as a trapezium from the belly down to its foot, in a box as wide as its foot
const beamBox = computed(() => ({
    left: `${-props.width / 2}px`,
    top: `${SAUCER.height / 2 - 2}px`,
    width: `${props.width}px`,
    height: `${props.reach}px`,
    opacity: props.beam,
}));
const beamPath = computed(() => {
    const [left, right] = [(props.width - SAUCER.belly) / 2, (props.width + SAUCER.belly) / 2];
    return `M${left} 0H${right}L${props.width} ${props.reach}H0Z`;
});
</script>

<template>
    <div class="flying-saucer" :style="style" aria-hidden="true">
        <template v-if="beam > 0">
            <svg class="flying-saucer-beam" :style="beamBox" :viewBox="`0 0 ${width} ${reach}`" :width="width" :height="reach">
                <defs>
                    <linearGradient id="flying-saucer-beam" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0" stop-color="#fff3a8" stop-opacity="0.85" />
                        <stop offset="1" stop-color="#fff3a8" stop-opacity="0.2" />
                    </linearGradient>
                </defs>
                <path :d="beamPath" fill="url(#flying-saucer-beam)" />
            </svg>
        </template>
        <svg class="flying-saucer-hull" viewBox="0 0 36 18" :width="SAUCER.width" :height="SAUCER.height">
            <path class="flying-saucer-dome" d="M11 9a7 7 0 0 1 14 0Z" />
            <ellipse class="flying-saucer-body" cx="18" cy="11" rx="17" ry="5" />
            <circle class="flying-saucer-light" cx="8" cy="12" r="1.4" />
            <circle class="flying-saucer-light" cx="18" cy="13.5" r="1.4" />
            <circle class="flying-saucer-light" cx="28" cy="12" r="1.4" />
        </svg>
    </div>
</template>

<style scoped>
.flying-saucer {
    position: fixed;
    z-index: 41;
    width: 0;
    height: 0;
    pointer-events: none;
}

.flying-saucer-beam {
    position: absolute;
    z-index: -1;
}

.flying-saucer-hull {
    position: absolute;
    left: -18px;
    top: -9px;
    overflow: visible;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
}

.flying-saucer-body {
    fill: #a9adb8;
    stroke: #272936;
    stroke-width: 0.8;
}

.flying-saucer-dome {
    fill: #cfe6ff;
    stroke: #272936;
    stroke-width: 0.8;
}

.flying-saucer-light {
    fill: #e8b84a;
    animation: flying-saucer-blink 600ms steps(2) infinite;
}

.flying-saucer-light:nth-of-type(2) {
    animation-delay: 200ms;
}

.flying-saucer-light:nth-of-type(3) {
    animation-delay: 400ms;
}

@keyframes flying-saucer-blink {
    50% {
        fill: #6366f1;
    }
}

@media (prefers-reduced-motion: reduce) {
    .flying-saucer-light {
        animation: none;
    }
}
</style>
