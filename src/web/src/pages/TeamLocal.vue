<script setup>
import {narrow} from "../platform/view.js";
import TeamChatBox from "./TeamChatBox.vue";
import TeamAdmin from "./TeamAdmin.vue";
import TeamElsewhere from "./TeamElsewhere.vue";
import TeamLent from "./TeamLent.vue";
import TeamOffer from "./TeamOffer.vue";
import TeamPassword from "./TeamPassword.vue";
import TeamPeople from "./TeamPeople.vue";
import TeamSync from "./TeamSync.vue";

defineProps({standing: {type: Object, required: true}, people: {type: Array, required: true}, devices: {type: Array, default: () => []}, pool: {type: Object, required: true}});
defineEmits(["pool"]);
</script>

<template>
    <template v-if="narrow">
        <div class="team-column">
            <TeamLent :pool="pool" @pool="$emit('pool', $event)" />
            <TeamSync :standing="standing" />
            <TeamElsewhere :pool="pool" />
            <TeamOffer :pool="pool" @pool="$emit('pool', $event)" />
            <TeamChatBox />
            <TeamPeople :people="people" :devices="devices" :admin="standing.admin" />
            <TeamPassword />
            <template v-if="standing.admin">
                <TeamAdmin />
            </template>
        </div>
    </template>
    <template v-else>
        <div class="team-grid">
            <div class="team-column">
                <TeamLent :pool="pool" @pool="$emit('pool', $event)" />
                <TeamElsewhere :pool="pool" />
                <TeamPeople :people="people" :devices="devices" :admin="standing.admin" />
            </div>
            <div class="team-column">
                <TeamSync :standing="standing" />
                <TeamOffer :pool="pool" @pool="$emit('pool', $event)" />
                <TeamChatBox />
                <TeamPassword />
                <template v-if="standing.admin">
                    <TeamAdmin />
                </template>
            </div>
        </div>
    </template>
</template>
