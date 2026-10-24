<script setup>
import {computed} from "vue";
import {ACTS} from "../../figure/acts.js";
import {POSTURES} from "../../figure/places.js";
import {COLOURS} from "./colours.js";

// The rope swing, drawn whole all the act long, from its first frame, so the figure sits down onto it: the knots it hangs from on the
// bubble's bottom edge above, its ropes down from them just outside the figure's arms, and its seat, a little wider than the figure's body,
// its top under the figure's thighs (acts.js rope_swing). The picture's `middle` across, in pixels; the `feet` as a share of the picture;
// the picture `size` pixels square.
const props = defineProps({
    middle: {type: Number, required: true},
    feet: {type: Number, required: true},
    size: {type: Number, required: true},
});

const swing = computed(() => {
    const {rope, ties, seat, under} = ACTS.rope_swing;
    const line = (props.feet - POSTURES.sit.drop) * props.size;
    const ropes = [["left", -1], ["right", 1]].map(([name, side]) => ({name, x: props.middle + (side * ties * props.size) / 2}));
    return {top: line - rope * props.size, seat: line + under * props.size, ropes, wide: seat * props.size};
});
</script>

<template>
    <template v-for="rope in swing.ropes" :key="rope.name">
        <line :x1="rope.x" :y1="swing.top" :x2="rope.x" :y2="swing.seat" :stroke="COLOURS.rope" stroke-width="1.4" stroke-linecap="round" data-swing-rope />
        <circle :cx="rope.x" :cy="swing.top" r="1.8" :fill="COLOURS.rope" />
    </template>
    <rect :x="middle - swing.wide / 2" :y="swing.seat" :width="swing.wide" height="3" rx="1" :fill="COLOURS.wood" stroke-width="0.6" data-swing-seat />
</template>
