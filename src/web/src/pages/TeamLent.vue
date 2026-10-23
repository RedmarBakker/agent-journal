<script setup>
import {ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import ListBox from "../kit/ListBox.vue";
import TeamFailure from "./TeamFailure.vue";
import TeamPoolLine from "./TeamPoolLine.vue";
import "./team.css";

defineProps({pool: {type: Object, required: true}});
const emit = defineEmits(["pool"]);
const stopping = ref(0);
const failure = ref("");

async function stop(request) {
    stopping.value = request;
    failure.value = "";
    try {
        emit("pool", await api.stopPoolWorker(request));
    } catch (e) {
        failure.value = e.message;
    } finally {
        stopping.value = 0;
    }
}
</script>

<template>
    <ListBox title="Lent out now" :count="pool.lent.length" :aside="pool.slots ? '' : 'No workers offered'">
        <template v-if="pool.lent.length">
            <template v-for="line in pool.lent" :key="line.request">
                <TeamPoolLine :line="line">
                    <Btn small kind="danger" :busy="stopping === line.request" @click="stop(line.request)">Stop</Btn>
                </TeamPoolLine>
            </template>
        </template>
        <template v-else>
            <div class="team-block">
                <p class="team-fine">{{ pool.slots ? "No colleague's worker runs on this machine now." : "This machine offers no workers to the team, so none is lent out." }} A worker a colleague's agent takes shows here with a Stop button.</p>
            </div>
        </template>
        <template v-if="failure">
            <TeamFailure :text="failure" />
        </template>
    </ListBox>
</template>
