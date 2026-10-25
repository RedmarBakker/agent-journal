import {expect, test} from "vitest";
import {attach} from "../src/chat/attachments.js";

test("a zip of 44.6 MB is attached, whatever its type", () => {
    const zip = new File([new Uint8Array(46_800_000)], "agent-journal-avatar-refined.zip", {type: "application/zip"});
    const {added, oversized} = attach([], [zip]);
    expect(added).toEqual([zip]);
    expect(oversized).toEqual([]);
});
