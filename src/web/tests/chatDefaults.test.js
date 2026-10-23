import {expect, test} from "vitest";
import {DEFAULT_HIDDEN, visibleIn} from "../src/domain/chatVisibility.js";
import {store} from "../src/state/store.js";

test("the chat hides acknowledgements, a sequence's steps and sync conflict notes, and shows a sequence starting and finishing", () => {
    store.spec = {...store.spec, chat_kinds: {turns: {}}};
    const shown = visibleIn(DEFAULT_HIDDEN);
    expect(DEFAULT_HIDDEN).toEqual(["acknowledgements", "sequence_steps", "conflicts"]);
    expect(shown({type: "card", data: {icon: "warn", shows: "conflicts"}})).toBe(false);
    expect(shown({type: "card", data: {icon: "list", shows: "sequence_steps"}})).toBe(false);
    expect(shown({type: "card", data: {icon: "list", shows: "sequences"}})).toBe(true);
    expect(shown({type: "card", data: {icon: "list", shows: "sequences"}})).toBe(true);
    expect(shown({type: "card", data: {icon: "branch", shows: "commits"}})).toBe(true);
    expect(visibleIn(["sequences", "sequence_steps"])({type: "card", data: {icon: "list", shows: "sequences"}})).toBe(false);
    expect(visibleIn([])({type: "card", data: {icon: "list", shows: "sequence_steps"}})).toBe(true);
});
