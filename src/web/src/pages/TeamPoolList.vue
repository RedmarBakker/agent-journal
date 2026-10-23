<script setup>
import ListBox from "../kit/ListBox.vue";
import TeamPoolLine from "./TeamPoolLine.vue";
import "./team.css";

defineProps({title: {type: String, required: true}, lead: {type: String, required: true}, lines: {type: Array, required: true}, empty: {type: String, required: true}});
</script>

<template>
    <ListBox :title="title" :count="lines.length" :lead="lead">
        <template v-if="lines.length">
            <template v-for="line in lines" :key="line.request">
                <TeamPoolLine :line="line" />
            </template>
        </template>
        <template v-else>
            <div class="team-block">
                <p class="team-fine">{{ empty }}</p>
            </div>
        </template>
    </ListBox>
</template>
