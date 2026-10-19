<script setup>
import {ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import Dialog from "../kit/Dialog.vue";

const props = defineProps({version: {type: String, required: true}});
const emit = defineEmits(["no"]);
const started = ref(false);
const failure = ref("");

async function upgrade() {
    failure.value = "";
    try {
        await api.update(true, props.version);
        started.value = true;
    } catch (failed) {
        failure.value = failed.message;
    }
}
</script>

<template>
    <Dialog modal fits small :closable="false" title="Upgrade to version 4">
        <div class="to-four">
            <p>
                The journal will close completely, then version {{ version }} is installed and its install script is run, because the journal
                cannot run while it is upgraded.
            </p>
            <p>Your to-dos become tasks. Plans and everything else come across. Nothing is lost, and the old journal is kept whole.</p>
            <p>The board is set aside for now and comes back later, revised.</p>
            <template v-if="started">
                <p class="state">The journal is closing and version 4 is being installed. This page stops answering; open it again in a few minutes.</p>
            </template>
            <template v-if="failure">
                <p class="state failed" role="alert">The upgrade did not start: {{ failure }}</p>
            </template>
        </div>
        <template #foot>
            <Btn kind="primary" :busy="started" :disabled="started" @click="upgrade">Upgrade and migrate</Btn>
            <Btn :disabled="started" @click="emit('no')">No</Btn>
        </template>
    </Dialog>
</template>

<style scoped>
.to-four p {
    margin: 0 0 10px;
    color: var(--text-2);
    font-size: 13.5px;
    line-height: 1.6;
}

.state {
    color: var(--text);
}

.failed {
    color: var(--danger);
}
</style>
