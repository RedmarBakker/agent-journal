<script setup>
import ListBox from "../kit/ListBox.vue";
import Stepper from "../kit/Stepper.vue";
import "./team.css";
</script>

<template>
    <ListBox title="Worker pool offer">
        <div class="team-block">
            <div class="team-field">
                <span class="team-field-label">Workers offered to the team</span>
                <Stepper :value="0" :min="0" :max="0" label="Workers offered to the team" />
            </div>
            <dl class="team-facts">
                <div>
                    <dt>Lent out now</dt>
                    <dd>0</dd>
                </div>
                <div>
                    <dt>Free now</dt>
                    <dd>0</dd>
                </div>
            </dl>
            <p class="team-fine">
                A colleague's agent can start up to this many workers on this machine. They run with your model account, so you pay for their runs. The
                offer can be set once the worker pool is part of the journal.
            </p>
        </div>
    </ListBox>
</template>

<style scoped>
.team-field {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
}

.team-field-label {
    color: var(--text-2);
    font-size: 12px;
    font-weight: 500;
}
</style>
