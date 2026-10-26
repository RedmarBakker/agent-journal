<script setup>
import {computed} from "vue";
import ChatMark from "../kit/ChatMark.vue";
import {meta} from "../domain/tables.js";
import {peek} from "../route.js";

// a document or report made: a chat mark like the creation of any row, its title on the line, its summary shown when it is opened, a click
// on the opened mark opening the row itself, and the word that it is still being written while it is
const props = defineProps({made: {type: Object, required: true}});
const mark = computed(() => ({
    key: `made:${props.made.table}:${props.made.id}`,
    icon: meta(props.made.table).icon,
    label: props.made.title,
    detail: props.made.summary || "",
    settled: props.made.status === "Being written" ? props.made.status : "",
}));
</script>

<template>
    <ChatMark class="thread-made" :mark="mark" :title="`Open the ${meta(made.table).title.toLowerCase()}`" @click="peek(made.table, made.id)" />
</template>
