<script setup>
import {computed} from "vue";
import {ACTS, ropeDown} from "../../figure/acts.js";
import {POSTURES} from "../../figure/places.js";
import {COLOURS} from "./colours.js";

// The rope swing, `u` of the way through the act: where its seat runs, under the hips of the figure sitting on it, the knots it hangs from
// on the bubble's bottom edge above, and how far its ropes are let down from them. The picture's `middle` across, in pixels; the `feet` as
// a share of the picture; the picture `size` pixels square.
const props = defineProps({
    u: {type: Number, required: true},
    middle: {type: Number, required: true},
    feet: {type: Number, required: true},
    size: {type: Number, required: true},
});

const swing = computed(() => {
    const {rope, ties, seat} = ACTS.rope_swing;
    const line = (props.feet - POSTURES.sit.drop) * props.size;
    const top = line - rope * props.size;
    const down = ropeDown(props.u);
    const ropes = [["left", -1], ["right", 1]].map(([name, side]) => ({name, x: props.middle + (side * ties * props.size) / 2}));
    return {line, top, reach: top + (line - top) * down, down, ropes, seat: seat * props.size};
});
</script>

<template>
    <template v-for="rope in swing.ropes" :key="rope.name">
        <line :x1="rope.x" :y1="swing.top" :x2="rope.x" :y2="swing.reach" :stroke="COLOURS.rope" stroke-width="1.4" stroke-linecap="round" />
        <circle :cx="rope.x" :cy="swing.top" r="1.8" :fill="COLOURS.rope" />
    </template>
    <template v-if="swing.down > 0.95">
        <rect :x="middle - swing.seat / 2" :y="swing.line - 1" :width="swing.seat" height="3" rx="1" :fill="COLOURS.wood" stroke-width="0.6" />
    </template>
</template>
