<script setup>
import {computed} from "vue";
import {cardinalityLine, modelLine} from "../domain/organizationFormat.js";
import SidePanel from "../kit/SidePanel.vue";
import TextDisplay from "../kit/TextDisplay.vue";

const props = defineProps({
    role: {type: Object, default: null},
    loading: {type: Boolean, default: false},
    problem: {type: String, default: ""},
});
defineEmits(["close"]);

const sections = computed(() => [
    {title: "Responsible for", items: props.role?.responsible || []},
    {title: "Not responsible for", items: props.role?.not_responsible || []},
    {title: "Inputs", items: props.role?.inputs || []},
    {title: "Outputs", items: props.role?.outputs || []},
    {title: "Skills", items: props.role?.skills || []},
    {title: "Tools", items: props.role?.tools || []},
    {title: "Actions that need approval", items: props.role?.approval_required || []},
]);

</script>

<template>
    <SidePanel :title="role?.title || 'Role'" :abstract="role?.description || ''" @close="$emit('close')">
        <div class="role-panel">
            <p v-if="loading" class="role-panel-status">Reading the Role contract…</p>
            <p v-else-if="problem" class="role-panel-error" role="alert">{{ problem }}</p>
            <template v-else-if="role">
                <dl class="role-facts">
                    <dt>Role ID</dt><dd><code>{{ role.id }}</code></dd>
                    <dt>Domain</dt><dd>{{ role.domain }}</dd>
                    <dt>Cardinality</dt><dd>{{ cardinalityLine(role.cardinality) }}</dd>
                    <dt>Writes files</dt><dd>{{ role.writes ? "Yes" : "No" }}</dd>
                    <dt>Models</dt><dd>{{ modelLine(role.models) }}</dd>
                </dl>

                <section v-for="section in sections" :key="section.title" class="role-section">
                    <h3>{{ section.title }}</h3>
                    <ul v-if="section.items.length"><li v-for="item in section.items" :key="item">{{ item }}</li></ul>
                    <p v-else class="role-none">None listed</p>
                </section>

                <section class="role-section">
                    <h3>Edges to other Roles</h3>
                    <ul v-if="role.edges?.length">
                        <li v-for="(edge, index) in role.edges" :key="`${edge.kind}:${edge.to}:${index}`">
                            <strong>{{ edge.kind }}</strong> · {{ edge.to }}<template v-if="edge.about"> — {{ edge.about }}</template>
                        </li>
                    </ul>
                    <p v-else class="role-none">None listed</p>
                </section>

                <section class="role-section role-guidance">
                    <h3>AGENTS.md</h3>
                    <TextDisplay v-if="role.guidance" :text="role.guidance" />
                    <p v-else class="role-none">No AGENTS.md file was found.</p>
                </section>
                <slot name="after-contract" />
            </template>
        </div>
    </SidePanel>
</template>

<style scoped>
.role-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.role-panel-status,
.role-panel-error {
    margin: 0;
    color: var(--text-2);
}

.role-panel-error {
    color: var(--danger);
}

.role-facts {
    display: grid;
    grid-template-columns: 112px minmax(0, 1fr);
    gap: 7px 10px;
    margin: 0;
    font-size: 12.5px;
}

.role-facts dt {
    color: var(--text-3);
}

.role-facts dd {
    min-width: 0;
    margin: 0;
    color: var(--text-2);
    overflow-wrap: anywhere;
}

.role-facts code {
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
}

.role-section h3 {
    margin: 0 0 6px;
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
}

.role-section ul {
    display: grid;
    gap: 4px;
    margin: 0;
    padding-left: 19px;
    color: var(--text-2);
    font-size: 12.5px;
}

.role-none {
    margin: 0;
    color: var(--text-4);
    font-size: 12px;
}

.role-guidance {
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
</style>
