<script setup>
import {ref} from "vue";
import {api} from "../api/client.js";
import {agentRunningIn} from "../composables/settings.js";
import {isOnline, machinesOf, onlineCount, presence, ROLES} from "../domain/team.js";
import Btn from "../kit/Btn.vue";
import CopyButton from "../kit/CopyButton.vue";
import Icon from "../kit/Icon.vue";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import {href} from "../route.js";
import {choose} from "../state/environment.js";
import TeamFailure from "./TeamFailure.vue";
import TeamPersonName from "./TeamPersonName.vue";
import "./team.css";

const props = defineProps({people: {type: Array, required: true}, devices: {type: Array, default: () => []}, admin: Boolean});
const LEAD = "A colleague's environment opens read-only: what you write there is a comment, and their agent treats it as a colleague's words.";
const failure = ref("");
const resets = ref({});

async function reset(person) {
    failure.value = "";
    try {
        resets.value = {...resets.value, [person.id]: (await api.resetTeamPassword(person.id)).password};
    } catch (e) {
        failure.value = e.message;
    }
}
</script>

<template>
    <ListBox title="Connected now" :count="`${onlineCount(people)} of ${people.length} online`" :lead="LEAD">
        <template v-if="failure">
            <TeamFailure :text="failure" />
        </template>
        <template v-for="person in people" :key="person.id">
            <div class="team-person">
                <div class="team-person-head">
                    <TeamPersonName :person="person" :sub="ROLES[person.role] || person.role" />
                    <template v-if="admin && !person.me && person.role !== 'relay'">
                        <Btn small @click="reset(person)">Reset password</Btn>
                    </template>
                    <span class="team-presence">
                        <StateDot :state="person.online ? 'done' : ''" />
                        {{ presence(person.online, person.seen_at) }}
                    </span>
                </div>
                <template v-if="resets[person.id]">
                    <div class="team-command">
                        <code>{{ resets[person.id] }}</code>
                        <CopyButton :text="resets[person.id]" label="Copy" />
                    </div>
                    <p class="team-fine">{{ person.name }}'s new password. Pass it on to them; it is shown only here.</p>
                </template>
                <div class="team-person-parts">
                    <div>
                        <span class="team-label">Machines</span>
                        <template v-if="!admin">
                            <p class="team-fine">Only an admin is shown the machines.</p>
                        </template>
                        <template v-else-if="!machinesOf(person, devices).length">
                            <p class="team-fine">None</p>
                        </template>
                        <template v-for="device in machinesOf(person, devices)" :key="device.id">
                            <div class="team-mini">
                                <StateDot :state="isOnline(device.pulled_at) ? 'done' : ''" />
                                <span class="team-mono">{{ device.name }}</span>
                                <span class="team-word">{{ presence(isOnline(device.pulled_at), device.pulled_at) }} · Offers none</span>
                            </div>
                        </template>
                    </div>
                    <div>
                        <span class="team-label">Environments</span>
                        <template v-if="!person.environments.length">
                            <p class="team-fine">None</p>
                        </template>
                        <template v-for="environment in person.environments" :key="environment.id">
                            <div class="team-mini">
                                <span class="team-mono">{{ environment.name }}</span>
                                <template v-if="person.me">
                                    <span class="team-word">{{ agentRunningIn(environment.name) ? "Agent working" : "No agent running" }}</span>
                                </template>
                                <template v-else>
                                    <span class="team-word" />
                                    <Btn small kind="text" :href="href.page()" @click="choose(environment.name)">Open <Icon name="chevronRight" /></Btn>
                                </template>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </template>
    </ListBox>
</template>

<style scoped>
.team-person {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 12px 16px;
}

.team-person + .team-person {
    border-top: 1px solid var(--border);
}

.team-person-head {
    display: flex;
    align-items: center;
    gap: 10px;
}

.team-person-head b {
    display: flex;
    align-items: center;
    gap: 6px;
}

.team-person-parts {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
    gap: 10px 24px;
    margin-left: 36px;
}

.team-person-parts .team-label {
    display: block;
    margin-bottom: 2px;
}

@media (max-width: 700px) {
    .team-person-parts {
        grid-template-columns: minmax(0, 1fr);
        margin-left: 0;
    }
}
</style>
