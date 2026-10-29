import {computed} from "vue";
import {store} from "../state/store.js";

// whether the Plan agents setting is on: every part of the agentic organization shows only while it is
export const planAgentsOn = (settings) => Boolean(settings?.plans?.plan_agents);

// the one place the new screens read the setting from the loaded settings
export const planAgents = computed(() => planAgentsOn(store.settings));
