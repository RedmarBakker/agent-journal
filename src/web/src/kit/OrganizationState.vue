<script setup>
import {computed} from "vue";
import {ORGANIZATION_STATES} from "../domain/organizationStates.js";
import EmptyState from "./EmptyState.vue";
import Notice from "./Notice.vue";

const props = defineProps({state: {type: String, required: true}, detail: {type: String, default: ""}});
const found = computed(() => ORGANIZATION_STATES[props.state]);
</script>

<template>
    <template v-if="found.tone === 'loading'">
        <EmptyState loading />
    </template>
    <template v-else-if="found.tone === 'problem'">
        <Notice tone="danger" icon="warn" class="organization-state">
            <strong>{{ found.title }}.</strong> {{ found.text }}
            <template v-if="detail"> {{ detail }}</template>
        </Notice>
    </template>
    <template v-else>
        <EmptyState class="organization-state" :title="found.title">{{ found.text }}</EmptyState>
    </template>
</template>
