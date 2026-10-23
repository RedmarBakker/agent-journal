<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {strongPassword} from "../domain/passwords.js";
import Btn from "../kit/Btn.vue";
import FormField from "../kit/FormField.vue";
import ListBox from "../kit/ListBox.vue";
import TextInput from "../kit/TextInput.vue";
import {choose} from "../state/environment.js";
import "./team.css";

const props = defineProps({email: {type: String, default: ""}});
const emit = defineEmits(["joined"]);
const url = ref("");
const email = ref("");
const password = ref("");
const generated = ref(false);
const busy = ref(false);
const failure = ref("");

onMounted(() => (email.value = props.email));

function generate() {
    password.value = strongPassword();
    generated.value = true;
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
    <ListBox title="Team server">
        <form class="team-block" @submit.prevent="join">
            <FormField label="Team URL" for="team-url" help="A new team server's URL makes you its admin. To join a team, paste the invitation URL an admin sent you.">
                <TextInput id="team-url" :value="url" placeholder="https://team.example.com" @input="url = $event.target.value" />
            </FormField>
            <FormField label="Email" for="team-email" help="Your user name on the team. Filled in from git when git knows it.">
                <TextInput id="team-email" :value="email" type="email" autocomplete="email" @input="email = $event.target.value" />
            </FormField>
            <FormField label="Password" for="team-password" help="At least 12 characters mixing three of lower case, upper case, digits and symbols, or 20 characters or more.">
                <div class="team-inline">
                    <TextInput id="team-password" :value="password" :type="generated ? 'text' : 'password'" autocomplete="new-password" @input="password = $event.target.value" />
                    <Btn @click="generate">Generate</Btn>
                </div>
            </FormField>
            <template v-if="generated">
                <p class="team-fine">Save this password somewhere safe before you connect: it is shown only here.</p>
            </template>
            <template v-if="failure">
                <p class="team-failure">{{ failure }}</p>
            </template>
            <Btn kind="primary" :busy="busy" @click="join">Connect</Btn>
            <p class="team-fine">
                The first journal to connect becomes the team's: everything in it, files too, is uploaded. A journal that joins a team that has a journal takes
                the team's copy, and is refused when it holds tasks or messages of its own.
            </p>
        </form>
    </ListBox>
</template>

<style scoped>
.team-inline {
    display: flex;
    gap: 8px;
}
</style>
