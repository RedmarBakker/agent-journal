<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {usePasswordField} from "../composables/passwordField.js";
import Btn from "../kit/Btn.vue";
import CopyButton from "../kit/CopyButton.vue";
import FormField from "../kit/FormField.vue";
import StateDot from "../kit/StateDot.vue";
import ListBox from "../kit/ListBox.vue";
import TextInput from "../kit/TextInput.vue";
import {choose} from "../state/environment.js";
import "./team.css";

const props = defineProps({email: {type: String, default: ""}});
const emit = defineEmits(["joined"]);
const url = ref("");
const email = ref("");
const {password, generated, generate} = usePasswordField();
const busy = ref(false);
const failure = ref("");

onMounted(() => (email.value = props.email));

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
    <ListBox title="Connect to a team server">
        <form @submit.prevent="join">
            <div class="team-block">
                <FormField label="Team URL" for="team-url" help="The invitation URL an admin sent you, or the URL of a new team server.">
                    <TextInput id="team-url" :value="url" placeholder="https://team.example.com" @input="url = $event.target.value" />
                </FormField>
                <FormField label="Email" for="team-email" help="Your user name on the team. Filled in from git when git knows it.">
                    <TextInput id="team-email" :value="email" type="email" autocomplete="email" @input="email = $event.target.value" />
                </FormField>
                <FormField label="Password" for="team-password" help="At least 12 characters mixing three of lower case, upper case, digits and symbols, or 20 characters or more.">
                    <div class="team-inline">
                        <TextInput id="team-password" :value="password" :type="generated ? 'text' : 'password'" :class="{'team-mono': generated}" autocomplete="new-password" @input="password = $event.target.value" />
                        <template v-if="generated">
                            <CopyButton :text="password" hint="Copy the password" />
                        </template>
                        <Btn @click="generate">Generate</Btn>
                    </div>
                </FormField>
                <template v-if="generated">
                    <p class="team-keep">
                        <StateDot state="you" />
                        <span>Save this password somewhere safe before you connect: it is shown only here.</span>
                    </p>
                </template>
            </div>
            <div class="team-block team-next">
                <span class="team-section">What connecting does</span>
                <dl class="team-facts">
                    <div>
                        <dt>With a new team server's URL</dt>
                        <dd>You become the team's admin</dd>
                        <dd class="team-sub">Everything in this journal, files too, is uploaded to the team.</dd>
                    </div>
                    <div>
                        <dt>With an invitation URL</dt>
                        <dd>This journal takes the team's copy</dd>
                        <dd class="team-sub">It is refused when it holds tasks or messages of its own.</dd>
                    </div>
                </dl>
                <template v-if="failure">
                    <p class="team-refusal">
                        <StateDot state="failed" />
                        <span>{{ failure }}</span>
                    </p>
                </template>
                <Btn kind="primary" :busy="busy" @click="join">{{ busy ? "Connecting" : "Connect" }}</Btn>
            </div>
        </form>
    </ListBox>
</template>

<style scoped>
.team-inline {
    display: flex;
    gap: 8px;
}

.team-next {
    border-top: 1px solid var(--border);
}

.team-section {
    color: var(--text-2);
    font-size: 12px;
    font-weight: 500;
}

.team-sub {
    color: var(--text-3);
    font-size: 12px;
}

.team-keep,
.team-refusal {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin: 0;
}

.team-keep {
    color: var(--tone-warn);
    font-size: 12px;
}

.team-refusal {
    color: var(--danger);
}

.team-keep :deep(.state-dot),
.team-refusal :deep(.state-dot) {
    margin-top: 5px;
}

@media (max-width: 520px) {
    .team-facts {
        grid-template-columns: minmax(0, 1fr);
    }
}
</style>
