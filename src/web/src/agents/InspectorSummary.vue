<script setup>
import {ref} from "vue";
import TaskFact from "../tasks/TaskFact.vue";
import TaskStatusIcon from "../tasks/TaskStatusIcon.vue";

defineProps({
    name: {type: String, required: true},
    state: {type: Object, required: true},
    moves: {type: Array, default: () => []},
    facts: {type: Array, default: () => []},
    parts: {type: Array, default: () => []},
});
const whole = ref(new Set());
const LONG = 160;
const show = (title) => (whole.value = new Set(whole.value).add(title));
</script>

<template>
    <div class="summary">
        <div class="stamp"><slot name="stamp" /></div>
        <h3 class="title">{{ name }}</h3>
        <div class="state-line">
            <span class="state">
                <TaskStatusIcon :status="state.icon" />
                {{ state.word }}
            </span>
            <template v-if="state.since">
                <span class="since">{{ state.since }}</span>
            </template>
        </div>
        <template v-if="moves.length">
            <div class="moves">
                <template v-for="(move, i) in moves" :key="i">
                    <span :class="move.at">
                        {{ move.word }}
                        <template v-if="move.time">
                            <b>{{ move.time }}</b>
                        </template>
                    </span>
                </template>
            </div>
        </template>
        <div class="facts">
            <template v-for="fact in facts" :key="fact.label">
                <TaskFact :label="fact.label">
                    <span :class="{mono: fact.mono}">{{ fact.value }}</span>
                </TaskFact>
            </template>
        </div>
        <template v-if="parts.length">
            <div class="parts">
                <template v-for="part in parts" :key="part.title">
                    <section class="part">
                        <h4>{{ part.title }}</h4>
                        <template v-if="part.text">
                            <p :class="['text', {clamped: !whole.has(part.title)}]">{{ part.text }}</p>
                            <template v-if="part.text.length > LONG && !whole.has(part.title)">
                                <button type="button" class="more" @click="show(part.title)">Show all</button>
                            </template>
                        </template>
                        <template v-else>
                            <p class="text none">{{ part.none }}</p>
                        </template>
                    </section>
                </template>
            </div>
        </template>
    </div>
</template>

<style scoped>
.summary {
    flex: none;
    max-height: 45%;
    overflow-y: auto;
    padding: 18px 20px;
    border-bottom: 1px solid var(--border);
    scrollbar-width: thin;
}

.stamp {
    color: var(--text-3);
    font-size: 12px;
}

.title {
    margin: 6px 0 12px;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.3;
}

.state-line {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}

.state {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text);
    font-size: 12.5px;
}

.since {
    color: var(--text-3);
    font-size: 12px;
}

.moves {
    display: flex;
    flex-wrap: wrap;
    gap: 2px 0;
    margin-top: 8px;
    color: var(--text-3);
    font-size: 12px;
}

.moves span + span::before {
    content: "·";
    margin: 0 7px;
    color: var(--text-4);
}

.moves b {
    color: var(--text-4);
    font: 400 11.5px var(--mono);
}

.moves .now {
    color: var(--text);
}

.moves .later {
    color: var(--text-4);
}

.facts {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 32px;
    margin-top: 16px;
}

.mono {
    font-family: var(--mono);
    font-size: 11.5px;
}

.parts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px 32px;
    margin-top: 16px;
}

.part h4 {
    margin: 0 0 6px;
    color: var(--text-3);
    font-size: 12px;
    font-weight: 500;
}

.text {
    margin: 0;
    color: var(--text-2);
    white-space: pre-wrap;
    text-wrap: pretty;
}

.text.clamped {
    display: -webkit-box;
    overflow: hidden;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.text.none {
    color: var(--text-4);
}

.more {
    margin-top: 4px;
    padding: 0;
    border: 0;
    background: none;
    color: var(--text-3);
    font: 12px var(--font);
    cursor: pointer;
}

.more:hover {
    color: var(--text);
}
</style>
