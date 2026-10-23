<script setup>
defineProps({line: {type: Object, required: true}});
</script>

<template>
    <div class="team-row">
        <div class="team-row-main">
            <b>{{ line.name }}</b>
            <span class="team-row-sub">{{ [line.task, line.owner, `${line.minutes} min`].filter(Boolean).join(" · ") }}</span>
        </div>
        <slot />
    </div>
</template>
