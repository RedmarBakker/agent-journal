<script setup>
import {computed} from "vue";
import RowDock from "./RowDock.vue";
import WatchDock from "./WatchDock.vue";

// One message docked above the chat: the output it watches, or the row it docks, marked closing while it leaves the dock
const props = defineProps({message: {type: Object, required: true}, folded: Boolean});

const card = computed(() => props.message.data);
const closing = computed(() => (card.value.undock_at ? "" : null));
</script>

<template>
    <template v-if="card.output">
        <WatchDock :message="message" :folded="folded" :data-figure-closing="closing" />
    </template>
    <template v-else>
        <RowDock :message="message" :folded="folded" :data-figure-closing="closing" />
    </template>
</template>
