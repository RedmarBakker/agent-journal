<script setup>
import {computed} from "vue";

// A parcel of code the figure built, standing on the page with its base's middle at `x`, `y`, in pixels, `up` pixels higher on the pile
// it sits on, `scale` times its size and as opaque as `opacity`; it pops in as it appears, and hops up when it is pushed onto the pile.
const props = defineProps({
    x: {type: Number, required: true},
    y: {type: Number, required: true},
    up: {type: Number, default: 0},
    scale: {type: Number, default: 1},
    opacity: {type: Number, default: 1},
});

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

@media (prefers-reduced-motion: reduce) {
    .code-parcel-box {
        animation: none;
    }

    .code-parcel-placed {
        transition: none;
    }
}
</style>
