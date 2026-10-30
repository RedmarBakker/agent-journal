<script setup>
import {computed, onMounted, ref, watch} from "vue";
import {api} from "../api/client.js";
import {domainCounts} from "../domain/organizationCounts.js";
import {cardinalityLine, modelLine} from "../domain/organizationFormat.js";
import {href, route} from "../route.js";
import {store} from "../state/store.js";
import Btn from "../kit/Btn.vue";
import EmptyState from "../kit/EmptyState.vue";
import OrganizationPlanBoard from "../organization/OrganizationPlanBoard.vue";
import OrganizationRolePanel from "./OrganizationRolePanel.vue";

const organization = ref(null);
const loading = ref(true);
const reading = ref(false);
const problem = ref("");
const selectedRole = ref(null);
const roleLoading = ref(false);
const roleProblem = ref("");

const folder = computed(() => organization.value?.folder ?? store.settings?.workers?.organization_folder ?? "");
const commit = computed(() => organization.value?.commit || "");
const domains = computed(() => organization.value?.domains || []);
const declaredEdges = computed(() => domains.value.flatMap((domain) => [
    ...(domain.edges || []).map((edge) => ({sourceId: `domain:${domain.id}`, targetId: `domain:${edge.to}`, source: `Domain ${domain.title}`, kind: edge.kind, target: `domain:${edge.to}`, about: edge.about})),
    ...(domain.roles || []).flatMap((role) => (role.edges || []).map((edge) => ({sourceId: `role:${domain.id}/${role.id}`, targetId: `role:${domain.id}/${edge.to}`, source: `Role ${domain.title} / ${role.title}`, kind: edge.kind, target: `role:${domain.id}/${edge.to}`, about: edge.about}))),
]));
const selectedDomain = computed(() => domains.value.find((domain) => domain.id === route.value.domain) || null);
const communicationEdges = computed(() => {
    if (!selectedDomain.value) return [];
    const domainId = `domain:${selectedDomain.value.id}`;
    const rolePrefix = `role:${selectedDomain.value.id}/`;
    return declaredEdges.value.filter((edge) =>
        edge.sourceId === domainId || edge.targetId === domainId ||
        edge.sourceId.startsWith(rolePrefix) || edge.targetId.startsWith(rolePrefix));
});
const problems = computed(() => organization.value?.problems || []);
const counts = computed(domainCounts);

const roleInstances = (domain, role) => counts.value[domain]?.roles?.[role.id]?.instances ?? role.instances ?? 0;
const activePlans = (domain) => counts.value[domain.id]?.plansActive ?? domain.plans_active ?? 0;
const running = (domain) => domain.roles.reduce((total, role) => total + roleInstances(domain.id, role), 0);

async function readRole() {
    const {domain, role} = route.value;
    if (!domain || !role) {
        selectedRole.value = null;
        roleProblem.value = "";
        roleLoading.value = false;
        return;
    }
    const target = `${domain}/${role}`;
    selectedRole.value = null;
    roleProblem.value = "";
    roleLoading.value = true;
    try {
        const detail = await api.organizationRole(domain, role);
        if (`${route.value.domain}/${route.value.role}` === target) selectedRole.value = detail;
    } catch (error) {
        roleProblem.value = error.message;
    } finally {
        roleLoading.value = false;
    }
}

async function readFolder(again = false) {
    if (again) reading.value = true;
    else loading.value = true;
    problem.value = "";
    try {
        organization.value = again ? await api.reloadOrganization() : await api.organization();
        if (route.value.domain && route.value.role) await readRole();
    } catch (error) {
        problem.value = error.message;
    } finally {
        loading.value = false;
        reading.value = false;
    }
}

function openRole(domain, role) {
    location.hash = href.role(domain, role);
}

function openDomain(domain) {
    location.hash = href.domain(domain.id);
}

function openOrganization() {
    location.hash = href.organization();
}

function closeRole() {
    location.hash = route.value.domain ? href.domain(route.value.domain) : href.organization();
}

watch(() => `${route.value.domain}/${route.value.role}`, readRole);
onMounted(() => readFolder());
</script>

