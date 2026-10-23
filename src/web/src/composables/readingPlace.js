import {unref} from "vue";

// how many of the rows in view are marked, so one removed or folded into another still leaves a row to hold the view by
const MARKS = 4;

// Keeps the rows a reader scrolled up to in place when rows above or around them change height, appear, fold or go: the first marked row
// still on the page is put back where it was in the view, and the marks are taken again from there; Safari has no scroll anchoring of
// its own.
export function useReadingPlace(scroller) {
    let places = [];

    function inView(box) {
        const top = box.getBoundingClientRect().top;
        return [...box.querySelectorAll("[data-ref]")]
            .map((el) => ({el, rect: el.getBoundingClientRect()}))
            .filter(({rect}) => rect.bottom > top)
            .slice(0, MARKS)
            .map(({el, rect}) => ({ref: el.dataset.ref, below: rect.top - top}));
    }

    function mark() {
        const box = unref(scroller);
        places = box ? inView(box) : [];
    }

    function forget() {
        places = [];
    }

    function hold() {
        const box = unref(scroller);
        if (!box || !places.length) return;
        const rows = new Map([...box.querySelectorAll("[data-ref]")].map((el) => [el.dataset.ref, el]));
        const place = places.find((each) => rows.has(each.ref));
        if (!place) return;
        const drift = rows.get(place.ref).getBoundingClientRect().top - box.getBoundingClientRect().top - place.below;
        if (Math.abs(drift) >= 1) box.scrollTop += drift;
        mark();
    }

    return {mark, forget, hold};
}
