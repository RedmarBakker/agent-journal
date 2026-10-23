<script setup>
import {computed} from "vue";
import {COMIC_BUBBLE, boilAt, bubbleOutline, bubbleSize, letterOf, phraseAt} from "../figure/comicBubble.js";

// The phone call's speech bubble drawn as a comic strip's (figure/comicBubble.js): the phrase of `phrases` it says `seconds` after it began
// saying them, lettered by hand, in an inked outline at page `left` and `top`, its tail to `tip` in the bubble's own pixels, the outline
// boiling as the figure's `frame` goes on.
const props = defineProps({
    phrases: {type: Array, required: true},
    seconds: {type: Number, required: true},
    left: {type: Number, required: true},
    top: {type: Number, required: true},
    tip: {type: Object, required: true},
    frame: {type: Number, required: true},
});

const size = computed(() => bubbleSize(props.phrases));
const said = computed(() => phraseAt(props.phrases, props.seconds));
// each row of the phrase said, each of its letters set a little off the line as a hand writes it
const rows = computed(() =>
    said.value.phrase.rows.map((row, index) => ({
        strong: row.strong,
        letters: [...row.text].map((letter, at) => {
            const {lift, tilt, grow} = letterOf(said.value.index, index, at);
            return {letter, style: {transform: `translateY(${lift}px) rotate(${tilt}deg) scale(${grow})`}};
        }),
    }))
);
const outline = computed(() => bubbleOutline(size.value.width, size.value.height, props.tip, boilAt(props.frame)));
const style = computed(() => ({
    left: `${props.left}px`,
    top: `${props.top}px`,
    width: `${size.value.width}px`,
    height: `${size.value.height}px`,
    fontFamily: COMIC_BUBBLE.hand,
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
        <span class="comic-bubble-words" :style="{opacity: said.shows}">
            <template v-for="(row, index) in rows" :key="`${said.index}-${index}`">
                <span class="comic-bubble-row" :class="{'comic-bubble-strong': row.strong}">
                    <template v-for="(letter, at) in row.letters" :key="at">
                        <span class="comic-bubble-letter" :style="letter.style">{{ letter.letter }}</span>
                    </template>
                </span>
            </template>
        </span>
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
    white-space: pre;
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

.comic-bubble-words {
    position: relative;
    display: flex;
    flex: 1;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.comic-bubble-letter {
    display: inline-block;
}

.comic-bubble-strong {
    font-weight: 700;
}
</style>
