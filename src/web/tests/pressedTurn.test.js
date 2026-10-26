import {expect, it, vi} from "vitest";
import {usePressedTurn} from "../src/composables/pressedTurn.js";

const pressOn = (element) => ({target: {closest: () => element}});

it("a bubble the reader pressed holds the pane where it is while it opens, and after a press outside any bubble the chat follows as before", () => {
    vi.useFakeTimers();
    const pressed = usePressedTurn();
    pressed.press(pressOn({isConnected: true}));
    expect(pressed.isOpening()).toBe(true);
    vi.advanceTimersByTime(1600);
    expect(pressed.isOpening()).toBe(false);
    pressed.press(pressOn(null));
    expect(pressed.isOpening()).toBe(false);
    vi.useRealTimers();
});
