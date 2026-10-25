import {expect, test} from "vitest";
import {standingLine} from "../src/domain/requests.js";

test("a request's line says its state, who it is for, who drives it and when it was done", () => {
    expect(standingLine({state: "started", standing: "started", for_whom: "Bob", driver: "Mr. Faraday", done_at: ""})).toBe("started · for Bob · driven by Mr. Faraday");
    expect(standingLine({state: "done", standing: "done", for_whom: "the acme team", driver: "", done_at: "2026-10-25T12:30:00+00:00"})).toBe("done · for the acme team · done 2026-10-25 12:30");
    expect(standingLine({state: "cancelled", standing: "declined", reason: "not this quarter", for_whom: "Bob", driver: "", done_at: "2026-10-25T09:00:00+00:00"})).toBe("declined: not this quarter · for Bob · done 2026-10-25 09:00");
});
