import {readFileSync} from "node:fs";
import {expect, test} from "vitest";
import {defaultHidden, visibleIn} from "../src/domain/chatVisibility.js";
import {store} from "../src/state/store.js";

const marks = JSON.parse(readFileSync("tests/fixtures/markKinds.json", "utf8"));

test("the chat hides what the registry starts hidden, acknowledgements, a sequence's steps, sync conflict notes and verifiers, and shows a sequence starting and finishing", () => {
    store.spec = {...store.spec, marks};
    const shown = visibleIn(defaultHidden());
    expect(defaultHidden().sort()).toEqual(["acknowledgements", "conflicts", "sequence_steps", "verifiers"]);
    expect(shown({type: "card", data: {icon: "warn", shows: "conflicts"}})).toBe(false);
    expect(shown({type: "card", data: {icon: "list", shows: "sequence_steps"}})).toBe(false);
    expect(shown({type: "card", data: {icon: "verifier", shows: "verifiers"}})).toBe(false);
    expect(shown({type: "card", data: {icon: "list", shows: "sequences"}})).toBe(true);
    expect(shown({type: "card", data: {icon: "branch", shows: "commits"}})).toBe(true);
    expect(visibleIn(["sequences", "sequence_steps"])({type: "card", data: {icon: "list", shows: "sequences"}})).toBe(false);
    expect(visibleIn([])({type: "card", data: {icon: "list", shows: "sequence_steps"}})).toBe(true);
    expect(visibleIn(["agents"])({type: "card", data: {shows: "workers"}}), "hiding the agents talking hides the workers it covers").toBe(
        false
    );
    expect(visibleIn(["filed"])({kind: "receipt", data: {}}), "a receipt is a mark of what was filed").toBe(false);
    expect(visibleIn(["acknowledgements"])({kind: "message", acknowledgement: true, data: {}})).toBe(false);
});
