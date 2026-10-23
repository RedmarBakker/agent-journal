<script setup>
import TeamPoolList from "./TeamPoolList.vue";

const LEAD = "Workers your own agents started from the team's pool. They run on a colleague's machine and report to you here.";

defineProps({pool: {type: Object, required: true}});
</script>

<template>
    <TeamPoolList title="Your workers on other machines" :lead="LEAD" :lines="pool.elsewhere" empty="None of your workers runs on another machine." />
</template>
