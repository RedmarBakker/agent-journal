<script setup>
import {computed, onMounted, onUnmounted, ref, watch} from "vue";
import {api} from "../api/client.js";
import EmptyState from "../kit/EmptyState.vue";
import ListBox from "../kit/ListBox.vue";
import Segmented from "../kit/Segmented.vue";
import TextInput from "../kit/TextInput.vue";
import LibraryItemPanel from "../resource/LibraryItemPanel.vue";
import LibraryItemRow from "../resource/LibraryItemRow.vue";
import {href} from "../route.js";

const KINDS = [
    {key: "", label: "Everything"},
    {key: "sequence", label: "Sequences"},
    {key: "template", label: "Templates"},
    {key: "profile", label: "Profiles"},
    {key: "reader", label: "Readers"},
    {key: "skill", label: "Skills"},
    {key: "document", label: "Documents"},
    {key: "file", label: "Files"},
    {key: "plan", label: "Plans"},
];
const POLL_MS = 30000;

const connection = ref(null);
const items = ref(null);
const kind = ref("");
const search = ref("");
const opened = ref(null);
let poll = 0;

const connected = computed(() => Boolean(connection.value?.connected));

async function load() {
    connection.value = await api.library();
    items.value = connected.value ? (await api.libraryItems(kind.value, search.value.trim())).items : [];
}

const isOpened = (item) => opened.value?.item_type === item.item_type && opened.value?.name === item.name;

watch([kind, search], load);
onMounted(() => {
    load();
    poll = setInterval(load, POLL_MS);
});
onUnmounted(() => clearInterval(poll));
</script>

<template>
    <section class="library-page">
        <header class="library-head">
            <h1>Library</h1>
            <p class="library-lead">The sequences, templates, profiles, readers, skills, documents, files and plans your team shares. Import one to use it here; an imported one can be updated when a newer version is published.</p>
        </header>
        <template v-if="connection && !connected">
            <EmptyState title="No library connected">
                Connect this journal to your team's library in <a :href="href.settings('library')">Settings, Library</a>.
            </EmptyState>
        </template>
        <template v-else>
            <div class="library-bar">
                <Segmented :options="KINDS" :value="kind" @pick="kind = $event" />
                <TextInput v-model="search" icon="search" placeholder="Search the library" />
            </div>
            <div class="library-body">
                <template v-if="!items">
                    <EmptyState loading />
                </template>
                <template v-else-if="!items.length">
                    <EmptyState>No items match.</EmptyState>
                </template>
                <template v-else>
                    <ListBox title="Items" :count="items.length">
                        <template v-for="entry in items" :key="`${entry.item.item_type}:${entry.item.name}`">
                            <LibraryItemRow
                                :item="entry.item"
                                :version="entry.version"
                                :imported="entry.imported_version"
                                :on="isOpened(entry.item)"
                                @open="opened = entry.item"
                            />
                        </template>
                    </ListBox>
                </template>
                <template v-if="opened">
                    <aside class="library-panel">
                        <LibraryItemPanel :type="opened.item_type" :name="opened.name" @changed="load" />
                    </aside>
                </template>
            </div>
        </template>
    </section>
</template>

<style scoped>
.library-page {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 24px;
    max-width: 1200px;
}

.library-head h1 {
    margin: 0 0 6px;
    font-size: 20px;
}

.library-lead {
    margin: 0;
    color: var(--text-2);
    max-width: 640px;
}

.library-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
}

.library-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 20px;
    align-items: start;
}

.library-panel {
    padding: 14px;
    border: 1px solid var(--border-3);
    border-radius: 8px;
}

@media (max-width: 760px) {
    .library-body {
        grid-template-columns: minmax(0, 1fr);
    }
}
</style>
