<script setup>
import {ref} from "vue";
import {api} from "../api/client.js";
import {usePasswordField} from "../composables/passwordField.js";
import Btn from "../kit/Btn.vue";
import FormField from "../kit/FormField.vue";
import ListBox from "../kit/ListBox.vue";
import TextInput from "../kit/TextInput.vue";
import "./team.css";

const old = ref("");
const {password, generated, generate} = usePasswordField();
const busy = ref(false);
const failure = ref("");
const changed = ref(false);

async function change() {
    busy.value = true;
    failure.value = "";
    changed.value = false;
    try {
        await api.changeTeamPassword(old.value, password.value);
        old.value = "";
        password.value = "";
        changed.value = true;
    } catch (e) {
        failure.value = e.message;
    } finally {
        busy.value = false;
    }
}
</script>

<template>
    <ListBox title="Your password">
        <form class="team-block" @submit.prevent="change">
            <FormField label="Current password" for="team-old-password">
                <TextInput id="team-old-password" :value="old" type="password" autocomplete="current-password" @input="old = $event.target.value" />
            </FormField>
            <FormField label="New password" for="team-new-password" help="At least 12 characters mixing three of lower case, upper case, digits and symbols, or 20 characters or more.">
                <div class="team-inline">
                    <TextInput id="team-new-password" :value="password" :type="generated ? 'text' : 'password'" autocomplete="new-password" @input="password = $event.target.value" />
                    <Btn @click="generate">Generate</Btn>
                </div>
            </FormField>
            <template v-if="failure">
                <p class="team-failure">{{ failure }}</p>
            </template>
            <template v-if="changed">
                <p class="team-fine">Your password is changed.</p>
            </template>
            <div>
                <Btn kind="primary" :busy="busy" @click="change">Change password</Btn>
            </div>
        </form>
    </ListBox>
</template>

<style scoped>
.team-inline {
    display: flex;
    gap: 8px;
}
</style>
