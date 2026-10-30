<script setup>
import {computed, ref, watch} from "vue";
import {api} from "../api/client.js";
import {goIn, route} from "../route.js";
import {chatPlan, modeOf, planAgentChats, planAgentChatsMatching, planChatHeader} from "../domain/plans.js";
import {phaseName} from "../domain/organizationBoard.js";
import {store} from "../state/store.js";
import Icon from "../kit/Icon.vue";
import MenuPanel from "../kit/MenuPanel.vue";

const anchor = ref(null);
const search = ref("");
const dropHeight = Math.round(window.innerHeight * 0.6);
const environments = computed(() => store.summary?.environments || []);
const mainName = computed(() => {
    const metadata = new Map((store.rows.environments || []).map((environment) => [environment.key, environment]));
    for (const row of environments.value) metadata.set(row.environment.key, row.environment);
    const byName = new Map([...metadata.values()].map((environment) => [environment.name, environment]));
    let environment = byName.get(route.value.env) || byName.get(store.spec?.environment);
    const seen = new Set();
    while (environment?.parent_key && !seen.has(environment.key)) {
        seen.add(environment.key);
        const parent = metadata.get(environment.parent_key);
        if (!parent) break;
        environment = parent;
    }
    return environment?.name || route.value.env || store.spec?.environment || "";
});
const plans = computed(() => store.organization?.plans || []);
const chats = computed(() => planAgentChats(plans.value, environments.value, mainName.value));
const visible = computed(() => planAgentChatsMatching(chats.value, search.value));
const currentPlan = computed(() => chatPlan(plans.value, route.value.env));
const heading = computed(() => planChatHeader(plans.value, route.value.env));
const phase = computed(() => (currentPlan.value?.phase ? phaseName(currentPlan.value.phase) : ""));
const planPage = computed(() => (currentPlan.value ? api.page(mainName.value, `plans/${currentPlan.value.id}`) : ""));
const currentTitle = computed(() => (currentPlan.value ? currentPlan.value.title : "Main agent"));

watch(() => route.value.env, () => {
    anchor.value = null;
    search.value = "";
});

function toggle(event) {
    event.stopPropagation();
    anchor.value = anchor.value ? null : event.currentTarget;
    search.value = "";
}

function select(chat) {
    anchor.value = null;
    search.value = "";
    if (chat.name !== route.value.env || route.value.page !== "chat") goIn(chat.name, "chat");
}
</script>

<template>
    <div class="plan-agent-chats">
        <a v-if="currentPlan" class="plan-agent-chat-heading" :href="planPage" :title="heading">
            <span>Plan {{ currentPlan.id }} · {{ currentPlan.title }}</span>
            <small>{{ modeOf(currentPlan) }}<template v-if="phase"> · Phase: {{ phase }}</template></small>
        </a>
        <button type="button" class="plan-agent-chat-toggle" aria-label="Choose a chat" :aria-expanded="Boolean(anchor)" @click.stop="toggle">
            <span>{{ currentTitle }}</span>
            <Icon name="chevron" :size="12" />
        </button>
        <template v-if="anchor">
            <MenuPanel :anchor="anchor" :min-width="250" :max-width="320" :max-height="dropHeight" @click.stop @close="anchor = null">
                <label class="plan-agent-chat-search">
                    <span class="visually-hidden">Search chats</span>
                    <input v-model="search" type="search" placeholder="Search chats" @keydown.esc="anchor = null" />
                </label>
                <div class="plan-agent-chat-options" role="list">
                    <button
                        v-for="chat in visible"
                        :key="chat.name"
                        type="button"
                        :class="['plan-agent-chat-option', {selected: chat.name === route.env}]"
                        :aria-current="chat.name === route.env ? 'page' : null"
                        @click="select(chat)"
                    >
                        <span class="plan-agent-chat-option-title">{{ chat.title }}</span>
                        <small v-if="chat.plan">Plan {{ chat.plan.id }} · {{ modeOf(chat.plan) }}</small>
                        <span v-if="chat.unread" class="plan-agent-chat-unread" role="img" aria-label="Unread messages" title="Unread messages" />
                    </button>
                    <p v-if="!visible.length" class="plan-agent-chat-empty">No chats found.</p>
                </div>
            </MenuPanel>
        </template>
    </div>
</template>

<style scoped>
.plan-agent-chats {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.plan-agent-chat-heading {
    display: flex;
    flex-direction: column;
    min-width: 0;
    max-width: 250px;
    color: var(--text-2);
    line-height: 1.3;
    text-decoration: none;
}

.plan-agent-chat-heading > span {
    overflow: hidden;
    color: var(--text);
    font-size: 11.5px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-agent-chat-heading small,
.plan-agent-chat-option small {
    color: var(--text-3);
    font-size: 10.5px;
}

.plan-agent-chat-heading:hover > span {
    color: var(--accent-text);
}

.plan-agent-chat-toggle {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    min-width: 0;
    padding: 5px 7px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: transparent;
    color: var(--text-2);
    font: inherit;
    font-size: 11px;
    cursor: pointer;
}

.plan-agent-chat-toggle > span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-agent-chat-toggle:hover,
.plan-agent-chat-toggle[aria-expanded="true"] {
    background: var(--hover);
    color: var(--text);
}

.plan-agent-chat-search {
    display: block;
    padding: 8px;
}

.plan-agent-chat-search input {
    box-sizing: border-box;
    width: 100%;
    padding: 7px 9px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
    font-size: 12px;
}

.plan-agent-chat-options {
    display: flex;
    flex-direction: column;
    gap: 2px;
    max-height: 48vh;
    overflow-y: auto;
    padding: 0 5px 5px;
}

.plan-agent-chat-option {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-height: 35px;
    padding: 7px 26px 7px 9px;
    border: 0;
    border-radius: 5px;
    background: transparent;
    color: var(--text-2);
    text-align: left;
    cursor: pointer;
}

.plan-agent-chat-option:hover,
.plan-agent-chat-option.selected {
    background: var(--hover);
    color: var(--text);
}

.plan-agent-chat-option-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-agent-chat-unread {
    position: absolute;
    top: 50%;
    right: 10px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent-text);
    transform: translateY(-50%);
}

.plan-agent-chat-empty {
    margin: 0;
    padding: 9px;
    color: var(--text-3);
    font-size: 12px;
}

.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
}
</style>
