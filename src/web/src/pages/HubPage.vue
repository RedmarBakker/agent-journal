<script setup>
import {computed} from "vue";
import {inHub, isHub} from "../domain/hub.js";
import HubBoard from "./HubBoard.vue";
import HubHome from "./HubHome.vue";

const props = defineProps({environments: Array, docs: Array, plans: Array, tasks: Array, messages: Array});
const emit = defineEmits(["open"]);
const hub = computed(() => props.environments.find(isHub));
</script>

<template>
    <div v-if="hub" class="hub-page" data-hub-page>
        <HubHome :hub="hub" :docs="docs" :plans="inHub(plans, hub)" :activity="inHub(messages, hub)" @open="emit('open', $event)" />
        <HubBoard :tasks="inHub(tasks, hub)" :environments="environments" @open="emit('open', $event)" />
    </div>
</template>
