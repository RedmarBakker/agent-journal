<script setup>
import StateDot from "../kit/StateDot.vue";

defineProps({message: {type: String, default: ""}});
</script>

<template>
    <template v-if="message">
        <p class="team-refusal">
            <StateDot state="failed" />
            <span>{{ message }}</span>
        </p>
    </template>
</template>
