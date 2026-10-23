import {pollNow, usePoll} from "../../src/web/src/composables/poll.js";

export function terminal(agent) {
    // @righteous PollerKeyNotWrittenDetector
    usePoll("agent.terminal", {params: () => ({agent})});
}

export function made(id) {
    // @sin PollerKeyNotWrittenDetector
    usePoll(`timeline:${id}`, {});
}

export function again(key) {
    // @sin PollerKeyNotWrittenDetector
    pollNow(key);
}
