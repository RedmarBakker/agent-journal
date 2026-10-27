import {onMounted, onUnmounted} from "vue";

/**
 * A tab brought back to the front reads the latest once (composables/poll.js); when messages came while it was away, `caughtUp(count)`
 * says so once, with the count now held, and the chat takes the reader to the foot at once, never gliding, wherever they left it.
 */
export function useTabReturn(count) {
    let hiddenAt = -1;
    let returning = false;
    const changed = () => {
        if (document.hidden) hiddenAt = count();
        else returning = hiddenAt >= 0;
    };
    onMounted(() => document.addEventListener("visibilitychange", changed));
    onUnmounted(() => document.removeEventListener("visibilitychange", changed));
    return {
        caughtUp(now) {
            if (!returning || now <= hiddenAt) return false;
            returning = false;
            hiddenAt = -1;
            return true;
        },
    };
}
