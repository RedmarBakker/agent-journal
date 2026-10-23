<script setup>
import {isOnline, presence} from "../domain/team.js";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import {narrow} from "../platform/view.js";
import "./team.css";

defineProps({devices: {type: Array, required: true}, admin: Boolean});
const HEADS = ["Machine", "Person", "Presence", "Journal version", "Pool offer"];
</script>

<template>
    <ListBox title="Machines" :count="admin ? devices.length : ''">
        <template v-if="!admin">
            <div class="team-block">
                <p class="team-fine">Only an admin is shown the machines.</p>
            </div>
        </template>
        <template v-else-if="narrow">
            <template v-for="device in devices" :key="device.id">
                <div class="team-card">
                    <div class="team-card-top">
                        <StateDot :state="isOnline(device.pulled_at) ? 'done' : ''" />
                        <b class="team-mono">{{ device.name }}</b>
                        <span class="team-fine">{{ presence(isOnline(device.pulled_at), device.pulled_at) }}</span>
                    </div>
                    <dl class="team-facts">
                        <div>
                            <dt>Person</dt>
                            <dd>{{ device.person }}</dd>
                        </div>
                        <div>
                            <dt>Journal version</dt>
                            <dd>Not known yet</dd>
                        </div>
                        <div>
                            <dt>Pool offer</dt>
                            <dd>None offered</dd>
                        </div>
                    </dl>
                </div>
            </template>
        </template>
        <template v-else>
            <div class="team-table">
                <template v-for="head in HEADS" :key="head">
                    <div class="team-th">{{ head }}</div>
                </template>
                <template v-for="device in devices" :key="device.id">
                    <div class="team-td"><span class="team-mono">{{ device.name }}</span></div>
                    <div class="team-td">{{ device.person }}</div>
                    <div class="team-td">
                        <StateDot :state="isOnline(device.pulled_at) ? 'done' : ''" />
                        {{ presence(isOnline(device.pulled_at), device.pulled_at) }}
                    </div>
                    <div class="team-td team-word">Not known yet</div>
                    <div class="team-td">None offered</div>
                </template>
            </div>
        </template>
    </ListBox>
</template>

<style scoped>
.team-table {
    display: grid;
    grid-template-columns: minmax(120px, 1fr) minmax(110px, 1fr) minmax(150px, 1.3fr) 120px minmax(110px, 0.9fr);
}

.team-th,
.team-td {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
}

.team-th {
    height: 30px;
    color: var(--text-4);
    font-size: 11.5px;
}

.team-td {
    min-height: 42px;
}

.team-th:nth-child(5n + 1),
.team-td:nth-child(5n + 1) {
    padding-left: 16px;
}

.team-th:nth-child(5n),
.team-td:nth-child(5n) {
    justify-content: flex-end;
    padding-right: 16px;
}

.team-td:nth-last-child(-n + 5) {
    border-bottom: 0;
}

.team-card {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
}

.team-card + .team-card {
    border-top: 1px solid var(--border);
}

.team-card-top {
    display: flex;
    align-items: center;
    gap: 8px;
}

.team-card-top b {
    flex: 1;
    font-weight: 500;
}
</style>
