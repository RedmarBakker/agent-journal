<script setup>
import {computed, ref} from "vue";
import {api} from "../api/client.js";
import {saveSettings} from "../actions/settings.js";
import ListBox from "../kit/ListBox.vue";
import Stepper from "../kit/Stepper.vue";
import TeamFailure from "./TeamFailure.vue";
import "./team.css";

const MOST_SLOTS = 8;

const props = defineProps({pool: {type: Object, required: true}});
const facts = computed(() => [
    {label: "Lent out now", value: props.pool.lent.length},
    {label: "Free now", value: props.pool.free},
    {label: "Minutes today", value: props.pool.minute_cap ? `${props.pool.minutes_today} of ${props.pool.minute_cap}` : props.pool.minutes_today},
]);
const emit = defineEmits(["pool"]);
const failure = ref("");

async function offered(slots) {
    failure.value = "";
    try {
        await saveSettings({workers: {pool_slots: slots}});
        emit("pool", await api.teamPool());
    } catch (e) {
        failure.value = e.message;
    }
}
</script>

<template>
    <ListBox title="Worker pool offer">
        <div class="team-block">
            <div class="team-field">
                <span class="team-field-label">Workers offered to the team</span>
                <Stepper :value="pool.slots" :min="0" :max="MOST_SLOTS" label="Workers offered to the team" @change="offered" />
            </div>
            <dl class="team-facts">
                <template v-for="fact in facts" :key="fact.label">
                    <div>
                        <dt>{{ fact.label }}</dt>
                        <dd>{{ fact.value }}</dd>
                    </div>
                </template>
            </dl>
            <p class="team-fine">A colleague's agent can start up to this many workers on this machine. They run with your model account, so you pay for their runs; a daily cap in minutes is set under Settings, Workers.</p>
            <template v-if="failure">
                <TeamFailure :text="failure" />
            </template>
        </div>
    </ListBox>
</template>

<style scoped>
.team-field {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
}

.team-field-label {
    color: var(--text-2);
    font-size: 12px;
    font-weight: 500;
}
</style>