<template>
    <section class="organization-page" aria-label="Organization">
        <header class="organization-head">
            <div class="organization-title">
                <h1>Organization</h1>
                <dl class="organization-source">
                    <dt>Folder</dt>
                    <dd><code>{{ folder || "No folder set" }}</code></dd>
                    <dt>Commit</dt>
                    <dd><code>{{ commit || "No Git commit" }}</code></dd>
                </dl>
            </div>
            <Btn kind="ghost" small :disabled="reading" @click="readFolder(true)">Read the folder again</Btn>
        </header>

        <p v-if="problem" class="organization-error" role="alert">{{ problem }}</p>
        <OrganizationPlanBoard v-if="loading && route.domain" :loading="true" />
        <EmptyState v-else-if="loading" class="organization-empty" :loading="true" title="Reading the organization" />
        <template v-else-if="organization">
            <section v-if="problems.length" class="contract-problems" aria-label="Contract problems">
                <h2>Contract problems <span>{{ problems.length }}</span></h2>
                <ul>
                    <li v-for="(item, index) in problems" :key="`${item.path}:${item.rule}:${index}`">
                        <code>{{ item.path }}</code>
                        <span class="problem-rule">{{ item.rule }}</span>
                        <p>{{ item.message }}</p>
                    </li>
                </ul>
            </section>

            <EmptyState v-if="!folder && !domains.length && !problems.length" class="organization-empty" title="No organization folder is set">
                Set the organization folder in Settings to show its domains and Roles here.
            </EmptyState>

            <section v-else-if="selectedDomain" class="organization-domain-page">
                <button type="button" class="organization-all-domains" @click="openOrganization">All domains</button>
                <section v-if="communicationEdges.length" class="communication-edges" :data-domain="selectedDomain.id" :aria-label="`Declared communication edges in ${selectedDomain.title}`">
                    <h2>Declared communication edges</h2>
                    <div class="communication-edges-table">
                        <table>
                            <thead><tr><th scope="col">From</th><th scope="col">Kind</th><th scope="col">To</th><th scope="col">About</th></tr></thead>
                            <tbody>
                                <tr v-for="(edge, index) in communicationEdges" :key="`${edge.source}:${edge.kind}:${edge.target}:${index}`" data-communication-edge>
                                    <td>{{ edge.source }}</td><td class="communication-edge-kind">{{ edge.kind }}</td><td>{{ edge.target }}</td><td>{{ edge.about }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>
                <OrganizationPlanBoard :domains="[selectedDomain]" />
            </section>

            <EmptyState v-else-if="route.domain" class="organization-empty" title="Domain not found">
                This domain is not in the organization folder.
            </EmptyState>

            <div v-else class="domain-grid">
                <article v-for="domain in domains" :key="domain.id" class="domain-card">
                    <header class="domain-head">
                        <span class="domain-icon" aria-hidden="true">{{ domain.icon }}</span>
                        <div>
                            <h2><button type="button" class="domain-board-link" :aria-label="`Open ${domain.title} board`" @click="openDomain(domain)">{{ domain.title }}</button></h2>
                            <p>{{ domain.description }}</p>
                        </div>
                    </header>
                    <div class="domain-meta">
                        <span>Roles: {{ domain.roles.length }}</span>
                        <span>Running: {{ running(domain) }}</span>
                        <span>Model: {{ modelLine(domain.models) }}</span>
                    </div>
                    <div class="role-list">
                        <div class="domain-agent-row" :data-domain-agent="domain.id">
                            <span class="role-name">Domain agent</span>
                            <span>Cardinality: One per active plan</span>
                            <span>Model: {{ modelLine(domain.models) }}</span>
                            <span>Running now: {{ activePlans(domain) ? "Yes" : "No" }}</span>
                        </div>
                        <button
                            v-for="role in domain.roles"
                            :key="role.id"
                            class="role-row"
                            type="button"
                            :aria-label="`Open ${role.title}`"
                            @click="openRole(domain.id, role.id)"
                        >
                            <span class="role-name">{{ role.title }} <small>{{ role.id }}</small></span>
                            <span>Cardinality: {{ cardinalityLine(role.cardinality) }}</span>
                            <span>Writes files: {{ role.writes ? "Yes" : "No" }}</span>
                            <span>Model: {{ modelLine(role.models) }}</span>
                            <span>Running now: {{ roleInstances(domain.id, role) ? "Yes" : "No" }} ({{ roleInstances(domain.id, role) }})</span>
                        </button>
                    </div>
                </article>
            </div>
        </template>

        <OrganizationRolePanel
            v-if="route.role"
            :role="selectedRole"
            :loading="roleLoading"
            :problem="roleProblem"
            @close="closeRole"
        />
    </section>
</template>

<style scoped>
.organization-page {
    padding: 0 0 40px;
}

.organization-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
    padding: 18px 22px;
    border-bottom: 1px solid var(--border);
}

.organization-title h1 {
    margin: 0 0 10px;
    font-size: 20px;
    font-weight: 650;
}

.organization-source {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 4px 10px;
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}

.organization-source dt {
    color: var(--text-2);
}

