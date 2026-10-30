<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import FormField from "../kit/FormField.vue";
import StateDot from "../kit/StateDot.vue";
import TextInput from "../kit/TextInput.vue";
import LibraryItems from "../resource/LibraryItems.vue";
import TeamServerSetup from "../resource/TeamServerSetup.vue";
import "./team.css";

// The Team page: with no team connected, connect to a server or set one up; once connected, as whom, the people, for an
// admin the invitations and devices, a password change, and the items the team shares
const standing = ref(null);
const failure = ref("");
const busy = ref(false);
const form = ref({url: "", email: "", name: "", password: ""});
const invited = ref(null);
const inviteEmail = ref("");
const devices = ref([]);
const people = ref([]);
const passwords = ref({old: "", fresh: ""});
const changed = ref(false);

async function load() {
    failure.value = "";
    try {
        standing.value = await api.team();
        if (standing.value.connected) await loadMembers();
    } catch (e) {
        failure.value = e.message;
    }
}

async function loadMembers() {
    people.value = (await api.teamPeople()).people;
    devices.value = standing.value.role === "admin" ? (await api.teamDevices()).devices : [];
}

async function acted(work) {
    busy.value = true;
    failure.value = "";
    try {
        await work();
    } catch (e) {
        failure.value = e.message;
    } finally {
        busy.value = false;
    }
}

const connect = () => acted(async () => ((standing.value = await api.connectTeam(form.value)), (form.value.password = ""), await loadMembers()));
const disconnect = () => acted(async () => (standing.value = await api.disconnectTeam()));
const invite = () => acted(async () => (invited.value = await api.inviteToTeam(inviteEmail.value)));
const revoke = (device) => acted(async () => (await api.revokeTeamDevice(device.id), await loadMembers()));
const changePassword = () => acted(async () => (await api.changeTeamPassword(passwords.value.old, passwords.value.fresh), (changed.value = true), (passwords.value = {old: "", fresh: ""})));

onMounted(load);
</script>

<template>
    <section class="team-page">
        <header class="team-head">
            <h1>Team</h1>
            <p class="team-plain">Your team's server: its people, their devices, and the sequences, templates, profiles, readers, skills, documents, files and plans the team shares.</p>
        </header>
        <template v-if="failure">
            <p class="team-failure">{{ failure }}</p>
        </template>
        <template v-if="!standing">
            <EmptyState loading />
        </template>
        <template v-else-if="!standing.connected">
            <div class="team-choices-side">
                <form class="team-block team-card" @submit.prevent="connect">
                    <h2 class="team-section">Connect to a team</h2>
                    <p class="team-plain">A new server's address makes you its admin; an invitation URL makes you a member; your account on a server logs you in.</p>
                    <FormField label="Server address or invitation URL">
                        <TextInput v-model="form.url" placeholder="https://team.example.com" />
                    </FormField>
                    <FormField label="Your email">
                        <TextInput v-model="form.email" placeholder="you@example.com" />
                    </FormField>
                    <FormField label="Your name, as the team sees it">
                        <TextInput v-model="form.name" />
                    </FormField>
                    <FormField label="Your password">
                        <TextInput v-model="form.password" type="password" />
                    </FormField>
                    <Btn kind="primary" :busy="busy" @click="connect">Connect to the team</Btn>
                </form>
                <div class="team-card">
                    <TeamServerSetup />
                </div>
            </div>
        </template>
        <template v-else>
            <div class="team-where">
                <p class="team-status">
                    <StateDot state="done" />
                    <span>Connected to {{ standing.address }} as {{ standing.name }}, {{ standing.role }}</span>
                </p>
                <Btn :busy="busy" @click="disconnect">Disconnect from the team</Btn>
            </div>
            <div class="team-columns">
                <section class="team-part">
                    <h2 class="team-section">People</h2>
                    <template v-for="person in people" :key="person.id">
                        <p class="team-plain">{{ person.name }}, {{ person.role }}</p>
                    </template>
                </section>
                <template v-if="standing.role === 'admin'">
                    <section class="team-part">
                        <h2 class="team-section">Devices</h2>
                        <template v-for="device in devices" :key="device.id">
                            <p class="team-mini">
                                <span class="team-word">{{ device.name }}, user {{ device.account_id }}</span>
                                <template v-if="!device.revoked_at">
                                    <Btn small :busy="busy" @click="revoke(device)">Revoke this device</Btn>
                                </template>
                            </p>
                        </template>
                    </section>
                    <section class="team-part">
                        <h2 class="team-section">Invite a person</h2>
                        <FormField label="Their email">
                            <TextInput v-model="inviteEmail" />
                        </FormField>
                        <Btn :busy="busy" @click="invite">Make an invitation URL</Btn>
                        <template v-if="invited">
                            <p class="team-plain">{{ invited.email }} connects with: {{ invited.url }}</p>
                        </template>
                    </section>
                </template>
                <section class="team-part">
                    <h2 class="team-section">Your password</h2>
                    <FormField label="Your password now">
                        <TextInput v-model="passwords.old" type="password" />
                    </FormField>
                    <FormField label="Your new password">
                        <TextInput v-model="passwords.fresh" type="password" />
                    </FormField>
                    <Btn :busy="busy" @click="changePassword">Change your password</Btn>
                    <template v-if="changed">
                        <p class="team-plain">Your password is changed.</p>
                    </template>
                </section>
            </div>
            <section class="team-shared">
                <h2 class="team-section">Shared items</h2>
                <LibraryItems />
            </section>
        </template>
    </section>
</template>

<style scoped>
.team-page {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 1200px;
    padding: 24px;
}

.team-head h1 {
    margin: 0 0 6px;
    font-size: 20px;
}

.team-head .team-plain {
    max-width: 640px;
}

.team-choices-side {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: start;
    gap: 20px;
}

.team-card {
    border: 1px solid var(--border-3);
    border-radius: 8px;
}

.team-where {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.team-columns {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    align-items: start;
    gap: 24px;
}

.team-part,
.team-shared {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.team-part .btn {
    align-self: flex-start;
}

.team-section {
    margin: 0;
}

@media (max-width: 760px) {
    .team-choices-side {
        grid-template-columns: minmax(0, 1fr);
    }
}
</style>
