<script setup>
import {computed, ref} from "vue";
import {runUpdate} from "../composables/updates.js";
import Btn from "../kit/Btn.vue";
import CopyButton from "../kit/CopyButton.vue";
import ListBox from "../kit/ListBox.vue";
import StateDot from "../kit/StateDot.vue";
import "./team.css";

const props = defineProps({standing: {type: Object, required: true}});
const DOTS = {in_step: "done", waiting: "running", connecting: "running", not_connected: "failed", version: "you"};
const behind = computed(() => props.standing.state === "version");
const matches = computed(() => props.standing.version === props.standing.running);
const waiting = computed(() => (props.standing.waiting ? String(props.standing.waiting) : "None"));
const updating = ref(false);
const failure = ref("");

async function update() {
    updating.value = true;
    failure.value = (await runUpdate(props.standing.version)) || "";
    updating.value = false;
}
</script>

<template>
    <ListBox title="Sync">
        <div class="team-block">
            <div class="team-status">
                <StateDot :state="DOTS[standing.state]" />
                <span>{{ standing.line }}</span>
            </div>
            <template v-if="behind">
                <div>
                    <Btn kind="primary" :busy="updating" @click="update">Update to {{ standing.version }}</Btn>
                </div>
                <template v-if="failure">
                    <p class="team-failure">{{ failure }}</p>
                </template>
            </template>
            <dl class="team-facts">
                <div class="wide">
                    <dt>Team server</dt>
                    <dd>
                        <span>{{ standing.address }}</span>
                        <CopyButton :text="standing.address" />
                    </dd>
                </div>
                <div>
                    <dt>Team version</dt>
                    <dd>{{ standing.version || "Not known yet" }}</dd>
                </div>
                <div>
                    <dt>This journal's version</dt>
                    <dd :class="{warn: standing.version && !matches}">{{ standing.running }}</dd>
                    <template v-if="standing.version">
                        <p class="team-fine">{{ matches ? "The team's version" : "Not the team's version" }}</p>
                    </template>
                </div>
                <div>
                    <dt>Changes waiting</dt>
                    <dd>{{ waiting }}</dd>
                    <template v-if="behind && standing.waiting">
                        <p class="team-fine">Sent once this journal runs {{ standing.version }}</p>
                    </template>
                </div>
            </dl>
        </div>
    </ListBox>
</template>
