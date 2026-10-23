<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import Icon from "../kit/Icon.vue";
import PageBar from "../kit/PageBar.vue";
import {project} from "../state/identity.js";
import {store} from "../state/store.js";
import TeamConnect from "./TeamConnect.vue";
import TeamHosted from "./TeamHosted.vue";
import TeamLocal from "./TeamLocal.vue";
import "./team.css";

const standing = ref(null);
const people = ref([]);
const devices = ref([]);
const failure = ref("");
const outcome = ref("");
const opening = ref(false);
const hosted = computed(() => Boolean(store.people && store.people.hosted));
const host = (address) => String(address || "").replace(/^https?:\/\//, "");
const me = computed(() => people.value.find((person) => person.me) || null);
const machine = computed(() => devices.value.find((device) => device.this) || null);
const line = computed(() => {
    if (!standing.value || !standing.value.joined) return "";
    if (hosted.value) return [`Hosted journal at ${host(standing.value.address)}`, me.value && `signed in as ${me.value.name}`].filter(Boolean).join(" · ");
    return [project.value, machine.value && `this machine: ${machine.value.name}`].filter(Boolean).join(" · ");
});

async function load() {
    try {
        standing.value = await api.team();
        if (!standing.value.joined) return;
        people.value = (await api.teamPeople()).people;
        if (standing.value.admin) devices.value = (await api.teamDevices()).devices;
    } catch (e) {
        failure.value = e.message;
    }
}

async function joined(text) {
    outcome.value = text;
    await load();
}

async function openShared() {
    opening.value = true;
    failure.value = "";
    try {
        window.open((await api.openSharedJournal()).url, "_blank", "noopener");
    } catch (e) {
        failure.value = e.message;
    } finally {
        opening.value = false;
    }
}

onMounted(load);
</script>

<template>
    <section class="team-page">
        <PageBar>
            <h2 class="team-page-title">Team</h2>
            <span class="team-page-line">{{ line }}</span>
            <span class="team-page-grow" />
            <template v-if="standing && standing.joined && !hosted">
                <Btn small :busy="opening" @click="openShared">Open the shared journal <Icon name="open" :size="12" /></Btn>
            </template>
        </PageBar>
        <div class="team-page-content">
            <template v-if="failure">
                <p class="team-failure">{{ failure }}</p>
            </template>
            <template v-if="outcome">
                <p class="team-line">{{ outcome }}</p>
            </template>
            <template v-if="!standing && !failure">
                <EmptyState loading />
            </template>
            <template v-else-if="standing && !standing.joined">
                <div class="team-connect">
                    <TeamConnect :email="standing.email" @joined="joined" />
                </div>
            </template>
            <template v-else-if="standing && hosted">
                <TeamHosted :standing="standing" :people="people" :devices="devices" />
            </template>
            <template v-else-if="standing">
                <TeamLocal :standing="standing" :people="people" :devices="devices" />
            </template>
        </div>
    </section>
</template>

<style scoped>
.team-page {
    display: flex;
    flex-direction: column;
    min-height: 100%;
}

.team-page-title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}

.team-page-line {
    color: var(--text-4);
    font-size: 12px;
}

.team-page-grow {
    flex: 1;
}

.team-page-content {
    display: flex;
    flex-direction: column;
    gap: 18px;
    padding: 24px 32px 36px;
}

.team-connect {
    max-width: 640px;
}

@media (max-width: 700px) {
    .team-page-content {
        padding: 16px;
    }
}
</style>
