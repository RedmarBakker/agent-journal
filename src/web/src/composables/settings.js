import {DEFAULT_MODE, DEFAULT_TESTING} from "../domain/modes.js";
import {computed} from "vue";
import {saveSettings} from "../actions/settings.js";
import {store} from "../state/store.js";

export const feedOn = computed(() => !store.settings || store.settings.features.file_feed !== false);
export const barOn = computed(() => !store.settings || store.settings.features.status_bar !== false);
export const workMode = computed(() => (store.settings && store.settings.workers && store.settings.workers.mode) || DEFAULT_MODE);
export const workTesting = computed(() => (store.settings && store.settings.workers && store.settings.workers.testing) || DEFAULT_TESTING);
export const orchestratorApproves = computed(() => Boolean(store.settings && store.settings.workers && store.settings.workers.orchestrator_approves_plans));
export const autoOn = computed(() => !store.settings || !store.settings.tasks || store.settings.tasks.auto !== false);
export const reviewerOn = computed(() => Boolean(store.settings && store.settings.reviewing && store.settings.reviewing.reviewer));
export const sharingOn = computed(() => !store.settings || store.settings.features.sharing !== false);

const viewer = () => (store.settings && store.settings.viewer) || {};

export const viewerSetting = (key, fallback) => viewer()[key] ?? fallback;

export const settingsLoaded = () => Boolean(store.settings);

export async function saveViewerSetting(key, value) {
    await saveSettings({viewer: {[key]: value}});
}

export const agentRunningIn = (name) => store.live.some((live) => live.environment === name);
