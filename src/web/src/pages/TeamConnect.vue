<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import {usePasswordField} from "../composables/passwordField.js";
import Btn from "../kit/Btn.vue";
import CopyButton from "../kit/CopyButton.vue";
import FormField from "../kit/FormField.vue";
import StateDot from "../kit/StateDot.vue";
import TextInput from "../kit/TextInput.vue";
import {choose} from "../state/environment.js";
import "./team.css";

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
        <template v-if="step === 'choice'">
            <div class="team-block">
                <span class="team-section">Connect to a team server</span>
                <p class="team-plain">Claim a new team server to become its admin, or connect to one you have an account or an invitation for.</p>
                <div class="team-choices">
                    <Btn kind="primary" @click="open('claim')">Claim a server</Btn>
                    <Btn @click="open('connect')">Connect with an account</Btn>
                </div>
            </div>
        </template>
        <template v-else-if="step === 'claim'">
            <form class="team-block" @submit.prevent="open('account')">
                <span class="team-section">Claim a server</span>
                <FormField label="Server address" for="team-url" help="The URL or IP address the installer printed. The first journal to claim a new server becomes its admin.">
                    <TextInput id="team-url" :value="url" placeholder="https://203.0.113.5" @input="url = $event.target.value" />
                </FormField>
                <div class="team-choices">
                    <Btn kind="primary" :disabled="!url.trim()" @click="open('account')">Next</Btn>
                    <Btn @click="open('choice')">Back</Btn>
                </div>
            </form>
        </template>
        <template v-else>
            <form class="team-block" @submit.prevent="join">
                <span class="team-section">{{ step === "account" ? `Your admin account on ${url}` : "Connect with an account" }}</span>
                <template v-if="step === 'connect'">
                    <FormField label="Team URL" for="team-url" help="The invitation URL an admin sent you, or the address of the team server.">
                        <TextInput id="team-url" :value="url" placeholder="https://team.example.com" @input="url = $event.target.value" />
                    </FormField>
                </template>
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
                        <span>Save this password somewhere safe before you go on: it is shown only here.</span>
                    </p>
                </template>
                <p class="team-sub">
                    {{ step === "account" ? "Everything in this journal, files too, is uploaded to the team." : "With an invitation URL this journal takes the team's copy; it is refused when it holds tasks or messages of its own." }}
                </p>
                <template v-if="failure">
                    <p class="team-refusal">
                        <StateDot state="failed" />
                        <span>{{ failure }}</span>
                    </p>
                </template>
                <div class="team-choices">
                    <Btn kind="primary" :busy="busy" @click="join">{{ busy ? (step === "account" ? "Claiming" : "Connecting") : step === "account" ? "Claim it" : "Connect" }}</Btn>
                    <Btn @click="open(step === 'account' ? 'claim' : 'choice')">Back</Btn>
                </div>
            </form>
        </template>
    </div>
</template>

<style scoped>
.team-connect-panel {
    border-bottom: 1px solid var(--border);
}

.team-choices,
.team-inline {
    display: flex;
    gap: 8px;
}

.team-section {
    color: var(--text-2);
    font-size: 12px;
    font-weight: 500;
}

.team-sub {
    margin: 0;
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
</style>
