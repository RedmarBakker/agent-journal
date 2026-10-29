<script setup>
import {computed} from "vue";
import OptionsPicker from "../resource/OptionsPicker.vue";
import {useScope} from "../composables/scope.js";
import Approvals from "../organization/Approvals.vue";

const props = defineProps({turn: {type: Object, required: true}});
const scope = useScope();
const question = computed(() =>
    scope.rows("questions").find((q) => q.id === props.turn.question.id) || {table: "questions", ...props.turn.question, text: props.turn.text}
);
const approval = computed(() =>
    scope.rows("approvals").find((row) => row.question_id === question.value.id)
);
</script>

<template>
    <div class="turn-question">
        <Approvals v-if="approval" :approval="approval" :question="question.text" />
        <OptionsPicker v-else :question="question" />
    </div>
</template>

<style scoped>
.turn-question {
    width: 100%;
}

.thread-context {
    margin: 4px 0 0;
    color: var(--text-3);
    font-size: 12.5px;
}
</style>
