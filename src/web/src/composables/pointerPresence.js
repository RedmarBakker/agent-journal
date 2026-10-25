import {getCurrentScope, onScopeDispose} from "vue";

export const POINTER_GONE_MS = 60000;

/**
 * Whether the pointer is over a pane, or left it so long ago that the pane may move itself again.
 *
 * A reader with the pointer over the chat is reading it, so nothing scrolls it for them; once the pointer has been
 * outside for POINTER_GONE_MS, the pane may scroll itself, and the callback given is called at that moment.
 */
export function usePointerPresence(gone = () => {}, goneMs = POINTER_GONE_MS) {
    let inside = false;
    let leftAt = 0;
    let goneTimer = 0;

    function entered() {
        clearTimeout(goneTimer);
        inside = true;
    }

    function left() {
        inside = false;
        leftAt = Date.now();
        clearTimeout(goneTimer);
        goneTimer = setTimeout(gone, goneMs);
    }

    const isGone = () => !inside && Date.now() - leftAt >= goneMs;

    if (getCurrentScope()) onScopeDispose(() => clearTimeout(goneTimer));

    return {entered, left, isGone};
}
