<script setup>
import {onMounted, ref} from "vue";
import {api} from "../api/client.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import StateDot from "../kit/StateDot.vue";
import TextInput from "../kit/TextInput.vue";
import "./team.css";

// The Settings Library tab: connect this journal to the team's library by its URL, see as whom it is connected, disconnect, and for an
// admin the invitations, devices and people; a password change for everyone
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
        standing.value = await api.library();
        if (standing.value.connected) await loadMembers();
    } catch (e) {
        failure.value = e.message;
    }
}

async function loadMembers() {
    people.value = (await api.libraryPeople()).people;
    devices.value = standing.value.role === "admin" ? (await api.libraryDevices()).devices : [];
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

const connect = () => acted(async () => ((standing.value = await api.connectLibrary(form.value)), (form.value.password = ""), await loadMembers()));
const disconnect = () => acted(async () => (standing.value = await api.disconnectLibrary()));
const invite = () => acted(async () => (invited.value = await api.inviteToLibrary(inviteEmail.value)));
const revoke = (device) => acted(async () => (await api.revokeLibraryDevice(device.id), await loadMembers()));
const changePassword = () => acted(async () => (await api.changeLibraryPassword(passwords.value.old, passwords.value.fresh), (changed.value = true), (passwords.value = {old: "", fresh: ""})));

onMounted(load);
</script>

<template>
    <div class="team-pane">
        <template v-if="failure">
            <p class="team-failure">{{ failure }}</p>
        </template>
        <template v-if="!standing">
            <EmptyState loading />
        </template>
        <template v-else-if="!standing.connected">
            <form class="library-form" @submit.prevent="connect">
                <p class="team-plain">A new server's address makes you its admin; an invitation URL makes you a member.</p>
                <TextInput v-model="form.url" placeholder="The library's address or invitation URL" />
                <TextInput v-model="form.email" placeholder="Your email" />
                <TextInput v-model="form.name" placeholder="Your name, as the team sees it" />
                <TextInput v-model="form.password" type="password" placeholder="Your password" />
                <Btn kind="primary" :busy="busy" @click="connect">Connect to the library</Btn>
            </form>
        </template>
        <template v-else>
            <div class="team-where">
                <p class="team-joined">
                    <StateDot state="done" />
                    <span>Connected to {{ standing.address }} as {{ standing.name }}, {{ standing.role }}</span>
                </p>
                <Btn :busy="busy" @click="disconnect">Disconnect from the library</Btn>
            </div>
            <section class="library-section">
                <h4>People</h4>
                <template v-for="person in people" :key="person.id">
                    <p class="team-plain">{{ person.name }}, {{ person.role }}</p>
                </template>
            </section>
            <template v-if="standing.role === 'admin'">
                <section class="library-section">
                    <h4>Invite a person</h4>
                    <TextInput v-model="inviteEmail" placeholder="Their email" />
                    <Btn :busy="busy" @click="invite">Make an invitation URL</Btn>
                    <template v-if="invited">
                        <p class="team-plain">{{ invited.email }} connects with: {{ invited.url }}</p>
                    </template>
                </section>
                <section class="library-section">
                    <h4>Devices</h4>
                    <template v-for="device in devices" :key="device.id">
                        <p class="team-plain">
                            {{ device.name }}, user {{ device.account_id }}
                            <template v-if="!device.revoked_at">
                                <Btn small :busy="busy" @click="revoke(device)">Revoke this device</Btn>
                            </template>
                        </p>
                    </template>
                </section>
            </template>
            <section class="library-section">
                <h4>Your password</h4>
                <TextInput v-model="passwords.old" type="password" placeholder="Your password now" />
                <TextInput v-model="passwords.fresh" type="password" placeholder="Your new password" />
                <Btn :busy="busy" @click="changePassword">Change your password</Btn>
                <template v-if="changed">
                    <p class="team-plain">Your password is changed.</p>
                </template>
            </section>
        </template>
    </div>
</template>

<style scoped>
.library-form,
.library-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 460px;
    margin-top: 16px;
}

.library-section h4 {
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
    font-weight: 500;
}
</style>
