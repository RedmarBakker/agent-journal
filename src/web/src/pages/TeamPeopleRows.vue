<script setup>
import {isOnline, machinesOf, presence, ROLES} from "../domain/team.js";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import TeamPersonName from "./TeamPersonName.vue";
import "./team.css";

defineProps({people: {type: Array, required: true}, devices: {type: Array, default: () => []}, admin: Boolean});
const online = (machines) => `${machines.filter((device) => isOnline(device.pulled_at)).length} of ${machines.length} ${machines.length === 1 ? "machine" : "machines"} online`;
</script>

<template>
    <ListBox title="People" :count="people.length">
        <template v-for="person in people" :key="person.id">
            <div class="team-row">
                <TeamPersonName :person="person" :sub="[ROLES[person.role] || person.role, admin ? online(machinesOf(person, devices)) : ''].filter(Boolean).join(' · ')" />
                <span class="team-presence">
                    <StateDot :state="person.online ? 'done' : ''" />
                    {{ presence(person.online, person.seen_at) }}
                </span>
            </div>
        </template>
    </ListBox>
</template>
