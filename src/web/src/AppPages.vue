<script setup>
import SwitchCase from "./kit/SwitchCase.vue";
import AboutPage from "./pages/AboutPage.vue";
import FilePage from "./pages/FilePage.vue";
import AttachmentsPage from "./pages/AttachmentsPage.vue";
import FilesPage from "./pages/FilesPage.vue";
import GitPage from "./pages/GitPage.vue";
import Home from "./pages/Home.vue";
import Index from "./pages/Index.vue";
import IntegrationsPage from "./pages/IntegrationsPage.vue";
import OrganizationPage from "./pages/OrganizationPage.vue";
import RolePage from "./organization/RolePage.vue";
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
import HomePlanBoard from "./pages/HomePlanBoard.vue";
import {computed} from "vue";
import {peek, route} from "./route.js";
import {store} from "./state/store.js";
import {rows} from "./sync/rows.js";
import {planAgents} from "./domain/planAgents.js";

defineProps({page: {type: String, required: true}});
const hosted = computed(() => Boolean(store.people && store.people.hosted));
const open = (row) => peek(row.table, row.id);
</script>

<template>
    <SwitchCase :value="page">
        <template #home>
            <template v-if="planAgents">
                <div class="home-plan-board-screen">
                    <div class="home-plan-board-screen-board"><HomePlanBoard /></div>
                    <div class="home-plan-board-screen-chat"><Home /></div>
                </div>
            </template>
            <template v-else-if="hosted">
                <HubPage :environments="rows('environments')" :docs="rows('docs')" :plans="rows('plans')" :tasks="rows('tasks')" :messages="rows('messages')" @open="open" />
            </template>
            <template v-else><Home /></template>
        </template>
        <template #settings><SettingsPage /></template>
        <template #search><SearchPage /></template>
        <template #attachments><AttachmentsPage /></template>
        <template #files><FilesPage /></template>
        <template #git><GitPage /></template>
        <template #skills><SkillsPage /></template>
        <template #profiles><AgentProfilesPage /></template>
        <template #about><AboutPage /></template>
        <template #plugins><PluginsPage /></template>
        <template #secrets><SecretsPage /></template>
        <template #team><TeamPage /></template>
        <template #requests><RequestsPage /></template>
        <template #worker><WorkerHome /></template>
        <template #mcp><IntegrationsPage /></template>
        <template #organization><OrganizationPage /></template>
        <template #role><RolePage /></template>
        <template #resources><ResourcesPage /></template>
        <template #file><FilePage /></template>
        <template #default><Index :table="route.page" /></template>
    </SwitchCase>
</template>

<style scoped>
.home-plan-board-screen {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.home-plan-board-screen-board {
    flex: 0 1 45%;
    min-height: 180px;
    overflow: auto;
    border-bottom: 1px solid var(--line);
}

.home-plan-board-screen-chat {
    flex: 1 1 0;
    min-height: 0;
    overflow: hidden;
}
</style>
