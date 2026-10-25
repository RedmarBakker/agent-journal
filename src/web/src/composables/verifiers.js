import {ref} from "vue";
import {usePoll} from "./poll.js";

// The verifiers the journal sent here, read while the list that shows them is open.
export function useEveryVerifier(open) {
    const rows = ref([]);
    const loaded = ref(false);
    const take = (got) => {
        rows.value = got;
        loaded.value = true;
    };
    return {rows, loaded, refresh: usePoll("verifiers.every", {take, active: () => open.value})};
}
