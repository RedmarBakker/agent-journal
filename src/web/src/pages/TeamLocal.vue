<script setup>
import {narrow} from "../platform/view.js";
import TeamChatBox from "./TeamChatBox.vue";
import TeamDevices from "./TeamDevices.vue";
import TeamElsewhere from "./TeamElsewhere.vue";
import TeamInvite from "./TeamInvite.vue";
import TeamLent from "./TeamLent.vue";
import TeamOffer from "./TeamOffer.vue";
import TeamPassword from "./TeamPassword.vue";
import TeamPeople from "./TeamPeople.vue";
import TeamSync from "./TeamSync.vue";

defineProps({standing: {type: Object, required: true}, people: {type: Array, required: true}, devices: {type: Array, default: () => []}});
</script>

<template>
    <template v-if="narrow">
        <div class="team-column">
            <TeamLent />
            <TeamSync :standing="standing" />
            <TeamElsewhere />
            <TeamOffer />
            <TeamChatBox />
            <TeamPeople :people="people" :devices="devices" :admin="standing.admin" />
            <TeamPassword />
            <template v-if="standing.admin">
                <TeamInvite />
                <TeamDevices />
            </template>
        </div>
    </template>
    <template v-else>
        <div class="team-grid">
            <div class="team-column">
                <TeamLent />
                <TeamElsewhere />
                <TeamPeople :people="people" :devices="devices" :admin="standing.admin" />
            </div>
            <div class="team-column">
                <TeamSync :standing="standing" />
                <TeamOffer />
                <TeamChatBox />
                <TeamPassword />
                <template v-if="standing.admin">
                    <TeamInvite />
                    <TeamDevices />
                </template>
            </div>
        </div>
    </template>
</template>