.organization-source dd {
    min-width: 0;
    margin: 0;
    overflow-wrap: anywhere;
}

.organization-source code {
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
}

.organization-error {
    margin: 14px 22px;
    color: var(--danger);
}

.organization-empty {
    max-width: 500px;
    margin: 38px auto;
}

.contract-problems {
    margin: 18px 22px 0;
    padding: 14px 16px;
    border: 1px solid color-mix(in srgb, var(--danger) 50%, var(--border));
    border-radius: 10px;
    background: color-mix(in srgb, var(--danger) 8%, var(--raised));
}

.communication-edges {
    margin: 18px 22px 0;
}

.communication-edges h2 {
    margin: 0 0 9px;
    font-size: 15px;
}

.communication-edges-table {
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 9px;
}

.communication-edges table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
}

.communication-edges th,
.communication-edges td {
    padding: 8px 10px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}

.communication-edges tr:last-child td {
    border-bottom: 0;
}

.communication-edges th {
    color: var(--text-2);
    font-weight: 600;
}

.communication-edge-kind {
    color: var(--accent-text);
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    white-space: nowrap;
}

.contract-problems h2 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 10px;
    font-size: 14px;
}

.contract-problems h2 span {
    color: var(--danger);
    font-size: 12px;
}

.contract-problems ul {
    display: grid;
    gap: 9px;
    margin: 0;
    padding: 0;
    list-style: none;
}

.contract-problems li {
    display: grid;
    grid-template-columns: minmax(120px, auto) minmax(80px, auto) minmax(0, 1fr);
    align-items: baseline;
    gap: 8px 12px;
    color: var(--text-2);
    font-size: 12.5px;
}

.contract-problems code,
.problem-rule {
    color: var(--text-3);
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    overflow-wrap: anywhere;
}

.contract-problems p {
    margin: 0;
}

.domain-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr));
    gap: 14px;
    padding: 18px 22px 0;
}

.domain-card {
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--raised);
}

.domain-head {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 15px 16px 10px;
}

.domain-icon {
    width: 28px;
    flex: none;
    font-size: 20px;
    line-height: 1.2;
    text-align: center;
}

.domain-head h2 {
    margin: 0;
    font-size: 15px;
    font-weight: 650;
}

.domain-board-link {
    padding: 0;
    border: 0;
    background: transparent;
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.domain-board-link:hover {
    color: var(--accent-text);
}

.organization-domain-page {
    padding: 18px 22px 0;
}

.organization-all-domains {
    margin: 0 0 14px;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--accent-text);
    font: inherit;
    font-size: 12px;
    cursor: pointer;
}

.domain-head p {
    margin: 4px 0 0;
    color: var(--text-3);
    font-size: 12.5px;
}

.domain-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 12px;
    padding: 0 16px 11px 54px;
    color: var(--text-3);
    font-size: 11.5px;
}

.role-list {
    display: grid;
    border-top: 1px solid var(--border);
}

.domain-agent-row {
    display: grid;
    grid-template-columns: minmax(120px, 1fr) minmax(130px, 1.15fr) minmax(160px, 1.25fr) auto;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-2);
    font-size: 11.5px;
}

.role-row {
    display: grid;
    grid-template-columns: minmax(120px, 1fr) minmax(130px, 1.15fr) minmax(92px, 0.8fr) minmax(160px, 1.25fr) auto;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 10px 14px;
    border: 0;
    border-bottom: 1px solid var(--border);
    background: transparent;
    color: var(--text-2);
    font: inherit;
    font-size: 11.5px;
    text-align: left;
    cursor: pointer;
}

.role-row:last-child {
    border-bottom: 0;
}

.role-row:hover,
.role-row:focus-visible {
    background: var(--hover);
    outline: none;
}

.role-name {
    color: var(--text);
    font-size: 12.5px;
    font-weight: 600;
}

.role-name small {
    display: block;
    margin-top: 2px;
    color: var(--text-4);
    font-size: 10.5px;
    font-weight: 400;
}

@media (max-width: 900px) {
    .role-row,
    .domain-agent-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 560px) {
    .organization-head {
        flex-direction: column;
        align-items: stretch;
        padding: 14px;
    }

    .domain-grid {
        padding: 14px 12px 0;
    }

    .organization-domain-page {
        padding: 14px 12px 0;
    }

    .contract-problems {
        margin: 14px 12px 0;
    }

    .contract-problems li {
        grid-template-columns: minmax(0, 1fr);
        gap: 4px;
    }

    .role-row,
    .domain-agent-row {
        grid-template-columns: minmax(0, 1fr);
    }
}
</style>
