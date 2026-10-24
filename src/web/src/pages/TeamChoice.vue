<script setup>
import Btn from "../kit/Btn.vue";

defineEmits(["open"]);
</script>

<template>
    <div class="team-block">
        <span class="team-section">Connect to a team server</span>
        <p class="team-plain">Claim a new team server to become its admin, or connect to one you have an account or an invitation for.</p>
        <div class="team-choices">
            <Btn kind="primary" @click="$emit('open', 'claim')">Claim a server</Btn>
            <Btn @click="$emit('open', 'connect')">Connect with an account</Btn>
        </div>
    </div>
</template>
