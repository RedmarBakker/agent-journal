<script setup>
import {href} from "../route.js";
</script>

<template>
    <section class="supervisor-not-set-up" data-supervisor-not-set-up role="status">
        <p>The supervisor is not set up for this environment.</p>
        <p>To set it up, start an owner plan for this environment.</p>
        <a data-supervisor-setup :href="href.page('plans')">Open Plans</a>
    </section>
</template>

<style scoped>
.supervisor-not-set-up {
    display: grid;
    gap: 8px;
    padding: 12px;
    border-radius: 8px;
    background: var(--side);
    color: var(--text-2);
}

.supervisor-not-set-up p { margin: 0; }
.supervisor-not-set-up a { justify-self: start; }
</style>
