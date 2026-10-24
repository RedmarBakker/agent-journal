<script setup>
import {computed} from "vue";
import Btn from "../kit/Btn.vue";
import CopyButton from "../kit/CopyButton.vue";
import FormField from "../kit/FormField.vue";
import StateDot from "../kit/StateDot.vue";
import TextInput from "../kit/TextInput.vue";
import TeamRefusal from "./TeamRefusal.vue";

const props = defineProps({
    step: {type: String, required: true},
    url: {type: String, default: ""},
    email: {type: String, default: ""},
    password: {type: String, default: ""},
    generated: Boolean,
    busy: Boolean,
    failure: {type: String, default: ""},
});
defineEmits(["update:url", "update:email", "update:password", "generate", "join", "open"]);

const claiming = computed(() => props.step === "account");
</script>

<template>
    <form class="team-block" @submit.prevent="$emit('join')">
        <span class="team-section">{{ claiming ? `Your admin account on ${url}` : "Connect with an account" }}</span>
        <template v-if="!claiming">
            <FormField label="Team URL" for="team-url" help="The invitation URL an admin sent you, or the address of the team server.">
                <TextInput id="team-url" :value="url" placeholder="https://team.example.com" @input="$emit('update:url', $event.target.value)" />
            </FormField>
        </template>
        <FormField label="Email" for="team-email" help="Your user name on the team. Filled in from git when git knows it.">
            <TextInput id="team-email" :value="email" type="email" autocomplete="email" @input="$emit('update:email', $event.target.value)" />
        </FormField>
        <FormField label="Password" for="team-password" help="At least 12 characters mixing three of lower case, upper case, digits and symbols, or 20 characters or more.">
            <div class="team-inline">
                <TextInput id="team-password" :value="password" :type="generated ? 'text' : 'password'" :class="{'team-mono': generated}" autocomplete="new-password" @input="$emit('update:password', $event.target.value)" />
                <template v-if="generated">
                    <CopyButton :text="password" hint="Copy the password" />
                </template>
                <Btn @click="$emit('generate')">Generate</Btn>
            </div>
        </FormField>
        <template v-if="generated">
            <p class="team-keep">
                <StateDot state="you" />
                <span>Save this password somewhere safe before you go on: it is shown only here.</span>
            </p>
        </template>
        <p class="team-sub">
            {{ claiming ? "Everything in this journal, files too, is uploaded to the team." : "With an invitation URL this journal takes the team's copy; it is refused when it holds tasks or messages of its own." }}
        </p>
        <TeamRefusal :message="failure" />
        <div class="team-choices">
            <Btn kind="primary" :busy="busy" @click="$emit('join')">{{ busy ? (claiming ? "Claiming" : "Connecting") : claiming ? "Claim it" : "Connect" }}</Btn>
            <Btn @click="$emit('open', claiming ? 'claim' : 'choice')">Back</Btn>
        </div>
    </form>
</template>
