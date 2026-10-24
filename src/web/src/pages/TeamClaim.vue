<script setup>
import Btn from "../kit/Btn.vue";
import FormField from "../kit/FormField.vue";
import TextInput from "../kit/TextInput.vue";
import TeamRefusal from "./TeamRefusal.vue";

defineProps({url: {type: String, default: ""}, busy: Boolean, failure: {type: String, default: ""}});
defineEmits(["update:url", "check", "open"]);
</script>

<template>
    <form class="team-block" @submit.prevent="$emit('check')">
        <span class="team-section">Claim a server</span>
        <FormField label="Server address" for="team-url" help="The URL or IP address the installer printed. The first journal to claim a new server becomes its admin.">
            <TextInput id="team-url" :value="url" placeholder="https://203.0.113.5" @input="$emit('update:url', $event.target.value)" />
        </FormField>
        <TeamRefusal :message="failure" />
        <div class="team-choices">
            <Btn kind="primary" :busy="busy" :disabled="!url.trim()" @click="$emit('check')">{{ busy ? "Checking" : "Next" }}</Btn>
            <Btn @click="$emit('open', 'choice')">Back</Btn>
        </div>
    </form>
</template>
