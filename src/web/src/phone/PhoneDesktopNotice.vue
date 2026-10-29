<script setup>
defineProps({message: {type: String, required: true}});
</script>

<template>
    <p class="phone-desktop-notice" role="status">{{ message }}</p>
</template>

<style scoped>
.phone-desktop-notice {
    margin: 0;
    padding: 22px;
    color: var(--text-2);
}
</style>
