<script setup>
import {computed} from "vue";
import {CLAW, prongsOf} from "../figure/parcels.js";

// The claw crane that now and then takes the server units away in the UFO's place (figure/parcels.js craneAt), drawn inside the chat
// window `box` (its left, top, right and bottom on the page), so a stack lifted past its top is out of the window: its rail along the
// window's top, its trolley at page `x` on it, the claw hanging `chain` pixels under the rail, below the window's top when less than nothing,
// and the claw `open`, 1 wide open and 0 shut on a stack.
const props = defineProps({
    box: {type: Object, required: true},
    x: {type: Number, required: true},
    chain: {type: Number, required: true},
    open: {type: Number, required: true},
});

// the trolley's drawing and where the chain leaves it, in pixels
const TROLLEY = {width: 30, height: 9, wheel: 2.2};

const style = computed(() => ({left: `${props.box.left}px`, top: `${props.box.top}px`, width: `${props.box.right - props.box.left}px`, height: `${props.box.bottom - props.box.top}px`}));
const across = computed(() => props.x - props.box.left);
const hangs = computed(() => TROLLEY.height + props.chain);
// each prong out from the hub along its bar and down beside the box, its tip out wide while the claw is open and in flat on the box's side
// once it is shut, turned in under a hook (parcels.js prongsOf)
const prongs = computed(() =>
    prongsOf(props.open).map(({way, top, tip, reach}) => `M${way * CLAW.hub} 0H${top}L${tip} ${reach}l${-way * CLAW.hook} ${CLAW.hook}`)
);
</script>

<template>
    <div class="claw-crane" :style="style" aria-hidden="true">
        <svg class="claw-crane-drawing" :width="box.right - box.left" :height="box.bottom - box.top">
            <rect class="claw-crane-rail" x="0" y="0" :width="box.right - box.left" height="3" />
            <g :transform="`translate(${across} 0)`">
                <line class="claw-crane-chain" x1="0" :y1="TROLLEY.height" x2="0" :y2="hangs" />
                <g :transform="`translate(0 ${hangs})`">
                    <template v-for="(prong, index) in prongs" :key="index">
                        <path class="claw-crane-prong" :d="prong" />
                    </template>
                    <rect class="claw-crane-hub" :x="-CLAW.hub" y="-3" :width="CLAW.hub * 2" height="5" rx="1.5" />
                </g>
                <rect class="claw-crane-trolley" :x="-TROLLEY.width / 2" y="1" :width="TROLLEY.width" :height="TROLLEY.height" rx="2" />
                <rect class="claw-crane-light" x="-3" y="3.5" width="6" height="2" rx="1" />
                <circle class="claw-crane-wheel" :cx="-TROLLEY.width / 2 + 5" cy="1" :r="TROLLEY.wheel" />
                <circle class="claw-crane-wheel" :cx="TROLLEY.width / 2 - 5" cy="1" :r="TROLLEY.wheel" />
            </g>
        </svg>
    </div>
</template>

<style scoped>
.claw-crane {
    position: fixed;
    z-index: 41;
    overflow: hidden;
    pointer-events: none;
}

.claw-crane-drawing {
    display: block;
    overflow: visible;
    filter: drop-shadow(0 0 1px color-mix(in srgb, var(--text) 45%, transparent));
}

.claw-crane-rail {
    fill: #6b6f7c;
}

.claw-crane-trolley {
    fill: #e8b84a;
    stroke: #272936;
    stroke-width: 0.8;
}

.claw-crane-light {
    fill: #ef476f;
}

.claw-crane-wheel {
    fill: #35374b;
    stroke: #a9adb8;
    stroke-width: 0.6;
}

.claw-crane-chain {
    stroke: #a9adb8;
    stroke-width: 1.4;
    stroke-dasharray: 2 1.4;
}

.claw-crane-hub {
    fill: #a9adb8;
    stroke: #272936;
    stroke-width: 0.7;
}

.claw-crane-prong {
    fill: none;
    stroke: #c9ccd4;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}
</style>
