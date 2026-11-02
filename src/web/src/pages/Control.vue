<script setup>
import {computed, onMounted, ref} from "vue";
import {api} from "../api/client.js";

const OPTIONS = [
    {value: "not_allowed", label: "Not allowed"},
    {value: "propose_only", label: "Propose only"},
    {value: "may_act", label: "May act"},
];

const control = ref(null);
const expanded = ref(false);
const problem = ref("");
const saving = ref("");
const visibleDecisions = computed(() => {
    const decisions = control.value?.tier_three_decisions || [];
    return expanded.value ? decisions : decisions.slice(0, 5);
});

async function load() {
    try {
        control.value = await api.supervisorControl();
        problem.value = "";
    } catch (error) {
        problem.value = error.message;
    }
}

async function decide(item, decision) {
    saving.value = item.command;
    problem.value = "";
    try {
        await api.saveSupervisorDecision(control.value.grant_id, control.value.grant_version, item.command, decision);
        await load();
    } catch (error) {
        problem.value = error.message;
    } finally {
        saving.value = "";
    }
}

onMounted(load);
</script>

<template>
    <main class="control-page">
        <h1>Control</h1>
        <p v-if="problem" role="alert">{{ problem }}</p>
        <p v-if="!control && !problem">Loading supervisor control…</p>
        <template v-if="control">
            <section aria-labelledby="needs-decision">
                <header class="control-heading">
                    <div>
                        <h2 id="needs-decision">Needs your decision</h2>
                        <p>Choose what the supervisor may do for each tier 3 verb.</p>
                    </div>
                    <button v-if="control.tier_three_decisions.length > 5" type="button" @click="expanded = !expanded">
                        {{ expanded ? "Show fewer" : "Show all" }}
                    </button>
                </header>
                <ul class="decision-list">
                    <li
                        v-for="(item, index) in visibleDecisions"
                        :key="item.command"
                        class="decision-row"
                        :data-command="item.command"
                    >
                        <div class="decision-name">
                            <strong>{{ item.area }}</strong>
                            <span>{{ item.command }}</span>
                        </div>
                        <fieldset :disabled="saving === item.command">
                            <legend>{{ item.command }} decision</legend>
                            <label v-for="option in OPTIONS" :key="option.value" :for="`decision-${index}-${option.value}`">
                                <input
                                    :id="`decision-${index}-${option.value}`"
                                    type="radio"
                                    :name="`decision-${index}`"
                                    :value="option.value"
                                    :checked="item.decision === option.value"
                                    @change="decide(item, option.value)"
                                >
                                {{ option.label }}
                            </label>
                        </fieldset>
                    </li>
                </ul>
            </section>
            <section aria-labelledby="never-allowed">
                <h2 id="never-allowed">Never allowed</h2>
                <p>Changing its own grant stays fixed at Never.</p>
                <ul class="never-list">
                    <li v-for="item in control.never_allowed" :key="item.command" :data-command="item.command">
                        <span>{{ item.area }}: {{ item.command }}</span>
                        <strong>Never</strong>
                    </li>
                </ul>
            </section>
        </template>
    </main>
</template>

<style scoped>
.control-page { max-width: 1100px; margin: 0 auto; padding: 24px; }
.control-heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.decision-list, .never-list { list-style: none; margin: 0; padding: 0; }
.decision-row, .never-list li { border-top: 1px solid var(--line, #555); padding: 14px 0; }
.decision-name { display: flex; gap: 12px; margin-bottom: 8px; }
.decision-row fieldset { display: flex; flex-wrap: wrap; gap: 12px 20px; border: 0; padding: 0; }
.decision-row legend { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }
.decision-row label { display: inline-flex; align-items: center; gap: 6px; }
.never-list li { display: flex; justify-content: space-between; gap: 12px; }
</style>
