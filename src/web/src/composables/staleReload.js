import {onBeforeUnmount, ref, watch} from "vue";
import {fieldBusy, reloadWhenFree} from "../platform/busyField.js";

// the seconds the page must be left alone before a newer viewer build reloads it
export const RELOAD_AFTER = 60;
const TOUCHES = ["pointerdown", "pointermove", "keydown", "wheel", "touchstart"];

// The reload a newer viewer build waits for, while `stale` holds: the page reloads once nobody has touched it for RELOAD_AFTER seconds, every
// touch, scroll or key starting the wait again, and at once when it goes out of sight; never while a field has words in it or `drafting`
// says a message is being written. `remaining` is the seconds left and `waiting` whether a draft holds the reload.
export function useStaleReload(stale, drafting, win = window) {
    const remaining = ref(0);
    const waiting = ref(false);
    const touched = () => stale.value && (remaining.value = RELOAD_AFTER);
    const reload = () => reloadWhenFree(win);
    const hidden = () => stale.value && win.document.visibilityState === "hidden" && reload();
    const tick = win.setInterval(() => {
        waiting.value = drafting() || fieldBusy(win.document);
        if (!remaining.value || waiting.value) return;
        remaining.value = Math.max(0, remaining.value - 1);
        if (!remaining.value) reload();
    }, 1000);
    TOUCHES.forEach((kind) => win.addEventListener(kind, touched, {passive: true}));
    win.document.addEventListener("visibilitychange", hidden);
    watch(stale, (is) => (remaining.value = is ? RELOAD_AFTER : 0), {immediate: true});
    onBeforeUnmount(() => {
        win.clearInterval(tick);
        TOUCHES.forEach((kind) => win.removeEventListener(kind, touched));
        win.document.removeEventListener("visibilitychange", hidden);
    });
    return {remaining, waiting, reload};
}
