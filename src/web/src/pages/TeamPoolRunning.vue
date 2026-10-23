<script setup>
import TeamPoolList from "./TeamPoolList.vue";

const LEAD = "Workers that one person's agent started on another person's machine, from what that machine offers.";

defineProps({pool: {type: Object, required: true}});
</script>

<template>
    <TeamPoolList title="Pool workers running" :lead="LEAD" :lines="pool.team" empty="No pool worker is running." />
</template>
