<script setup>
import {computed, ref} from "vue";
import ChatMark from "../kit/ChatMark.vue";
import FlowchartDialog from "./FlowchartDialog.vue";

const props = defineProps({title: {type: String, required: true}, edges: {type: Array, required: true}, time: {type: Number, required: true}});
const opened = ref(false);
const mark = computed(() => ({icon: "activity", markIcon: "flowchart", group: "agent", label: "Flowchart", name: props.title, time: props.time, title: "Open the flowchart", action: "Open the flowchart"}));
</script>

<template>
    <ChatMark :mark="mark" @act="opened = true" />
    <template v-if="opened">
        <FlowchartDialog :title="title" :edges="edges" @close="opened = false" />
    </template>
</template>
