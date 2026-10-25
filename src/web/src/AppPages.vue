<script setup>
import SwitchCase from "./kit/SwitchCase.vue";
import AboutPage from "./pages/AboutPage.vue";
import FilePage from "./pages/FilePage.vue";
import AttachmentsPage from "./pages/AttachmentsPage.vue";
import FilesPage from "./pages/FilesPage.vue";
import Home from "./pages/Home.vue";
import Index from "./pages/Index.vue";
import IntegrationsPage from "./pages/IntegrationsPage.vue";
import PluginsPage from "./pages/PluginsPage.vue";
import ResourcesPage from "./pages/ResourcesPage.vue";
import SearchPage from "./pages/SearchPage.vue";
import SecretsPage from "./pages/SecretsPage.vue";
import TeamPage from "./pages/TeamPage.vue";
import WorkerHome from "./pages/WorkerHome.vue";
import SettingsPage from "./pages/SettingsPage.vue";
import SkillsPage from "./pages/SkillsPage.vue";
import AgentProfilesPage from "./pages/AgentProfilesPage.vue";
import RequestsPage from "./pages/RequestsPage.vue";
import HubPage from "./pages/HubPage.vue";
import {computed} from "vue";
import {peek, route} from "./route.js";
import {store} from "./state/store.js";
import {rows} from "./sync/rows.js";

defineProps({page: {type: String, required: true}});
const hosted = computed(() => Boolean(store.people && store.people.hosted));
const open = (row) => peek(row.table, row.id);
</script>

<template>
    <SwitchCase :value="page">
        <template #home>
            <template v-if="hosted">
                <HubPage :environments="rows('environments')" :docs="rows('docs')" :plans="rows('plans')" :tasks="rows('tasks')" :messages="rows('messages')" @open="open" />
            </template>
            <template v-else><Home /></template>
        </template>
        <template #settings><SettingsPage /></template>
        <template #search><SearchPage /></template>
        <template #attachments><AttachmentsPage /></template>
        <template #files><FilesPage /></template>
        <template #skills><SkillsPage /></template>
        <template #profiles><AgentProfilesPage /></template>
        <template #about><AboutPage /></template>
        <template #plugins><PluginsPage /></template>
        <template #secrets><SecretsPage /></template>
        <template #team><TeamPage /></template>
        <template #requests><RequestsPage /></template>
        <template #worker><WorkerHome /></template>
        <template #mcp><IntegrationsPage /></template>
        <template #resources><ResourcesPage /></template>
        <template #file><FilePage /></template>
        <template #default><Index :table="route.page" /></template>
    </SwitchCase>
</template>
