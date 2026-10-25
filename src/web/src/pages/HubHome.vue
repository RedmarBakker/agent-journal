<script setup>
import {computed} from "vue";
import {recentActivity} from "../domain/hub.js";
import {titleOf} from "../domain/row.js";

const props = defineProps({hub: Object, docs: {type: Array, default: () => []}, plans: {type: Array, default: () => []}, activity: {type: Array, default: () => []}});
const emit = defineEmits(["open"]);
const recent = computed(() => recentActivity(props.activity));
</script>

<template>
    <div class="hub-home" data-hub-home>
        <h2 class="team">{{ hub.team_name || hub.name }}</h2>
        <section data-hub-docs>
            <h3 class="head">Documents</h3>
            <template v-for="doc in docs" :key="doc.id">
                <button type="button" class="line" @click="emit('open', doc)">{{ titleOf(doc) }}</button>
            </template>
        </section>
        <section data-hub-plans>
            <h3 class="head">Plans</h3>
            <template v-for="plan in plans" :key="plan.id">
                <button type="button" class="line" @click="emit('open', plan)">Plan {{ plan.id }}: {{ titleOf(plan) }}</button>
            </template>
        </section>
        <section data-hub-activity>
            <h3 class="head">Recent activity</h3>
            <template v-for="message in recent" :key="message.id">
                <div class="line">{{ titleOf(message) }}</div>
            </template>
        </section>
    </div>
</template>

<style scoped>
.hub-home {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px 20px;
}

.team {
    font-size: 16px;
    font-weight: 600;
}

.head {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-2);
    margin-bottom: 4px;
}

.line {
    display: block;
    text-align: left;
    padding: 4px 0;
    font-size: 12.5px;
    color: var(--text);
}
</style>
