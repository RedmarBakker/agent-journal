import {ref, watch} from "vue";
import {remember, remembered} from "../platform/storage.js";

const KEY = "journal.plan_strip";

// whether the plan bar is one thin strip of its started plans, kept for this viewer
export const stripped = ref(remembered(KEY, false));

watch(stripped, (now) => remember(KEY, now));
