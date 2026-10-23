<script setup>
import CopyButton from "../kit/CopyButton.vue";

defineProps({label: String, address: String});
</script>

<template>
    <div class="wide">
        <dt>{{ label }}</dt>
        <dd>
            <span>{{ address }}</span>
            <CopyButton :text="address" />
        </dd>
    </div>
</template>
