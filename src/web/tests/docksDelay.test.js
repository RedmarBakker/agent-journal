import {expect, test} from "vitest";
import {isDocked} from "../src/domain/docks.js";

test("a chat mark that docks itself comes after its run has gone on five seconds and leaves five seconds after it ends", () => {
    const mark = (data) => ({data: {docked: true, auto_docked: true, ...data}});
    expect(isDocked(mark({dock_at: 105}), 102)).toBe(false);
    expect(isDocked(mark({dock_at: 105}), 106)).toBe(true);
    expect(isDocked(mark({dock_at: 105, undock_at: 115}), 112)).toBe(true);
    expect(isDocked(mark({dock_at: 105, undock_at: 105}), 104)).toBe(false);
    expect(isDocked(mark({dock_at: 105, undock_at: 105}), 106)).toBe(false);
});
