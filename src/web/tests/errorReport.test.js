import {expect, test, vi} from "vitest";
import {reportErrors} from "../src/platform/errorReport.js";

test("an error thrown in the page is posted once with its stack, however often it repeats", () => {
    const send = vi.fn(() => Promise.resolve());
    reportErrors(window, send);
    const error = new Error("the list is empty");
    window.dispatchEvent(new ErrorEvent("error", {error, message: error.message}));
    window.dispatchEvent(new ErrorEvent("error", {error, message: error.message}));
    expect(send).toHaveBeenCalledTimes(1);
    expect(send.mock.calls[0][0].message).toBe("the list is empty");
    expect(send.mock.calls[0][0].stack).toContain("the list is empty");
});

test("a loop of different errors posts no more than five in the window", () => {
    const send = vi.fn(() => Promise.resolve());
    let clock = 0;
    reportErrors(window, send, () => clock);
    for (let i = 0; i < 50; i++) window.dispatchEvent(new ErrorEvent("error", {error: new Error(`failure ${i}`), message: `failure ${i}`}));
    expect(send).toHaveBeenCalledTimes(5);
    clock = 10000;
    window.dispatchEvent(new ErrorEvent("error", {error: new Error("later"), message: "later"}));
    expect(send).toHaveBeenCalledTimes(6);
});
