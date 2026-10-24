<script setup>
import {computed} from "vue";
import {ACTS, bugAt, partOf, splatDrops} from "../../figure/acts.js";

// The bug of a fixed test run, drawn in 3D (`bug`, its pictures one for each step of its stride, figure.js Stage.drawBug): crawling in
// along the floor to its place out on the figure's left, its legs going (acts.js bugAt); shot, it splatters, and drops of the splatter fly
// out at the screen, growing as they come, land on it as on a camera's lens and run down as they fade (acts.js splatDrops); smashed by
// the mallet it lies flat and fades. The act `name`, `u` of the way through it; the picture's `middle` across and the `floor` under the
// feet, in pixels; the picture `size` pixels square.
const props = defineProps({
    name: {type: String, required: true},
    u: {type: Number, required: true},
    middle: {type: Number, required: true},
    floor: {type: Number, required: true},
    size: {type: Number, required: true},
    bug: {type: Object, required: true},
});

const crawler = computed(() => {
    const act = ACTS[props.name];
    const at = bugAt(act, props.u, props.size);
    const x = props.middle + at.out;
    const y = props.floor;
    const splat = act.splat !== undefined ? props.u >= act.splat : at.flat > 0;
    const drops = props.name === "bug_shot" ? splatDrops(props.u, props.size, {x, y: y - 4}, {x: props.middle, y: props.size * 0.5}) : [];
    return {
        x,
        y,
        whole: at.whole,
        flat: at.flat,
        shows: at.shows,
        splat: splat ? Math.max(at.shows, act.splat !== undefined ? 1 - partOf(props.u, [0.85, 1]) : 0) : 0,
        drops: drops.map((drop, index) => ({...drop, name: `drop${index}`})),
    };
});
// the bug's picture for the step of its stride it is at, placed with its feet at the crawler
const picture = computed(() => {
    const step = Math.floor((props.u * ACTS[props.name].frames) / 2) % 2;
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
    <template v-for="drop in crawler.drops" :key="drop.name">
        <g class="figure-act-lens" :opacity="drop.fade">
            <template v-if="drop.landed">
                <rect :x="drop.x - drop.r * 0.25" :y="drop.y" :width="drop.r * 0.5" :height="drop.run" rx="2" fill="#9bd34a" opacity="0.8" />
                <circle :cx="drop.x" :cy="drop.y + drop.run" :r="drop.r * 0.4" fill="#9bd34a" />
            </template>
            <circle :cx="drop.x" :cy="drop.y" :r="drop.r" fill="#9bd34a" opacity="0.85" />
            <circle :cx="drop.x - drop.r * 0.3" :cy="drop.y - drop.r * 0.3" :r="drop.r * 0.25" fill="#e8ffd0" opacity="0.8" />
        </g>
    </template>
</template>

<style scoped>
/* a drop of the bug's splatter on the screen, soft as a drop on a camera's lens is */
.figure-act-lens {
    filter: blur(0.7px);
}
</style>
