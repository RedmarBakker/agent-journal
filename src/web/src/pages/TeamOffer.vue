<script setup>
import {ref} from "vue";
import {api} from "../api/client.js";
import {saveSettings} from "../actions/settings.js";
import ListBox from "../kit/ListBox.vue";
import Stepper from "../kit/Stepper.vue";
import TeamFailure from "./TeamFailure.vue";
import "./team.css";

const MOST_SLOTS = 8;

defineProps({pool: {type: Object, required: true}});
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
                <div>
                    <dt>Lent out now</dt>
                    <dd>{{ pool.lent.length }}</dd>
                </div>
                <div>
                    <dt>Free now</dt>
                    <dd>{{ pool.free }}</dd>
                </div>
            </dl>
            <p class="team-fine">A colleague's agent can start up to this many workers on this machine. They run with your model account, so you pay for their runs.</p>
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
