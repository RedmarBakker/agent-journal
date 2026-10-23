<script setup>
import {narrow} from "../platform/view.js";
import TeamChatBox from "./TeamChatBox.vue";
import TeamMachines from "./TeamMachines.vue";
import TeamPeopleRows from "./TeamPeopleRows.vue";
import TeamPoolRunning from "./TeamPoolRunning.vue";
import TeamServer from "./TeamServer.vue";
import TeamSummary from "./TeamSummary.vue";
import TeamVersion from "./TeamVersion.vue";

defineProps({standing: {type: Object, required: true}, people: {type: Array, required: true}, devices: {type: Array, default: () => []}, pool: {type: Object, required: true}});
</script>

<template>
    <div class="team-column">
        <TeamSummary :standing="standing" :people="people" />
        <template v-if="narrow">
            <TeamPoolRunning :pool="pool" />
            <TeamVersion :standing="standing" />
            <TeamMachines :devices="devices" :admin="standing.admin" />
            <TeamChatBox hosted />
            <TeamPeopleRows :people="people" :devices="devices" :admin="standing.admin" />
            <TeamServer :standing="standing" />
        </template>
        <template v-else>
            <div class="team-grid hosted">
                <div class="team-column">
                    <TeamPoolRunning :pool="pool" />
                    <TeamMachines :devices="devices" :admin="standing.admin" />
                </div>
                <div class="team-column">
                    <TeamVersion :standing="standing" />
                    <TeamChatBox hosted />
                    <TeamPeopleRows :people="people" :devices="devices" :admin="standing.admin" />
                    <TeamServer :standing="standing" />
                </div>
            </div>
        </template>
    </div>
</template>
