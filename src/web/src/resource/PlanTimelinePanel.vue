<script setup>
import {ref} from "vue";
import {useScope} from "../composables/scope.js";
import {usePoll} from "../composables/poll.js";
import {peek} from "../route.js";
import PlanTimeline from "./PlanTimeline.vue";
import {onPhone} from "../platform/phone.js";
import PhoneDesktopNotice from "../phone/PhoneDesktopNotice.vue";

const props = defineProps({plan: {type: Object, required: true}});
const items = ref([]);
const loaded = ref(false);
const scope = useScope();

if (!onPhone) {
    usePoll("plan.timeline", {
        params: () => ({scope, plan: props.plan.id}),
        take: (got) => {
            items.value = got;
            loaded.value = true;
        },
    });
}
</script>

<template>
    <section class="timeline-panel">
        <PhoneDesktopNotice v-if="onPhone" message="The plan timeline opens on the desktop." />
        <template v-else>
            <h3 class="heading">Timeline</h3>
            <PlanTimeline :items="items" :loading="!loaded" @open="(n) => peek('tasks', n)" />
        </template>
    </section>
</template>

<style scoped>
.timeline-panel {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 16px;
    overflow-y: auto;
}

.heading {
    margin: 0;
    color: var(--text-2);
    font-size: 13px;
    font-weight: 600;
}
</style>
