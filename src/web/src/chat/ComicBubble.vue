<script setup>
import {computed} from "vue";
import {COMIC_BUBBLE, boilAt, bubbleOutline, bubbleSize} from "../figure/comicBubble.js";

// The phone call's speech bubble drawn as a comic strip's (figure/comicBubble.js): `rows` of its text in an inked outline at page `left` and
// `top`, its tail to `tip` in the bubble's own pixels, the outline boiling as the figure's `frame` goes on.
const props = defineProps({
    rows: {type: Array, required: true},
    left: {type: Number, required: true},
    top: {type: Number, required: true},
    tip: {type: Object, required: true},
    frame: {type: Number, required: true},
});

const size = computed(() => bubbleSize(props.rows));
const outline = computed(() => bubbleOutline(size.value.width, size.value.height, props.tip, boilAt(props.frame)));
const style = computed(() => ({
    left: `${props.left}px`,
    top: `${props.top}px`,
    width: `${size.value.width}px`,
    height: `${size.value.height}px`,
    fontSize: `${COMIC_BUBBLE.size}px`,
    lineHeight: `${COMIC_BUBBLE.line}px`,
    padding: `${COMIC_BUBBLE.pad}px`,
}));
</script>

<template>
    <div class="comic-bubble" :style="style" aria-hidden="true">
        <svg class="comic-bubble-drawing" :width="size.width" :height="size.height">
            <g class="comic-bubble-ink" :stroke-width="2 * COMIC_BUBBLE.ink">
                <path :d="outline.body" />
                <path :d="outline.tail" />
            </g>
            <g class="comic-bubble-fill">
                <path :d="outline.body" />
                <path :d="outline.tail" />
            </g>
        </svg>
        <template v-for="(row, index) in rows" :key="index">
            <span class="comic-bubble-row" :class="{'comic-bubble-strong': row.strong}">{{ row.text }}</span>
        </template>
    </div>
</template>

<style scoped>
.comic-bubble {
    position: fixed;
    z-index: 40;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    color: var(--text);
    font-family: inherit;
    white-space: nowrap;
    pointer-events: none;
}

.comic-bubble-drawing {
    position: absolute;
    left: 0;
    top: 0;
    overflow: visible;
}

.comic-bubble-ink {
    fill: var(--text);
    stroke: var(--text);
    stroke-linejoin: round;
}

.comic-bubble-fill {
    fill: var(--tip-bg);
}

.comic-bubble-row {
    position: relative;
}

.comic-bubble-strong {
    font-weight: 600;
}
</style>
