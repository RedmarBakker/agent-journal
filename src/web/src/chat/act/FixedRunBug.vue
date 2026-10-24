<script setup>
import {computed} from "vue";
import {ACTS, bugAt} from "../../figure/acts.js";

// The bug a fixed test run's mallet smashes, drawn in 3D (`bug`, its pictures one for each step of its stride, figure.js Stage.drawBug):
// crawling in along the floor to its place out on the figure's left, its legs going (acts.js bugAt); smashed, it lies flat, splattered,
// and fades. `u` of the way through the smash; the picture's `middle` across and the `floor` under the feet, in pixels; the picture
// `size` pixels square.
const props = defineProps({
    u: {type: Number, required: true},
    middle: {type: Number, required: true},
    floor: {type: Number, required: true},
    size: {type: Number, required: true},
    bug: {type: Object, required: true},
});

const act = ACTS.bug_smash;
const crawler = computed(() => {
    const at = bugAt(act, props.u, props.size);
    return {x: props.middle + at.out, y: props.floor, whole: at.whole, flat: at.flat, shows: at.shows, splat: at.flat > 0 ? at.shows : 0};
});
// the bug's picture for the step of its stride it is at, placed with its feet at the crawler
const picture = computed(() => {
    const step = Math.floor((props.u * act.frames) / 2) % 2;
    return {href: props.bug.pictures[step], x: -props.bug.at.x, y: -props.bug.at.y, width: props.bug.width, height: props.bug.height};
});
</script>

<template>
    <template v-if="crawler.whole || crawler.flat">
        <image
            :href="picture.href"
            :x="picture.x"
            :y="picture.y"
            :width="picture.width"
            :height="picture.height"
            :opacity="crawler.shows"
            :transform="`translate(${crawler.x} ${crawler.y}) scale(${1 + 0.4 * crawler.flat} ${1 - 0.78 * crawler.flat})`"
            data-act-bug
        />
    </template>
    <template v-if="crawler.splat">
        <path :transform="`translate(${crawler.x} ${crawler.y}) scale(${1.3 - 0.3 * crawler.splat})`" :opacity="crawler.splat" d="M-9 0q2-6 6-3 1-6 5-2 5-3 5 2 5 1 2 4 3 4-3 3-4 4-7 1-3 0-6-1-6-4-4-3Z" fill="#9bd34a" stroke="#5f8f24" stroke-width="0.8" />
    </template>
</template>
