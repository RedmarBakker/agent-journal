<script setup>
import {computed} from "vue";
import {ACTS, partOf, splatDrops} from "../../figure/acts.js";

// The bugs of a fixed test run crawling on the chat window's walls, drawn in 3D (`bug`, its pictures one for each step of its stride,
// figure.js Stage.drawBug), each `bugs` one where it is on its wall in the picture's pixels, its feet to the wall (acts.js bugShotScene):
// shot, it splatters where it sits; after the last, drops of its splatter fly out at the screen, growing as they come, land on it as on a
// camera's lens and run down as they fade (acts.js splatDrops). `u` of the way through the bug shot; the picture's `middle` across, and the
// picture `size` pixels square.
const props = defineProps({
    u: {type: Number, required: true},
    middle: {type: Number, required: true},
    size: {type: Number, required: true},
    bug: {type: Object, required: true},
    bugs: {type: Array, required: true},
});

const act = ACTS.bug_shot;
const SPLAT = "M-9 0q2-6 6-3 1-6 5-2 5-3 5 2 5 1 2 4 3 4-3 3-4 4-7 1-3 0-6-1-6-4-4-3Z";

// each bug as it is drawn, named by its place in the shot, its picture for the step of its stride it is at and its splatter's fading
const drawn = computed(() => {
    const step = Math.floor((props.u * act.frames) / 2) % 2;
    const fades = 1 - partOf(props.u, [0.85, 1]);
    return props.bugs.map((each, index) => ({
        name: `bug${index}`,
        shot: each.shot,
        place: `translate(${each.x} ${each.y}) rotate(${each.turn})`,
        href: props.bug.pictures[step],
        fades,
    }));
});
const picture = computed(() => ({x: -props.bug.at.x, y: -props.bug.at.y, width: props.bug.width, height: props.bug.height}));
const drops = computed(() => {
    const last = props.bugs.at(-1);
    return last ? splatDrops(props.u, props.size, last, {x: props.middle, y: props.size * 0.5}).map((drop, index) => ({...drop, name: `drop${index}`})) : [];
});
</script>

<template>
    <template v-for="each in drawn" :key="each.name">
        <g :transform="each.place">
            <template v-if="each.shot">
                <path :opacity="each.fades" :d="SPLAT" fill="#9bd34a" stroke="#5f8f24" stroke-width="0.8" data-act-splat />
            </template>
            <template v-else>
                <image :href="each.href" :x="picture.x" :y="picture.y" :width="picture.width" :height="picture.height" data-act-bug />
            </template>
        </g>
    </template>
    <template v-for="drop in drops" :key="drop.name">
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
