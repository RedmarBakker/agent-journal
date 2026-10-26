import {expect, test} from "vitest";
import {dayLine, withDayLines} from "../src/domain/dayLines.js";

const at = (text) => new Date(text).getTime() / 1000;

test("a line names the day before the first turn of each day: today, yesterday or the weekday, with the date", () => {
    const now = at("2026-10-26T22:00:00");
    expect(dayLine(at("2026-10-26T09:00:00"), now)).toBe("Today, 26 October");
    expect(dayLine(at("2026-10-25T23:00:00"), now)).toBe("Yesterday, 25 October");
    expect(dayLine(at("2026-10-22T10:00:00"), now)).toBe("Thursday, 22 October");
    const turns = [{key: "a", time: at("2026-10-25T10:00:00")}, {key: "b", time: at("2026-10-25T11:00:00")}, {key: "c", time: at("2026-10-26T09:00:00")}];
    expect(withDayLines(turns, now).map((t) => (t.kind === "day" ? t.title : t.key))).toEqual(["Yesterday, 25 October", "a", "b", "Today, 26 October", "c"]);
});
