// @vitest-environment node
import {afterEach, beforeEach, expect, test, vi} from "vitest";

const {SETTLE_AFTER_MS, useFollowing} = await import("../src/composables/following.js");
const {POINTER_GONE_MS, usePointerPresence} = await import("../src/composables/pointerPresence.js");

const pane = (at = 0, height = 1000, visible = 400) => ({scrollTop: at, scrollHeight: height, clientHeight: visible});

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

test("a reader who scrolled up with the pointer over the chat is never scrolled down, not by arrivals nor by resting near the foot", () => {
    const box = pane(560);
    const presence = usePointerPresence();
    const {away, arrived, scrolled} = useFollowing(box, 24, presence.isGone);
    presence.entered();
    scrolled();
    arrived(3);
    vi.advanceTimersByTime(SETTLE_AFTER_MS * 4);
    expect([away.value, box.scrollTop]).toEqual([true, 560]);
});

test("the pointer gone for less than a minute still leaves the chat where it is", () => {
    const box = pane(560);
    const presence = usePointerPresence();
    const {away, scrolled} = useFollowing(box, 24, presence.isGone);
    presence.entered();
    scrolled();
    presence.left();
    vi.advanceTimersByTime(POINTER_GONE_MS - 1000);
    expect([away.value, box.scrollTop, presence.isGone()]).toEqual([true, 560, false]);
});

test("once the pointer has been outside the chat for a minute, a reader still away is taken back to the foot", () => {
    const box = pane(100);
    let following = null;
    const presence = usePointerPresence(() => following.away.value && following.toBottom());
    following = useFollowing(box, 24, presence.isGone);
    presence.entered();
    following.scrolled();
    presence.left();
    vi.advanceTimersByTime(POINTER_GONE_MS);
    expect([presence.isGone(), following.away.value, box.scrollTop]).toEqual([true, false, box.scrollHeight]);
});

test("the pointer coming back before the minute is up cancels the return to the foot", () => {
    const box = pane(100);
    const back = vi.fn();
    const presence = usePointerPresence(back);
    presence.entered();
    presence.left();
    vi.advanceTimersByTime(POINTER_GONE_MS / 2);
    presence.entered();
    vi.advanceTimersByTime(POINTER_GONE_MS);
    expect([back.mock.calls.length, presence.isGone(), box.scrollTop]).toEqual([0, false, 100]);
});
