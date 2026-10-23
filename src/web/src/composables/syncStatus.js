import {reactive} from "vue";
import {api} from "../api/client.js";
import {pollKey, usePoll} from "./poll.js";

const EVERY_MS = 5000;

// how a shared journal's sync with its team stands: its line and its state, both empty in a journal in no team
export function useSyncStatus() {
    const status = reactive({line: "", state: ""});
    usePoll(
        pollKey(),
        () => api.syncLine(),
        EVERY_MS,
        (got) => {
            status.line = got.line || "";
            status.state = got.state || "";
        }
    );
    return status;
}
