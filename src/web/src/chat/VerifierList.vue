<script setup>
import {computed} from "vue";
import CloseButton from "../kit/CloseButton.vue";
import Btn from "../kit/Btn.vue";
import Skeleton from "../kit/Skeleton.vue";
import {judgedLine, verifierName, verifierWord} from "../domain/verifiers.js";
import {ago} from "../format/time.js";
import {seconds} from "../domain/row.js";
import {peek} from "../route.js";

const props = defineProps({rows: {type: Array, default: () => []}, loading: Boolean});
const emit = defineEmits(["close"]);
const newest = computed(() => [...props.rows].sort((a, b) => b.id - a.id));
const judging = computed(() => props.rows.filter((row) => row.state === "verifying").length);
const sessionLine = (row) => [row.session ? `Session ${row.session.slice(0, 8)}` : "", `sent ${ago(seconds(row.created_at))}`, judgedLine(row)].filter(Boolean).join(" · ");

function inspect(row) {
    peek("verifiers", row.id);
    emit("close");
}
</script>

<template>
    <div class="verifiers">
        <header class="verifiers-head">
            <div>
                <h4 class="verifiers-heading">Verifiers</h4>
                <span class="verifiers-counts">{{ judging ? `${judging} judging` : "" }}</span>
            </div>
            <CloseButton @click="emit('close')" />
        </header>
        <div class="verifiers-body">
            <template v-if="!rows.length && loading">
                <Skeleton :count="2" label="Loading the verifiers" />
            </template>
            <template v-else-if="!rows.length">
                <p class="verifiers-none">No verifier has been sent here yet. The journal sends one when the agent dismisses a reader report.</p>
            </template>
            <template v-for="row in newest" :key="row.id">
                <Btn kind="text" :class="['verifier', row.state]" v-tip="'Open this verifier'" @click="inspect(row)">
                    <span :class="['verifier-dot', row.state]" />
                    <span class="verifier-what">
                        <strong class="verifier-name">{{ verifierName(row) }}</strong>
                        <span class="verifier-state">{{ verifierWord(row) }}</span>
                        <small class="verifier-session">{{ sessionLine(row) }}</small>
                    </span>
                </Btn>
            </template>
        </div>
    </div>
</template>

<style scoped>
.verifiers {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
}

.verifiers-head {
    display: flex;
    flex: none;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 2px 2px 8px 8px;
    border-bottom: 1px solid var(--line);
}

.verifiers-heading {
    margin: 0;
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.verifiers-counts {
    margin-left: 8px;
    color: var(--text-3);
    font-size: 12px;
}

.verifiers-body {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding-top: 4px;
}

.verifier {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
    padding: 6px 8px;
    text-align: left;
}

.verifier-dot {
    flex: none;
    width: 7px;
    height: 7px;
    margin-top: 6px;
    border-radius: 50%;
    background: var(--text-3);
}

.verifier-dot.verifying {
    background: var(--accent);
}

.verifier-dot.judged {
    background: var(--tone-work);
}

.verifier-what {
    display: flex;
    flex-direction: column;
    gap: 1px;
    min-width: 0;
}

.verifier-name {
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.verifier-state {
    color: var(--text-2);
    font-size: 12px;
}

.verifier-session {
    color: var(--text-3);
    font-size: 11px;
}

.verifiers-none {
    margin: 8px;
    color: var(--text-3);
    font-size: 12px;
}
</style>
