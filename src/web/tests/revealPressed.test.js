import {describe, expect, it, vi} from "vitest";
import {revealOffset, useRevealPressed} from "../src/composables/revealPressed.js";

describe("a bubble that opens near the foot", () => {
    const pane = {top: 0, bottom: 600};

    it("scrolls the pane up until the bubble is seen whole above the docks and the composer", () => {
        expect(revealOffset({top: 400, bottom: 700}, pane)).toBe(108);
    });

    it("brings a bubble taller than the pane only as far as its top", () => {
        expect(revealOffset({top: 300, bottom: 1200}, pane)).toBe(292);
    });

    it("leaves a bubble already in view where it is", () => {
        expect(revealOffset({top: 100, bottom: 500}, pane)).toBe(0);
    });
});

describe("a chat mark pressed at the foot of the chat", () => {
    const turn = (bottom) => ({isConnected: true, querySelector: () => null, getBoundingClientRect: () => ({top: 400, bottom})});
    const pressOn = (element) => ({target: {closest: () => element}});

    it("holds the follow to the foot while it opens, and scrolls its bottom into view rather than snapping to the foot", () => {
        vi.useFakeTimers();
        const scrolled = [];
        const pane = {scrollTop: 1000, getBoundingClientRect: () => ({top: 0, bottom: 600}), scrollTo: (to) => scrolled.push(to)};
        const pressed = useRevealPressed({value: pane});
        const mark = turn(700);
        pressed.press(pressOn(mark));
        expect(pressed.isRevealing()).toBe(true);
        pressed.reveal();
        expect(scrolled).toEqual([{top: 1108, behavior: "smooth"}]);
        vi.advanceTimersByTime(1600);
        expect(pressed.isRevealing()).toBe(false);
        vi.useRealTimers();
    });

    it("follows the foot as before after a press outside any bubble", () => {
        const pressed = useRevealPressed({value: null});
        pressed.press(pressOn(null));
        expect(pressed.isRevealing()).toBe(false);
    });
});
