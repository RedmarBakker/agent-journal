import {describe, expect, test} from "vitest";
import {adapted, fresh, leaves, valid, VIEWS} from "../src/domain/panes.js";

describe("a stored layout after a release", () => {
    const tabsOf = (layout) => leaves(layout.tree).flatMap((id) => layout.panes[id].tabs);

    test("keeps the user's arrangement when the release adds a view, the new one joining the first pane", () => {
        const stored = fresh();
        const views = [...VIEWS, "a view this release adds"];
        const kept = adapted(stored, views, true);
        expect(valid(kept, views)).toBe(true);
        const first = kept.panes[leaves(kept.tree)[0]].tabs;
        expect(first.includes("a view this release adds")).toBe(true);
        expect(tabsOf(kept).filter((view) => tabsOf(stored).includes(view))).toEqual(tabsOf(stored));
    });

    test("drops a view the release no longer has, the rest staying where the user put them", () => {
        const stored = fresh();
        const gone = tabsOf(stored)[0];
        const views = VIEWS.filter((view) => view !== gone);
        const kept = adapted(stored, views, false);
        expect(valid(kept, views)).toBe(true);
        expect(tabsOf(kept)).toEqual(tabsOf(stored).filter((view) => view !== gone));
    });

    test("leaves a layout that is not one untouched, so the fresh layout takes its place", () => {
        expect(adapted(null, VIEWS, true)).toBe(null);
        expect(adapted({tree: null}, VIEWS, true)).toEqual({tree: null});
    });
});
