<script setup>
import ListBox from "../kit/ListBox.vue";
import "./team.css";

defineProps({standing: {type: Object, required: true}});
</script>

<template>
    <ListBox title="Team version">
        <div class="team-block">
            <dl class="team-facts">
                <div>
                    <dt>Pinned version</dt>
                    <dd>{{ standing.version || "Not known yet" }}</dd>
                </div>
                <div>
                    <dt>Versions that sync</dt>
                    <dd>{{ standing.version ? `Only ${standing.version}` : "Not known yet" }}</dd>
                </div>
                <div class="wide">
                    <dt>Machines behind</dt>
                    <p class="team-fine">Not known yet: the machines do not report their version to the team server.</p>
                </div>
            </dl>
            <p class="team-fine">A machine behind keeps its changes until it runs {{ standing.version }}. Its status bar tells its owner which command installs it.</p>
        </div>
    </ListBox>
</template>
