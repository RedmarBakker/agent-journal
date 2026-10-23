import {reactive} from "vue";
import {usePoll} from "./poll.js";

// how a shared journal's sync with its team stands: its line and its state, both empty in a journal in no team
export function useSyncStatus() {
    const status = reactive({line: "", state: ""});
    usePoll("sync.line", {
        take: (got) => {
            status.line = got.line || "";
            status.state = got.state || "";
        },
    });
    return status;
}
