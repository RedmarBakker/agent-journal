<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {usePasswordField} from "../composables/passwordField.js";
import SwitchCase from "../kit/SwitchCase.vue";
import {choose} from "../state/environment.js";
import "./team.css";
import TeamAccount from "./TeamAccount.vue";
import TeamChoice from "./TeamChoice.vue";
import TeamClaim from "./TeamClaim.vue";

const props = defineProps({email: {type: String, default: ""}});
const emit = defineEmits(["joined"]);
// what the panel shows: the two choices, a claim's URL, a claim's account, or the form for a server already claimed
const step = ref("choice");
const url = ref("");
const email = ref("");
const {password, generated, generate} = usePasswordField();
const busy = ref(false);
const failure = ref("");

onMounted(() => (email.value = props.email));

async function check() {
    busy.value = true;
    failure.value = "";
    try {
        const got = await api.checkTeam({url: url.value});
        url.value = got.address;
        if (got.refusal) failure.value = got.refusal;
        else step.value = "account";
    } catch (e) {
        failure.value = e.message;
    } finally {
        busy.value = false;
    }
}

function open(next) {
    failure.value = "";
    step.value = next;
}

async function join() {
    busy.value = true;
    failure.value = "";
    try {
        const got = await api.joinTeam({url: url.value, email: email.value, password: password.value});
        password.value = "";
        choose(got.environment);
        emit("joined", got.outcome);
    } catch (e) {
        failure.value = e.message;
    } finally {
        busy.value = false;
    }
}
</script>

<template>
    <div class="team-connect-panel">
        <SwitchCase :value="step">
            <template #choice>
                <TeamChoice @open="open" />
            </template>
            <template #claim>
                <TeamClaim v-model:url="url" :busy="busy" :failure="failure" @check="check" @open="open" />
            </template>
            <template #default>
                <TeamAccount
                    v-model:url="url"
                    v-model:email="email"
                    v-model:password="password"
                    :step="step"
                    :generated="generated"
                    :busy="busy"
                    :failure="failure"
                    @generate="generate"
                    @join="join"
                    @open="open"
                />
            </template>
        </SwitchCase>
    </div>
</template>

<style scoped>
.team-connect-panel {
    border-bottom: 1px solid var(--border);
}
</style>
