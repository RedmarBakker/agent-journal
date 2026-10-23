import {nextTick, onUnmounted, ref, unref, watch} from "vue";

// how many frames the place is held while rows drawn above it settle, and how many still frames end the hold early
const HOLD_FRAMES = 60;
const STILL_FRAMES = 6;
const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));

// Loads rows above what the reader sees and keeps the reader's place: the rows above may be drawn over several frames, so the
// place is held each frame until the height has been still for a few, and let go at once when the reader scrolls themselves.
export async function keepingPlace(scroller, load) {
    const box = unref(scroller);
    const fromBottom = box ? box.scrollHeight - box.scrollTop : 0;
    const grew = await load();
    await nextTick();
    if (grew === false) return grew;
    let held = null;
    let still = 0;
    let height = -1;
    for (let frame = 0; frame < HOLD_FRAMES && still < STILL_FRAMES; frame++) {
        const now = unref(scroller);
        if (!now || (held !== null && now.scrollTop !== held)) break;
        now.scrollTop = now.scrollHeight - fromBottom;
        held = now.scrollTop;
        still = now.scrollHeight === height ? still + 1 : 0;
        height = now.scrollHeight;
        await nextFrame();
    }
    return grew;
}

export function useSighted(mark, onSight, {root = null, margin = "0px"} = {}) {
    let watcher = null;
    const stop = watch(
        () => [unref(mark), unref(root)],
        ([el, box]) => {
            if (watcher) watcher.disconnect();
            watcher = null;
            if (!el || (root && !box)) return;
            watcher = new IntersectionObserver((seen) => seen.some((e) => e.isIntersecting) && onSight(), {
                root: box || null,
                rootMargin: margin,
            });
            watcher.observe(el);
        },
        {immediate: true, flush: "post"}
    );
    onUnmounted(() => {
        stop();
        if (watcher) watcher.disconnect();
    });
}

// How near the top of the scroller the mark must stand for the reader to be at the top.
const NEAR_PX = 200;

export function useScrollback(scroller, mark, load, {ready = () => true, margin = "200px 0px 0px 0px"} = {}) {
    const loading = ref(false);
    let spent = false;
    // whether the mark still stands near the top of the scroller, so the reader is still at the top
    function inSight() {
        const el = unref(mark);
        const box = unref(scroller);
        return Boolean(el && box) && Math.abs(el.getBoundingClientRect().top - box.getBoundingClientRect().top) < NEAR_PX;
    }
    // after a page the next waits until the reader has left the top and come back to it
    function leftTheTop() {
        if (spent && !inSight()) spent = false;
    }
    async function older() {
        if (loading.value || spent || !ready()) return false;
        loading.value = true;
        try {
            return await keepingPlace(scroller, load);
        } finally {
            loading.value = false;
            spent = true;
        }
    }
    useSighted(mark, older, {root: scroller, margin});
    watch(
        () => unref(scroller),
        (box, was) => {
            was?.removeEventListener("scroll", leftTheTop);
            box?.addEventListener("scroll", leftTheTop, {passive: true});
        },
        {immediate: true, flush: "post"}
    );
    onUnmounted(() => unref(scroller)?.removeEventListener("scroll", leftTheTop));
    return {loading, older};
}
