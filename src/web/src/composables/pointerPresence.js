import {getCurrentScope, onScopeDispose} from "vue";
import {useWindowEvent} from "./windowEvent.js";

export const POINTER_GONE_MS = 60000;
// what says the pointer is over a pane: coming onto it, moving, pressing or wheeling in it, so a pointer that was over it before the
// page drew counts as soon as it stirs
const PRESENT = ["pointerenter", "pointermove", "pointerdown", "wheel"];

/**
 * Whether the pointer is over a pane, or left it so long ago that the pane may move itself again.
 *
 * A reader with the pointer over the chat is reading it, so nothing scrolls it for them; once the pointer has been
 * outside for POINTER_GONE_MS, the pane may scroll itself, and the callback given is called at that moment. Given the pane's element,
 * it listens on it itself.
 */
export function usePointerPresence(gone = () => {}, goneMs = POINTER_GONE_MS, pane = null) {
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
    if (pane) {
        PRESENT.forEach((name) => useWindowEvent(name, entered, {passive: true}, () => pane.value));
        useWindowEvent("pointerleave", left, undefined, () => pane.value);
    }

    return {entered, left, isGone};
}
